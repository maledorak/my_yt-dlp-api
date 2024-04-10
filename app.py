import os
import shutil
from typing import Optional
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import yt_dlp

from src.utils import logger_config
from src.media import download_audio, get_info, stereo_to_mono
from src.tts import transcribe_audio, simple_transcribe
from src.models import AuthData, TranscribeData, ApiInputTranscribeData
from src.settings import DOWNLOADS_DIR

logger = logger_config(__name__)

api = FastAPI()

class TranscribeInput(BaseModel):
    url: str
    tts_data: Optional['ApiInputTranscribeData'] = ApiInputTranscribeData()
    # auth_data: 'AuthData'

class TranscribeOutput(BaseModel):
    text: str = None
    error: str = None

class CleanOutput(BaseModel):
    text: str = None
    error: str = None

@api.post("/transcribe", response_model=TranscribeOutput)
async def get_transcribe(input: TranscribeInput, request: Request):
    if not request.headers['authorization'] and not request.headers['openai-organization']:
        return {"error": "Missing Authorization and OpenAI-Organization header"}
    
    auth_data = AuthData(
        openai_api_key=request.headers['authorization'].split(' ')[1],
        openai_org_id=request.headers['openai-organization']
    )

    item_info = download_audio(input.url)
    item_info.paths.audio_mono = stereo_to_mono(item_info.paths.audio)

    if os.path.getsize(item_info.paths.audio_mono) > 25000000:
        return {"error": "Audio file is too large, longer than 25mb"}

    if input.tts_data.language:
        language = input.tts_data.language
    else:
        language = item_info.language

    transcribe_data = TranscribeData(
        language=language,
        prompt=input.tts_data.prompt,
        response_format=input.tts_data.response_format,
        temperature=input.tts_data.temperature
    )

    transcript = transcribe_audio(item_info, transcribe_data, auth_data)
    return {'text': transcript}

@api.post('/clean')
async def clean_downloads():
    root, dirs, files = next(os.walk(DOWNLOADS_DIR))
    dirs_count = len(dirs)

    for d in dirs:
        shutil.rmtree(os.path.join(root, d))

    return {'text': f"Deleted {dirs_count} directories"}

class HealthCheckOutput(BaseModel):
    text: str = None
    error: str = None

@api.get('/health', response_model=HealthCheckOutput)
async def health_check():
    return {'text': 'ok'}

if __name__ == "__main__":
    uvicorn.run("app:api", host="0.0.0.0", port=8080, reload=True)
    # info = get_info('https://youtu.be/uoupp8kHQY0?list=TLGGMreXo8PtjG4yNzAzMjAyNA', True)
    # help(yt_dlp.postprocessor.ffmpeg.FFmpegExtractAudioPP)
    # download_audio('https://youtu.be/uoupp8kHQY0?list=TLGGMreXo8PtjG4yNzAzMjAyNA')
    # path = '/home/mariusz/code/projects/my_yt-dlp-api/downloads/wes-roth/test_opus/lowestOpus.webm'
    # path='./tmp/lowestOpus.webm'


    # simple_transcribe(path)
