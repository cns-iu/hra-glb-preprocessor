#!/bin/bash

if [ -e '.venv' ]; then
  source .venv/bin/activate
fi

mkdir -p dist
rm -rf dist/*
mkdir -p dist/original dist/glb dist/off dist/off_temp

cd mesh_processing_blender
python glb_preprocessor_all_organs.py --downloaded_dir ../dist/original --output_glb_model_dir ../dist/glb

cd ../mesh_processing_cgal
python all_organ_preprocessor_cgal.py --preproceesed_models_stage_1 ../dist/glb --output_off_model_dir ../dist/off

rm -rf dist/off_temp
