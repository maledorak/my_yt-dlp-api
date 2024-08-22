import os

import requests
from dotenv import load_dotenv

load_dotenv()

def trans():
    """
    Debug function which sends a POST request to the transcribe endpoint of dockerized app
    """
    url = 'http://localhost:8080/transcribe'
    data = {
        'url': 'https://www.youtube.com/watch?v=Vx65Gdeat-c',
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
    response = requests.post(url, json=data, headers=headers)
    print(response.json())

def clean():
    """
    Debug function which sends a POST request to the clean endpoint of dockerized app
    """
    url = 'http://localhost:8080/clean'
    response = requests.post(url)
    print(response.json())


if __name__ == '__main__':
    trans()
    # clean()
