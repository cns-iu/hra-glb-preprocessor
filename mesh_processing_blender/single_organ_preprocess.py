"""
Date: 03/18/2024
Author: Lu
"""

import addon_utils
import array
import bmesh
import bpy
from bpy import context
import os
import math
from mathutils import *
from math import *
from object_print3d_utils import mesh_helpers
import datetime
from datetime import datetime
import pandas as pd
import logging
import shutil
import time
import sys
import argparse
import textwrap

cur_dir = os.getcwd()
if not cur_dir in sys.path:
    sys.path.append(cur_dir)

from HuBMAP_reduction import FileLocations
from HuBMAP_reduction import import_files, convert_time, generate_outputs
from HuBMAP_reduction import clean_scene, setup_scene, enable_addons
from HuBMAP_reduction import select_all_meshes, add_edgesplit_modifier
from HuBMAP_reduction import count_polys, check_manifold
from HuBMAP_reduction import decimate, analyze_mesh
from my_argparser import MyArgParser


def setup_logging(output_root):
    """
    Logging system

    Args:
        output_root (str): directory for the output files
    """
    now = datetime.now()
    dt_string = now.strftime("%H%M%S")
    log_location = os.path.join(output_root, 'output_' + dt_string + '.log')
    logging.basicConfig(filename=log_location, encoding='utf-8', level=logging.DEBUG)


def generate_output_LOD(lod, output_filepath, file_locations):

    #orient the camera to frame the mesh
    bpy.ops.object.mode_set(mode='OBJECT')
    select_all_meshes()
    bpy.ops.view3d.camera_to_view_selected()

    output_dir = os.path.dirname(output_filepath)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    bpy.ops.export_scene.gltf(filepath=output_filepath[:-4], export_format='GLB', export_cameras=False)


def mesh_process(file_locations, repair_type, levels, max_tris):
    """
    This is the main mesh processing script.  It will run through a series of steps:

    1.  Start a timer for the processing steps
    2.  Import the source file
    3.  Set up the Blender Scene (Cameras, lighting etc.)
    4.  Analyze the mesh to identify it's attributes
    5.  Reset the pivot points for all mesh and group objects
    6.  Iteratively generate LOD models through decimation
    6.  Generate output files and renders for each LOD as it is generated

    Args:
        file_locations (object): an object containing urls and filenames for inputs and outputs
    """
    #start a timer for the process
    start_time = time.time()
   
    #import the source file
    print("Import File: %s" %file_locations.filename)
    import_files(file_locations)
    
    #setup the Blender scene
    objs = select_all_meshes()
    print("Setup scene...")
    setup_scene(file_locations.hdr)

    #add edge split to harden edges
    add_edgesplit_modifier()

    #analyze the mesh to determine the attributes of the input file
    #We should return this values as attributes of the input file when integrated into the NIH 3D workflows.
    polys, verts, manifold, intersections = analyze_mesh(True, repair_type)
    
    print("Analyze mesh...")
    print("Starting Polys: %s" %polys)
    print("Starting Verts: %s" %verts)
    print("Non-Manifold Objects: %s" %manifold)
    print("Objects with self-intersections: %s" %intersections)
    
    for max_tri, output_filepath in max_tris.items():
        approximate_lod = min(100, int(max_tri / polys * 100))
        levels[approximate_lod] = output_filepath
        
    #create lod models
    objs = select_all_meshes()

    bpy.context.view_layer.objects.active = objs[0]
    
    print("Create preprocessed models")
    levels = sorted(levels.items(), reverse=True)
    prev_level = 100.0

    for level, output_filepath in levels:
        ratio = level / prev_level
        prev_level = level
        decimate(ratio)
        verts, polys = count_polys()
        #check for and repair manifold errors
        manifold = check_manifold(True, False, repair_type)
        
        #define the output formats for specific input types depending on their source and attributes.  Will output glb by default.
        print("output files...")
        generate_output_LOD(level, output_filepath, file_locations)
        
        
    #reporting of elapsed time for mesh processing.
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info("process completed in %s" %convert_time(elapsed_time))


def main(repair_type="doubles"):
    """
    Sets up the intital scene, input and output paths, and logging.
    will process each file from a list of paths, cleaning the scene between.

    Different repair types can be set for the process:

    1. print - will run the 3d printing add-on repair.  Tries to fill holes so will cause errors where this isn't appropriate
    2.  doubles - will only fuse doubled vertices.

    Args:
        repair_type (str): define the type of repair as either "print" or "doubles".
    """
    
    
    enable_addons()
    
    # argument from argparser
    myArg = MyArgParser()
    input_file_path = myArg.input_file_path
    levels = myArg.levels
    max_tris = myArg.max_triangles

    # default hdr
    hdr = "./studio_small_01_4k.exr"

    print(input_file_path)
    if not input_file_path.endswith('glb'):
        print("The 3D model is not in GLB format!")
        return

    # Ensure the input and output directories exist
    if not os.path.exists(input_file_path):
        print(f"Input path '{input_file_path}' does not exist.")
        return

    #remove default objects and create new camera
    clean_scene()
    camera_data = bpy.data.cameras.new(name='Camera')
    camera_object = bpy.data.objects.new('Camera', camera_data)
    bpy.context.scene.collection.objects.link(camera_object)
    bpy.context.scene.camera = camera_object

    #path to the source file
    source_path = input_file_path
    split_path = os.path.splitext(source_path)
    
    #extension for the source file
    extension = split_path[1]
    
    #store the filename without the extension
    filestem = os.path.split(split_path[0])[1]
    
    #store the complete filename
    filename = filestem + extension
    
    #output directory for output files (testing only)

    # output_dir = output_root
    # no need to specify output directory, which is given by the command arguments. 
    output_dir = ""
    output_root = ""

    logging.info('processing: ' + input_file_path)

    file_locations = FileLocations(filename, filestem, extension, source_path, output_dir, output_root, hdr)

    #process the files, levels and max_tris are dictionaries, (key, value) -> (lod, output_filename) or (max_triangle, output_filename)
    mesh_process(file_locations, repair_type, levels, max_tris)
 

main('print')