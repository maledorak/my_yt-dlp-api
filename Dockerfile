# https://github.com/linuxserver/docker-ffmpeg
FROM lscr.io/linuxserver/ffmpeg:6.1.1-cli-ls128

RUN \
  echo "**** install build packages ****" && \
  apt-get update && \
  apt-get install -y \
    python3-venv && \
  python3 -m venv /opt/yt-dlp/venv && \
  /opt/yt-dlp/venv/bin/pip install --no-cache-dir --upgrade pip

COPY requirements.txt /opt/yt-dlp/requirements.txt
RUN \
  /opt/yt-dlp/venv/bin/pip install --no-cache-dir -r /opt/yt-dlp/requirements.txt

COPY . /opt/yt-dlp

WORKDIR /opt/yt-dlp
ENTRYPOINT ["/opt/yt-dlp/venv/bin/uvicorn", "app:api", "--host", "0.0.0.0", "--port", "80", "--proxy-headers"]
