from openai import OpenAI

from src.models import AuthData, MediaItemInfo, TranscribeData
from src.utils import logger_config

logger = logger_config(__name__)

def transcribe_audio(item: 'MediaItemInfo', transcribe_data: 'TranscribeData', auth_data: 'AuthData'):
    # files = {
    #     'file': open(item.paths.audio, 'rb')
    # }

    # headers = {
    #     "Authorization": f"Bearer {auth_data.openai_api_key}",
    #     "OpenAI-Organization": auth_data.openai_org_id,
    #     'Content-Type': 'multipart/form-data'
    # }

    # # Now, you can send the POST request
    # response = requests.post(
    #     "https://api.openai.com/v1/audio/transcriptions",
    #     headers=headers, files=files, data=transcribe_data, timeout=120
    # )
    # files['file'].close()

    # Handling the response
    # # if response.status_code == 200:
    # #     logger.info(f'Transcribe success')
    # # else:
    # #     logger.error(f'Transcribe failed: {response.status_code}, {response.text}')

    # return response.json()

    client = OpenAI(
        api_key=auth_data.openai_api_key,
        organization=auth_data.openai_org_id
    )

    audio_file = open(item.paths.audio, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language=transcribe_data.language,
        prompt=transcribe_data.prompt,
        response_format=transcribe_data.response_format.value,
        temperature=transcribe_data.temperature
    )
    audio_file.close()
    if transcribe_data.response_format == 'json':
        return transcript['text']
    return transcript
