# https://github.com/linuxserver/docker-ffmpeg
FROM lscr.io/linuxserver/ffmpeg:6.1.1-cli-ls128

RUN \
  echo "**** install build packages ****" && \
  apt-get update && \
  apt-get install -y \
    python3-venv && \
  python3 -m venv /opt/yt-dlp/venv && \
  /opt/yt-dlp/venv/bin/pip install --no-cache-dir --upgrade pip

COPY . /opt/yt-dlp
RUN \
  /opt/yt-dlp/venv/bin/pip install --no-cache-dir -r /opt/yt-dlp/requirements.txt && \
  /opt/yt-dlp/venv/bin/pip install --no-cache-dir /opt/yt-dlp/plugins/yt-dlp-youtube-oauth2

WORKDIR /opt/yt-dlp
ENTRYPOINT ["/opt/yt-dlp/venv/bin/uvicorn", "app:api", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
