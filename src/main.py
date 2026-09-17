import os
import shutil

from pathlib      import Path
from rich.console import Console

from ui.logger         import FancyLogger, _format_size
from processes.processors import classify_image, classify_video

# ---------- настройки ----------
# Пути
SOURCE_DIR = './../source'
TARGET_DIR = './../export'

USE_UI = True

# Перемещать ли файлы, или просто сканировать
MOVE_FILES = False

# Факторы, выше - строже
NSFW_THRESH  = 0.01
FURRY_THRESH = 0.38

# По общему 'mean' или по максимальному 'max'
NSFW_AGGREGATION  = 'max'
FURRY_AGGREGATION = 'mean'

# Настройки для обработки видео
VIDEO_LONG_PLAYTIME_FRAMES_COUNT                   = 250
VIDEO_USE_GAUSS_HANDLER_ALGORITM_FOR_LONG_PLAYTIME = True
VIDEO_KEYFRAMES_COUNT                              = 40
VIDEO_KEYFRAMES_OFFSET                             = 5

# Бдует сохранять вырезки из видео
DEBUG_VIDEO = False

# Поддерживаемые форматы
EXTENSIONS = {
    'video'  : {
        '.mp4',
        '.avi',
        '.mov',
        '.mkv',
        '.webm',
    },
    'image' : {
        '.jpg',
        '.jpeg',
        '.png',
        '.gif',
        '.webp',
        '.bmp',
    }
}

# Сопоставление ключ, название директории
CATEGORY = {
    'SFW'        : { 'name' : 'SFW',        'color' : 'green' },
    'NSFW'       : { 'name' : 'NSFW',       'color' : 'green' },
    'SFW_FURRY'  : { 'name' : 'SFW_FURRY',  'color' : 'red' },
    'NSFW_FURRY' : { 'name' : 'NSFW_FURRY', 'color' : 'red' },
    'OTHER'      : { 'name' : 'OTHER',      'color' : 'white' }
}
# -------------------------------

SOURCE_DIR = Path( SOURCE_DIR ).resolve() if SOURCE_DIR.startswith( '.' ) else SOURCE_DIR
TARGET_DIR = Path( TARGET_DIR ).resolve() if TARGET_DIR.startswith( '.' ) else TARGET_DIR

def main():
    if USE_UI:
        console = Console()
        logger  = FancyLogger( console )
        logger.start()

    os.makedirs( SOURCE_DIR, exist_ok = True )

    if not os.listdir( SOURCE_DIR ):
        print( "Директория source пуста, положите в неё файлы!" )
        exit

    os.makedirs( TARGET_DIR, exist_ok = True )
    
    for key, category in CATEGORY.items():
        os.makedirs( os.path.join( TARGET_DIR, category[ 'name' ] ), exist_ok = True )

    for root, _, files in os.walk( SOURCE_DIR ):
        for fname in files:
            ext       = Path( fname ).suffix.lower()
            full_path = os.path.join( root, fname )
            rel_path  = os.path.relpath( full_path, SOURCE_DIR )

            try:
                if ext in EXTENSIONS[ 'image' ]:
                    [ nsfw, furry, nsfw_score, furry_score ] = classify_image(
                        full_path,
                        NSFW_THRESH, FURRY_THRESH
                    )
                elif ext in EXTENSIONS[ 'video' ]:
                    [ nsfw, furry, nsfw_score, furry_score ] = classify_video(
                        full_path,
                        VIDEO_KEYFRAMES_OFFSET, VIDEO_KEYFRAMES_COUNT,
                        NSFW_THRESH, FURRY_THRESH, NSFW_AGGREGATION, FURRY_AGGREGATION,
                        VIDEO_LONG_PLAYTIME_FRAMES_COUNT, VIDEO_USE_GAUSS_HANDLER_ALGORITM_FOR_LONG_PLAYTIME,
                        DEBUG_VIDEO
                    )
            except Exception as e:
                continue

            if nsfw and furry:
                category = CATEGORY[ 'NSFW_FURRY' ]
            elif nsfw and not furry:
                category = CATEGORY[ 'NSFW' ]
            elif not nsfw and furry:
                category = CATEGORY[ 'SFW_FURRY' ]
            else:
                category = CATEGORY[ 'SFW' ]

            dest_dir = os.path.join( TARGET_DIR, category[ 'name' ], os.path.dirname( rel_path ) )
            os.makedirs( dest_dir, exist_ok = True )
            dest_path = os.path.join( dest_dir, fname )

            if os.path.exists( dest_path ):
                base, ext_ = os.path.splitext( fname )
                counter = 1
                
                while os.path.exists( os.path.join( dest_dir, f'{base}_{counter}{ext_}' ) ):
                    counter += 1

                dest_path = os.path.join( dest_dir, f'{base}_{counter}{ext_}' )

            if MOVE_FILES:
                shutil.move( full_path, dest_path )

            if USE_UI:
                info = {
                    'name'        : os.path.basename( full_path ),
                    'source'      : rel_path,
                    'dest'        : dest_path,
                    'type'        : ext.upper(),
                    'size_bytes'  : os.path.getsize(full_path),
                    'nsfw_score'  : nsfw_score,
                    'furry_score' : furry_score,
                    'category'    : category
                }

                logger.add_entry( info )
            else:
                print(f'Processing {os.path.basename( full_path )}\n├─Category: {category["name"]}\n├─Type:     {ext}\n├─Source:   {rel_path}\n├─Dest:     {dest_path}\n└─NSFW Score | Furry Score\n  {nsfw_score:.4f}       {furry_score:.4f}\n')

if __name__ == '__main__':
    main()