#!/bin/bash

if [ -e '.venv' ]; then
  source .venv/bin/activate
fi

mkdir -p dist
rm -rf dist/*
mkdir -p dist/original dist/glb dist/off dist/off_temp dist/model

# ENDPOINT=https://apps.humanatlas.io/api/v1/sparql
ENDPOINT=https://apps.humanatlas.io/api--staging/v1/sparql

as_url=https://grlc.io/api-git/hubmapconsortium/ccf-grlc/subdir/mesh-collision/anatomical-structures.csv?endpoint=$ENDPOINT
patch_url=https://grlc.io/api-git/hubmapconsortium/ccf-grlc/subdir/mesh-collision/placement-patches.csv?endpoint=$ENDPOINT

curl $as_url -o dist/model/asct-b-grlc.csv
curl $patch_url -o dist/model/reference-organ-grlc.csv

csvcut -c glb_file dist/model/asct-b-grlc.csv | tail -n +2 | sort | uniq > dist/glb-files.txt

# no blender needed
# cd mesh_processing_blender
# python glb_preprocessor_all_organs.py --downloaded_dir ../dist/original --output_glb_model_dir ../dist/glb

# skip the blender processing stage and directly use the original models as the preprocessed models from stage 1
cd mesh_processing_cgal
python all_organ_preprocessor_cgal.py \
  --urls ../dist/glb-files.txt \
  --downloaded_dir ../dist/original \
  --preproceesed_models_stage_1 ../dist/original \
  --output_off_model_dir ../dist/off \
  --temp_plain_model_dir ../dist/off_temp

rm -rf ../dist/off_temp

cd ../dist/model
cp -r ../off all_preprocessed_off_models_cgal
zip -r ../off-release.zip *
chmod a+r -R ../*

echo aws s3 cp dist/off-release.zip s3://cdn-humanatlas-io/hra-glb-off-releases/hra-glb-off-data.v2.x.zip
echo then update hra-tissue-block-annotation, hra-corridor-generation, hra-3d-cell-generation-api
