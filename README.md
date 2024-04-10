# yt-dlp-api

## yt-dlp youtube oauth2
In order to download videos without 429 error, you need to authenticate with youtube. This is done by using oauth2. The following steps are needed to authenticate:

### Create your own OAuth2 client

1. Use the following instructions to create your own OAuth2 client for yt-dlp plugin:
[link](https://developers.google.com/youtube/v3/live/guides/auth/devices)
2. Get client_id and client_secret
3. Add client_id and client_secret to `plugins/yt-dlp-youtube-oauth2/yt_dlp_plugins/extractor/youtubeoauth.py` file (TODO: should be added to env variables)

### Authenticate with yt-dlp

1. On vps run bash in yt-dlp container `docker exec -it yt-dlp bash`
2. Run `/opt/yt-dlp/venv/bin/yt-dlp --username oauth2 --password '' https://youtu.be/dQw4w9WgXcQ`
3. Follow the instructions to authenticate
4. Remove downloaded video


## Run in n8n docker-compose

```
services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:1.33.1
    restart: always
    environment:
      - N8N_HOST=n8n.example.com
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - NODE_ENV=production
      - WEBHOOK_URL=https://n8n.example.com/
      - GENERIC_TIMEZONE=Europe/Warsaw
      - TZ=Europe/Warsaw
    ports:
      - "127.0.0.1:5678:5678"
    volumes:
      - /apps/n8n/data:/home/node/.n8n
      # Uncomment the line below if you're reading/writing local files with n8n
      - /apps/n8n/files:/files
    networks:
      - n8n

  ytdlp:
    image: ghcr.io/maledorak/yt-dlp-api:ffmpeg_6.1.1-ytdlp_2024.04.09
    restart: always
    ports:
      - "127.0.0.1:8080:80"
    environment:
      - TZ=Europe/Warsaw
    volumes:
      - /apps/ytdlp/downloads:/opt/yt-dlp/downloads
      - /apps/ytdlp/.cache/yt-dlp:/root/.cache/yt-dlp # cache for oauth2 token
    networks:
      - n8n

networks:
  n8n:
```
