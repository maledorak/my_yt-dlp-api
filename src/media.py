import json
import os
from yt_dlp import YoutubeDL

from src.models import MediaItemInfo
from src.settings import DOWNLOADS_DIR
from src.utils import slugify, logger_config

logger = logger_config(__name__)

# https://github.com/yt-dlp/yt-dlp?tab=readme-ov-file#embedding-yt-dlp
def format_selector(ctx):
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

def progress_hook(d):
    if d['status'] == 'finished':
        logger.info('Done downloading, now post-processing ...')


def get_info(url: str, raw_dump: bool = False) -> 'MediaItemInfo':
    ydl_opts = {
        'username': 'oauth2',
        'password': '',
        'logger': logger,
        'noplaylist': True,
        'quiet': True,
        'no_progress': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        logger.info('Getting info: "%s"', url)
        raw_info = ydl.extract_info(url, download=False, process=False)

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
        'paths': {'home': item_dir},
        'outtmpl': {'default': 'video.%(ext)s'},
        'keepvideo': True,
        # 'age_limit': 30,
        # 'progress_hooks': [progress_hook],

        'format': format_selector,
        'postprocessors': [{  # Extract audio using ffmpeg
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
    }

    # help(yt_dlp.postprocessor)

    info.paths.audio = os.path.join(item_dir, 'audio.m4a')

    with YoutubeDL(ydl_opts) as ydl:
        logger.info(f'Downloading audio: "{url}"')

        if os.path.exists(info.paths.audio):
            logger.info(f'Already downloaded to "{info.paths.audio}"')
        else:
            errors = ydl.download([url])
            if errors:
                logger.error(f'Failed to download audio: {errors}')
                return None
            os.rename(os.path.join(item_dir, 'video.m4a'), info.paths.audio)
            logger.info(f'Downloaded to "{info.paths.audio}"')

    return info
