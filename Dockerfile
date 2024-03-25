# https://github.com/linuxserver/docker-ffmpeg/releases
FROM lscr.io/linuxserver/ffmpeg:6.1.1-cli-ls128

ENTRYPOINT ["/bin/bash", "-c"]
# CMD ["bash"]
