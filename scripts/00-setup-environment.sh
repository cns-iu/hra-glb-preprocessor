#!/bin/bash
set -euo pipefail
IFS=$'\n\t'
set -v

# Base paths

DIR="${0%/*}"
ROOT_DIR="$DIR/.."

# Parse arguments

ENV=`realpath ${1:-.venv}`
if [[ ! "$ENV" = /* ]]; then ENV="$ROOT_DIR/$ENV"; fi

if [ ! -e "$ENV/bin/activate" ]; then
  python3 -m venv $ENV
fi

# Install dependencies
if [ -e "$ENV/bin/activate" ]; then
  set +u # Disable in case we are running old venv versions that can't handle strict mode
  source "$ENV/bin/activate"
  set -u

  python -m pip install -r "$ROOT_DIR/requirements.txt"
  python -m pip cache purge

  if [ ! -e "$ROOT_DIR/mesh_processing_cgal/build/mesh_hole_filling" ]; then
    mkdir -p $ENV/opt
    curl -Ls https://github.com/CGAL/cgal/releases/download/v5.5.3/CGAL-5.5.3.zip -o $ENV/CGAL.zip
    unzip $ENV/CGAL.zip -d $ENV/opt
    mv $ENV/opt/CGAL-* $ENV/opt/CGAL
    rm $ENV/CGAL.zip

    mkdir -p mesh_processing_cgal/build
    export CGAL_HOME=$ENV/opt/CGAL
    pushd mesh_processing_cgal/build
      cmake ..
      make
    popd

    mv mesh_processing_cgal/build/mesh_* .venv/bin/
    rm -r mesh_processing_cgal/build
  fi

  if [ ! -e $ENV/opt/blender ]; then
    mkdir -p $ENV/opt
    curl -s https://download.blender.org/release/Blender3.6/blender-3.6.15-linux-x64.tar.xz -o $ENV/blender.tar.xz
    tar -xf $ENV/blender.tar.xz -C $ENV/opt
    mv $ENV/opt/blender-*-linux-x64 $ENV/opt/blender
    rm $ENV/blender.tar.xz

    echo "export PATH=\$PATH:${ENV}/opt/blender" >> $ENV/bin/activate

    $ENV/opt/blender/3.6/python/bin/python3.10 -m pip install pandas
  fi
fi

if [ -e "$ENV/bin/activate" ]; then
  set +u # Just to be on the safe side
  deactivate
  set -u
fi
