#!/bin/bash

if [ -e '.venv' ]; then
  source .venv/bin/activate
fi

mkdir -p dist
rm -rf dist/*
mkdir -p dist/original dist/glb dist/off dist/off_temp

# no blender needed
# cd mesh_processing_blender
# python glb_preprocessor_all_organs.py --downloaded_dir ../dist/original --output_glb_model_dir ../dist/glb

# skip the blender processing stage and directly use the original models as the preprocessed models from stage 1
cd mesh_processing_cgal
python all_organ_preprocessor_cgal.py --preproceesed_models_stage_1 ../dist/original --output_off_model_dir ../dist/off --temp_plain_model_dir ../dist/off_temp

rm -rf ../dist/off_temp

cd ../dist/off
zip -r ../off-release.zip *
chmod a+r -R ../*
