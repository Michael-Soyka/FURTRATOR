import os
import numpy as np

from PIL     import Image, ImageFont, ImageDraw
from pathlib import Path

DEBUG_VIDEO_THUMB_HEIGHT   = 200
DEBUG_VIDEO_MAX_COLS       = 10
DEBUG_VIDEO_FORMAT         = 'JPEG'
DEBUG_VIDEO_QUALITY        = 95
DEBUG_VIDEO_MAX_GRID_WIDTH = 1600

def is_video_frame_blank(
    img: Image.Image, std_threshold: float = 10.0
) -> bool:
    arr = np.array( img.convert( 'L' ) )

    return arr.std() < std_threshold

def save_video_frame_grid(
    frames_dict    : dict,
    video_path     : str,
    output_dir     : str = None,
    thumb_height   : int = DEBUG_VIDEO_THUMB_HEIGHT,
    max_cols       : int = DEBUG_VIDEO_MAX_COLS,
    img_format     : str = DEBUG_VIDEO_FORMAT,
    quality        : int = DEBUG_VIDEO_QUALITY,
    max_grid_width : int = DEBUG_VIDEO_MAX_GRID_WIDTH
):
    if not frames_dict:
        return

    items = sorted( frames_dict.items(), key=lambda x: x[ 0 ] )
    n     = len( items )
    cols  = min( n, max_cols )
    rows  = ( n + cols - 1 ) // cols

    label_height = 30
    bg_color     = ( 30, 30, 30 )

    try:
        font = ImageFont.truetype( 'arial.ttf', 14 )
    except:
        font = ImageFont.load_default()

    cells = []

    for frame_id, img in items:
        w, h  = img.size
        ratio = w / h
        tw    = int( thumb_height * ratio )

        if tw > 1200:
            tw                  = 1200
            thumb_height_actual = int( tw / ratio )
        else:
            thumb_height_actual = thumb_height

        thumb = img.resize( ( tw, thumb_height_actual ), Image.Resampling.LANCZOS )
        
        cell_w = tw
        cell_h = thumb_height_actual + label_height
        cell   = Image.new( 'RGB', ( cell_w, cell_h ), bg_color )
        cell.paste( thumb, ( 0, 0 ) )

        draw = ImageDraw.Draw( cell )
        text = f'Idx {frame_id}'
        bbox = draw.textbbox( ( 0, 0 ), text, font = font )
        tx   = ( cell_w - ( bbox[ 2 ] - bbox[ 0 ] ) ) // 2
        ty   = thumb_height_actual + ( label_height - ( bbox[ 3 ] - bbox[ 1 ] ) ) // 2
        
        draw.text( ( tx, ty ), text, fill = ( 255, 255, 255 ), font = font )
        cells.append( cell )

    # Собираем сетку
    row_heights = []
    row_widths  = []

    for r in range( rows ):
        start     = r * cols
        end       = min( start + cols, n )
        row_cells = cells[ start:end ]
        row_heights.append( max( c.height for c in row_cells ) )
        row_widths.append( sum( c.width for c in row_cells ) )

    grid_w   = max( row_widths )
    grid_h   = sum( row_heights )
    grid_img = Image.new( 'RGB', ( grid_w, grid_h ), bg_color )

    y = 0

    for r in range( rows ):
        start = r * cols
        end   = min( start + cols, n )
        x     = 0

        for i in range( start, end ):
            grid_img.paste( cells[ i ], ( x, y ) )
            x += cells[ i ].width
        
        y += row_heights[ r ]

    if grid_w > max_grid_width:
        ratio    = max_grid_width / grid_w
        new_h    = int( grid_h * ratio )
        grid_img = grid_img.resize( ( max_grid_width, new_h ), Image.Resampling.LANCZOS )

    video_name = Path( video_path ).stem
    ext        = img_format.lower()
    
    if output_dir:
        os.makedirs( output_dir, exist_ok = True )
        save_path = os.path.join( output_dir, f'{video_name}_keyframes.{ext}' )
    else:
        base_dir  = os.path.dirname( video_path )
        save_path = os.path.join( base_dir, f'{video_name}_keyframes.{ext}' )

    if img_format.upper() == 'JPEG':
        grid_img = grid_img.convert( 'RGB' )
        grid_img.save( save_path, 'JPEG', quality = quality )
    else:
        grid_img.save( save_path, 'PNG' )