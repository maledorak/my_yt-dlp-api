import chainlit as cl
import re
import os
import requests
from dotenv import load_dotenv
import httpx
import asyncio
from openai import AsyncOpenAI

client = AsyncOpenAI()
cl.instrument_openai()

settings = {
    "model": "gpt-4o",
    "temperature": 0,
    # ... more settings
}

load_dotenv()

youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com|youtu\.be)\/(?:watch\?v=)?(?:embed\/)?(?:v\/)?(?:shorts\/)?(?:\S+)'

@cl.on_chat_start
def on_chat_start():
    print("A new chat session has started!")

@cl.set_starters
async def set_starters():
    return [
        # cl.Starter(
        #     label="Download YouTube video",
        #     message="https://www.youtube.com/watch?v=_3o3U5qBPJM",
        #     ),
        cl.Starter(
            label="Download YouTube video 2",
            message="https://www.youtube.com/watch?v=Vx65Gdeat-c",
        ),
        cl.Starter(
            label="Don't download anything",
            message="Not a YouTube video url",
        ),
    ]

@cl.step(type="tool", name="Download YouTube video")
async def ytdlp_download(url: str):
    print("Downloading...")
    # await cl.sleep(2)
    base_url = 'http://localhost:8080/transcribe'
    data = {
        'url': url,
        'auth_data': {
            'openai_api_key': os.getenv('OPENAI_API_KEY'),
            'openai_org_id': os.getenv('OPENAI_ORG_ID')
        }
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Organization': os.getenv('OPENAI_ORG_ID')
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(base_url, json=data, headers=headers, timeout=120)
    # print(response.json())
    return response.json()['text']

@cl.on_message
async def on_message(message: cl.Message):
    print(message.author)
    if message.author != "User":
        return
    
    # Find all YouTube URLs in the message content
    youtube_urls = re.findall(youtube_pattern, message.content)
    
    if youtube_urls:
        response = f"I found {len(youtube_urls)} YouTube URL(s) in your message:\n" + "\n".join(youtube_urls)
        response += "\n\nDo you want to download them?"

        res = await cl.AskActionMessage(
            content=response,
            actions=[
                cl.Action(name="download", value="download", label="✅ Download"),
                cl.Action(name="cancel", value="cancel", label="❌ Cancel"),
            ],
        ).send()

        if res['value'] == "download":
            transcription = await ytdlp_download(youtube_urls[0])
            if transcription != "":
                response = f"Here is the transcription of the video:\n\n{transcription}"
                with open("transcription.txt", "w") as f:
                    f.write(transcription)
            else:
                response = "I couldn't download the video."
            return await cl.Message(response).send()
        else:
            response = "Cancelled."
            return await cl.Message(response).send()

    saved_transcription = ""
    with open("transcription.txt", "r") as f:
        saved_transcription = f.read()

    if saved_transcription != "":
        response = await client.chat.completions.create(
            messages=[
                {
                    "content": "You are a helpful bot, you always reply in English, your task is to answer questions about the video transcript.\n\nHere is the transcript:\n\n" + saved_transcription,
                    "role": "system"
                },
                {
                    "content": message.content,
                    "role": "user"
                }
            ],
            **settings
        )
        return await cl.Message(content=response.choices[0].message.content).send()
        

    # else:
        # response = "I didn't find any YouTube URLs in your message."
    
    # await cl.Message(response).send()
