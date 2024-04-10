import json
import os
from yt_dlp import YoutubeDL

from src.models import MediaItemInfo
from src.settings import DOWNLOADS_DIR
from src.utils import slugify, logger_config

logger = logger_config(__name__)

# https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#embedding-yt-dlp
def format_selector(ctx): # Not used for now
    """ Select the best video and the best audio that won't result in an mkv.
    NOTE: This is just an example and does not handle all cases """

    # formats are already sorted worst to best
    formats = ctx.get('formats')[::-1]

    # acodec='none' means there is no audio
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] == 'none')

    # find compatible audio extension
    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    # vcodec='none' means there is no video
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    # These are the minimum required fields for a merged format
    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        # Must be + separated list of protocols
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }

def audio_selector(ctx):
    """ Select all audio formats """
    formats = ctx.get('formats')
    opus = [f for f in formats if f['acodec'] == 'opus' and f['vcodec'] == 'none']
    yield opus[0] # lowest opus format will be better than other formats

def get_info(url: str, raw_dump: bool = False) -> 'MediaItemInfo':
    ydl_opts = {
        'username': 'oauth2',
        'password': '',
        'youtube_include_dash_manifest': False, # Opus audio is in dash manifest
        'youtube_include_hls_manifest': False,
        'allow_unplayable_formats': False,
        # 'hls_prefer_native': False,
        'simulate': True,
        'sleep_interval_requests': 1,
        'logger': logger,
        'noplaylist': True,
        'quiet': True,
        'no_progress': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        logger.info('Getting info: "%s"', url)
        raw_info = ydl.extract_info(url, download=True, process=True)

    item_info = MediaItemInfo(
        language=raw_info['language'],
        title=raw_info['title'],
        slug_title=slugify(raw_info['title']),
        uploader=raw_info['uploader'],
        slug_uploader=slugify(raw_info['uploader']),
        original_url=raw_info['original_url'],
        uploader_url=raw_info['uploader_url'],

    )

    if raw_dump:
        raw_info_dir = os.path.join(DOWNLOADS_DIR, item_info.slug_uploader, item_info.slug_title)
        os.makedirs(raw_info_dir, exist_ok=True)
        item_info.paths.raw_info = os.path.join(raw_info_dir, 'raw_info.json')

        with open(item_info.paths.raw_info, 'w') as f:
            json.dump(raw_info, f, indent=2)
    
    return item_info

def download_audio(url: str) -> 'MediaItemInfo':
    info = get_info(url)
    item_dir = os.path.join(DOWNLOADS_DIR, info.slug_uploader, info.slug_title)
    os.makedirs(item_dir, exist_ok=True)

    ydl_opts = {
        'username': 'oauth2',
        'password': '',
        'logger': logger,
        'quiet': True,
        'no_progress': True,
        'noplaylist': True,
        'youtube_include_dash_manifest': True, # Opus audio is in dash manifest
        'youtube_include_hls_manifest': False,
        'paths': {'home': item_dir},
        'outtmpl': {'default': 'video.%(ext)s'},
        'keepvideo': True,
        'cachedir': False,
        'format': audio_selector,
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            # 'preferredcodec': 'opus',
            # 'preferredquality': 0.5
        }],
    }

    info.paths.audio = os.path.join(item_dir, 'audio.webm')

    with YoutubeDL(ydl_opts) as ydl:
        logger.info(f'Downloading audio: "{url}"')

        if os.path.exists(info.paths.audio):
            logger.info(f'Already downloaded to "{info.paths.audio}"')
        else:
            errors = ydl.download([url])
            if errors:
                logger.error(f'Failed to download audio: {errors}')
                return None
            os.rename(os.path.join(item_dir, 'video.webm'), info.paths.audio)
            logger.info(f'Downloaded to "{info.paths.audio}"')
    return info


def stereo_to_mono(path) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f'File not found: {path}')
    
    if path.endswith('_mono.webm'):
        return path

    output_path = f'{path}_mono.webm'
    # 18k for mono opus audio is good enough to transcribe
    os.system(f'ffmpeg -i {path} -codec:a libopus -b:a 18k -ac 1 {output_path}')
    return output_path
