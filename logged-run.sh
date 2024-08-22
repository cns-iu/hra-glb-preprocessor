#!/bin/bash
# source constants.sh

rm -r dist log.txt
time bash -c "time ./run.sh 2>&1" | tee log.txt
