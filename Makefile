define PRINT_HELP_PYSCRIPT
import re, sys

print("{ln}{sp}HELP{sp}{ln}".format(ln=24*"=", sp=5*" "))
for line in sys.stdin:
	category_match = re.match(r'^#%% (.*)$$', line)
	target_match = re.match(r'^([a-zA-Z0-9_-]+):.*?#% (.*)$$', line)
	if category_match:
		category, = category_match.groups()
		print("\n{}:".format(category))
	if target_match:
		target, help = target_match.groups()
		print("  {:26} {}".format(target, help))
endef
export PRINT_HELP_PYSCRIPT

.PHONY: help
.DEFAULT_GOAL := help
help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

VERSION=ffmpeg_6.1.1-ytdlp_2024.04.09
DOCKER_IMAGE=ghcr.io/maledorak/yt-dlp-api:${VERSION}

#%% Docker commands
image: #% Show the image
	@echo ${DOCKER_IMAGE}

build: #% Build the docker image
	docker build -t ${DOCKER_IMAGE} .

run: #% Run server in the container
	docker run -p 8080:80 ${DOCKER_IMAGE}

run_bash: #% Run bash in the container
	docker run -it --entrypoint="" ${DOCKER_IMAGE} bash

login: #% Login to ghcr.io
	@echo ${GH_PACKAGES_TOKEN} | docker login ghcr.io -u maledorak --password-stdin

vps_echo: #% Echo the login
	@echo "echo ${GH_PACKAGES_TOKEN} | docker login ghcr.io -u maledorak --password-stdin"

push: login #% Push the docker image
	docker push ${DOCKER_IMAGE}
