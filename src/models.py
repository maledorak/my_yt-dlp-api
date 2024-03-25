
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class ResponseFormatEnum(str, Enum):
    json = 'json'
    text = 'text'
    srt = 'srt'
    verbose_json = 'verbose_json'
    vtt = 'vtt'

class AuthData(BaseModel):
    openai_api_key: str
    openai_org_id: str

class ApiInputTranscribeData(BaseModel):
    language: Optional[str] = None
    prompt: Optional[str] = None
    response_format: Optional[ResponseFormatEnum] = ResponseFormatEnum.text
    temperature: Optional[float] = 0.0

class TranscribeData(ApiInputTranscribeData):
    model: str = 'whisper-1'

class MediaItemInfoPaths(BaseModel):
    audio: str = None
    video: str = None
    raw_info: str = None

class MediaItemInfo(BaseModel):
    title: str
    slug_title: str
    language: str
    uploader: str
    slug_uploader: str
    original_url: str
    uploader_url: str
    paths: 'MediaItemInfoPaths' = MediaItemInfoPaths()



