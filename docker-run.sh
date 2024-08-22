#!/bin/bash
# source constants.sh

rm -r dist log.txt
docker compose run processor | tee log.txt
