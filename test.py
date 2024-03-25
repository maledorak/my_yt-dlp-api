import os

import requests
from dotenv import load_dotenv

load_dotenv()

def trans():
    url = 'http://localhost:8080/transcribe'
    data = {
        'url': 'https://youtu.be/KCeiQV4aZ70',
        # 'auth_data': {
        #     'openai_api_key': os.getenv('OPENAI_API_KEY'),
        #     'openai_org_id': os.getenv('OPENAI_ORG_ID')
        # }
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
        'OpenAI-Organization': os.getenv('OPENAI_ORG_ID')
    }
    response = requests.post(url, json=data, headers=headers)
    print(response.json())

def clean():
    url = 'http://localhost:8080/clean'
    response = requests.post(url)
    print(response.json())


if __name__ == '__main__':
    trans()
