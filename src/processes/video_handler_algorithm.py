
import math, random
import numpy as np

# Метод 1
def handleFramesByCenter(
    frames,
    offset, max_frames
):
    center_idx = frames // 2
    indices    = [ center_idx ]

    left  = center_idx - offset
    right = center_idx + offset

    while len( indices ) < max_frames * 2:
        left  -= offset
        right += offset

        added = False
        
        if 0 <= left < frames:
            indices.append( left )
            added = True

        if 0 <= right < frames:
            indices.append( right )
            added = True

        if not added:
            break

    return indices[ :max_frames ]

# Метод 2
def handleFramesByInterval(
    frames, max_frames
):
    indices = []
    step    = frames // min( frames, max_frames )
    index   = 0

    while index < max_frames:
        currentFrame = index * step
        indices.append( currentFrame )

        index += 1

    return indices[ :max_frames ]


def handleFramesByTrimodalGauss(
    total_frames, num_to_select, 
    center_start = 0, center_mid = None, center_end = None,
    sigma_start = None, sigma_mid = None, sigma_end = None,
    weight_start = 0.22, weight_mid = 0.64, weight_end = None,
    seed = None
):
    if seed is not None:
        np.random.seed( seed )
    
    if center_mid is None:
        center_mid = total_frames // 2
    if center_end is None:
        center_end = total_frames - 1
    
    if sigma_start is None:
        sigma_start = total_frames / 20
    if sigma_mid is None:
        sigma_mid = total_frames / 6
    if sigma_end is None:
        sigma_end = total_frames / 20
    
    n_start = int( round( num_to_select * weight_start ) )
    n_mid   = int( round( num_to_select * weight_mid ) )
    
    if weight_end is not None:
        n_end = int( round( num_to_select * weight_end ) )

        diff = num_to_select - ( n_start + n_mid + n_end )
        n_mid += diff 
    else:
        n_end = num_to_select - n_start - n_mid

        if n_end < 0:
            n_mid += n_end  
            n_end = 0

    sample_start = np.random.normal( loc = center_start, scale = sigma_start, size = n_start )
    sample_mid   = np.random.normal( loc = center_mid,   scale = sigma_mid,   size = n_mid )
    sample_end   = np.random.normal( loc = center_end,   scale = sigma_end,   size = n_end )
    
    combined = np.concatenate( 
        [
            sample_start,
            sample_mid,
            sample_end
        ]
    )
    
    indices = np.round( combined ).astype( int )
    indices = np.clip( indices, 0, total_frames - 1 )

    np.random.shuffle( indices )
    
    uniqueIndices = np.unique( indices )

    return uniqueIndices

# Метод 3
def handleFramesByPFrame(
    decoded_stream,
    offset, max_frames
):
    indices = []
    index   = 0

    for frame in decoded_stream:
        if frame.pict_type == 1:
            rndOffset = math.floor( offset * random.random() )
            indices.append( index + random.randint( rndOffset * -1, rndOffset ) )
        index += 1

    return indices[ :max_frames ]