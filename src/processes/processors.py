import torch
from decord import VideoReader, cpu
from transformers import (
    AutoModelForImageClassification,
    AutoImageProcessor,
    ViTImageProcessor,
)

from processes.video_utils import is_video_frame_blank, save_video_frame_grid
from processes.video_handler_algorithm import (
    handleFramesByCenter,
    handleFramesByInterval,
    handleFramesByTrimodalGauss
)
from PIL import Image

device = 'cuda' if torch.cuda.is_available() else 'cpu'

NSFW_MODEL_ID  = 'Falconsai/nsfw_image_detection'
nsfw_model     = AutoModelForImageClassification.from_pretrained( NSFW_MODEL_ID ).to( device ).eval()
nsfw_processor = ViTImageProcessor.from_pretrained( NSFW_MODEL_ID )
nsfw_id2label  = nsfw_model.config.id2label
nsfw_label2id  = { v.lower(): k for k, v in nsfw_id2label.items() }
nsfw_idx       = nsfw_label2id.get( 'nsfw', 0 )

FURRY_MODEL_ID  = 'SaintGermain/is-this-furry'
furry_model     = AutoModelForImageClassification.from_pretrained( FURRY_MODEL_ID ).to( device ).eval()
furry_processor = AutoImageProcessor.from_pretrained( FURRY_MODEL_ID )
furry_id2label  = furry_model.config.id2label
furry_label2id  = { v.lower(): k for k, v in furry_id2label.items() }
furry_idx       = furry_label2id.get( 'furry', 0 )

def classify_image(
    path,
    nsfw_resolve_range = 0.5, furry_resolve_range = 0.5
):
    image = Image.open( path ).convert( 'RGB' )

    nsfw_prob  = predict_nsfw( image )
    furry_prob = predict_furry( image )

    nsfw  = nsfw_prob  > nsfw_resolve_range
    furry = furry_prob > furry_resolve_range
    
    return [ nsfw, furry, nsfw_prob, furry_prob ]

def classify_video(
    path,
    video_keyframes_offset = 5, video_keyframes_count = 50,
    nsfw_resolve_range = 0.5, furry_resolve_range = 0.5,
    nsfw_aggregation = 'max', furry_aggregation = 'mean',
    video_long_playtime_frames_count = 250, video_use_gauss_handler_algoritm_for_long_playtime = True,
    is_debug = False
):
    keyframes = extract_keyframes_precise(
        path,
        video_keyframes_offset,           video_keyframes_count,
        video_long_playtime_frames_count, video_use_gauss_handler_algoritm_for_long_playtime,
        is_debug
    )
    
    if not keyframes:
        return []

    nsfw_probs  = []
    furry_probs = []

    for id, img in keyframes.items():
        nsfw_probs.append( predict_nsfw( img ) )
        furry_probs.append( predict_furry( img ) )

    final_nsfw  = ( max( nsfw_probs )  if nsfw_aggregation  == 'max' else sum( nsfw_probs )  / len( nsfw_probs )  )
    final_furry = ( max( furry_probs ) if furry_aggregation == 'max' else sum( furry_probs ) / len( furry_probs ) )

    nsfw  = final_nsfw  > nsfw_resolve_range
    furry = final_furry > furry_resolve_range
    
    return [ nsfw, furry, final_nsfw, final_furry ]

# ---

def extract_keyframes_precise(
    path,
    keyframes_offset = 5, max_keyframes = 50,
    video_long_playtime_frames_count = 250, video_use_gauss_handler_algoritm_for_long_playtime = True,
    skip_blank = True, blank_thresh = 15.0,
    is_debug = False
):
    try:
        vr = VideoReader( path, ctx = cpu( 0 ) )
    except Exception as e:
        return {}

    nb_frames = len( vr )

    if nb_frames == 0:
        return {}

    indices = []

    if nb_frames > video_long_playtime_frames_count:
        if video_use_gauss_handler_algoritm_for_long_playtime:
            indices = handleFramesByTrimodalGauss( nb_frames, max_keyframes )
        else:
            indices = handleFramesByCenter( nb_frames, keyframes_offset, max_keyframes )
    else:
        indices = handleFramesByInterval( nb_frames, max_keyframes )

    result        = {}
    blank_skipped = 0

    for idx in indices:
        if idx < 0 or idx >= nb_frames:
            continue

        frame_arr = vr[ idx ].asnumpy()
        img       = Image.fromarray( frame_arr )

        if skip_blank and is_video_frame_blank( img, blank_thresh ):
            blank_skipped += 1

            for offset_idx in range( 1, 5 ):
                new_idx = idx + offset_idx

                if new_idx < nb_frames:
                    frame_arr2 = vr[ new_idx ].asnumpy()
                    img2 = Image.fromarray( frame_arr2 )
                
                    if not is_video_frame_blank( img2, blank_thresh ):
                        result[ new_idx ] = img2
                        break
            continue

        result[ idx ] = img

    if is_debug:
        save_video_frame_grid( result, path, 'debug' )

    return result

def predict_nsfw(
    image
):
    inputs = nsfw_processor( images = image, return_tensors = 'pt' ).to( device )
    
    with torch.no_grad():
        logits = nsfw_model( **inputs ).logits
    
    probs = torch.softmax( logits, dim = -1 ).squeeze().cpu().numpy()
    
    return float( probs[ nsfw_idx ] )

def predict_furry(
    image
):
    inputs = furry_processor( images = image, return_tensors = 'pt' ).to( device )

    with torch.no_grad():
        logits = furry_model( **inputs ).logits
    
    probs = torch.softmax( logits, dim = -1 ).squeeze().cpu().numpy()
    
    return float( probs[ furry_idx ] )