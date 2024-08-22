#!/bin/bash
# source constants.sh

rm -rf dist log.txt
mkdir -p dist
docker compose run -it processor | tee log.txt
