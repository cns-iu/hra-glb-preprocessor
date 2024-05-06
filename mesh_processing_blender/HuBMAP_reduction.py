# HuBMAP_reduction.py

"""
Will create LOD models from a directory of glb files, center all pivots, render images, and output glb and fbx files.

* Update **input_dir**, **hdr**, **output_dir** in main() to match the location of your test files.

You should run main() to process the mesh files.  There are two options for the repair of input files:

**"print"** will run the 3d printing add-on repair which is good for meshes that are already closed.  It will, however,
attempt to close holes, which may create results that are poor when run on meshes that were designed to be open.

**"doubles"** is more appropriate for meshes that have open pieces as it will only fuse doubled vertices.

Analyze_outputs() will subsequently determine whether the outputs were manifold, self-intersecting, and do a poly count.
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

#lists that are used internally to output results
df_filename = []
df_time  = []
df_stpolys = []
df_polys80 = []
df_polys40 = []
df_polys20 = []
df_manifold = []
df_intersections = []
ex_filename = []
ex_polys = []
ex_manifold = []
ex_intersection = []

class FileLocations:
    """
    This class is used to organize a set of paths and filenames that are used in multiple locations
    """
    def __init__(self, filename, filestem, extension, source_path, output_dir, output_root, hdr):
        self.filename = filename
        self.filestem = filestem
        self.extension = extension
        self.source_path = source_path
        self.output_dir = output_dir
        self.output_root = output_root
        self.hdr = hdr

class Materials:
    """
    This class is a set of attributes used to describe a material
    """
    def __init__(self, name, r, g, b, spec_val, metal_val, rough_val):
        self.name = name
        self.r = r
        self.g = g
        self.b = b
        self.specular = spec_val
        self.metallic = metal_val
        self.roughness = rough_val


def enable_addons():
    """Enable Blender Add-Ons.  We only use the 3D Printing Add-On, but more may be added at a later date"""

    addon_utils.enable('object_print3d_utils')
    

def purge_orphans():
    """Removes any unused orphan data from Blender"""

    if bpy.app.version >= (3, 0, 0):
        bpy.ops.outliner.orphans_purge(
            do_local_ids=True, do_linked_ids=True, do_recursive=True
        )
    else:
        # call purge_orphans() recursively until there are no more orphan data blocks to purge
        result = bpy.ops.outliner.orphans_purge()
        if result.pop() != 'CANCELLED':
            purge_orphans()

def clean_scene():

    """Removes all objects from the Blender scene"""

    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    collection_names = [col.name for col in bpy.data.collections]
    for name in collection_names:
        bpy.data.collections.remove(bpy.data.collections[name])

    purge_orphans()
           
def check_intersections():
    """
    Does the object have intersecting faces?

    Returns:
        intersections (list of str): names of objects that are self-intersecting
    """
    
    objects = select_all_meshes()
    intersections = []
    for obj in objects:
        faces_intersect = mesh_helpers.bmesh_check_self_intersect_object(obj)
        if (len(faces_intersect)) > 0:
            intersections.append(obj.name)
    return intersections

    
def mesh_process(file_locations, repair_type):
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
    df_filename.append(file_locations.filename)
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

    df_stpolys.append(polys)
    df_manifold.append(manifold)
    df_intersections.append(intersections)

    #reset the origins of the input objects.  Set the origin of each mesh to the geometry center then find the empty objects and center their position to the
    #average of the child geometries.
    # objects = select_all_meshes()
    # bpy.ops.object.select_all(action='DESELECT')
    # print("reset origins")
    # for obj in objects:
    #     if obj.type == 'MESH':
    #         obj.select_set(True)
    #         bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    #         bpy.ops.object.select_all(action='DESELECT')
            
    # empties = select_all_empty()
    # if len(empties) > 0:
    #     update_origins_from_children(empties[0])

    objs = select_all_meshes()
    
    #create lod models
    levels = [100,80,40,20]
    ratios = [1.0,0.8,0.5,0.5]
    
    i=0
    
    objs = select_all_meshes()

    bpy.context.view_layer.objects.active = objs[0]
    
    print("Create lod models")
    for level in levels:
        print("Current level: %s" %level)
        decimate(ratios[i])
        verts, polys = count_polys()
        #push data to dataframe
        if i == 0:    
            df_polys80.append(polys)
        elif i == 1:
            df_polys40.append(polys)
        else:
            df_polys20.append(polys)
        
        #check for and repair manifold errors
        manifold = check_manifold(True, False, repair_type)
        
        #define the output formats for specific input types depending on their source and attributes.  Will output glb by default.
        print("output files...")
        convert_formats = [".fbx"] 
        suffix = "-" + str(levels[i])
        print("render images")
        suffix_png =  "-" + str(levels[i])    
        #output the mesh files and render pngs for the input files
        if len(convert_formats) > 0:
            logging.info("output %s:" %convert_formats)
            generate_outputs(convert_formats, suffix_png, suffix, file_locations)
        
        i += 1   
        
    #reporting of elapsed time for mesh processing.
    end_time = time.time()
    elapsed_time = end_time - start_time
    logging.info("process completed in %s" %convert_time(elapsed_time))
    df_time.append(convert_time(elapsed_time))
    
def remove_interior_faces():
    """
    A basic utility to remove doubled vertices then select and remove all interior faces from the currently
    selected object.
    """
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
    select_all_meshes()
    bpy.ops.mesh.remove_doubles()
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_interior_faces()
    bpy.ops.mesh.delete(type='FACE')
    bpy.ops.object.mode_set(mode='OBJECT')

def clean_up():
    """
    Clean up operation to remove interior faces, doubles, reset normals, quads to tris, and uses the 3d print add-on
    """
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0001)
    bpy.ops.object.mode_set(mode='OBJECT')
   

    
def add_edgesplit_modifier():
    """
    Add an edge split modifier to objects.  This will harden creases before smooth shading is applied.
    """
    bpy.ops.object.select_all(action='DESELECT')
    objects = context.scene.objects
    for obj in objects:
        obj.select_set(obj.type == "MESH")
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode='OBJECT')
        edge_modifier = obj.modifiers.new(name='split', type='EDGE_SPLIT')
        if edge_modifier:
            edge_modifier.show_viewport = False
            edge_modifier.show_render = False
            bpy.ops.object.modifier_apply(modifier='split')

def update_origins_from_children(obj):
    """
    Will center the empty grouping objects to the center of child origins

    Args:
        obj (bpy_types.Object): current object
    """
    if obj.type=='EMPTY':
        barn = list(filter(lambda x: x is not None, [update_origins_from_children(o) for o in obj.children]))        
        antall = len(barn)
        if antall>0:
            print(barn[0:4])
            total = sum(barn, Vector((0.0,0.0,0.0)) )
            nypos = total/antall
            for barn in obj.children:
                barn.location-=nypos
            obj.location=nypos
            return nypos
        else:
            return None
    else:
        return obj.location

  

def import_files(file_locations):
    """
    Will import a file that is in **glb** format

    Args:
        file_locations (object): an object containing urls and filenames for input/output
    """
 
    source_path = file_locations.source_path
    bpy.ops.import_scene.gltf(filepath=source_path)
    

def select_all_meshes():
    """
    A simple utility script to select all mesh objects in the Blender scene.

    Returns:
        all_objects (list of bpy_types.Object): A list of all mesh objects in the scene
    """
    objects = context.scene.objects
    for obj in objects:
        obj.select_set(obj.type == 'MESH')
    all_objects = context.selected_objects
    
    return all_objects

def select_all_empty():
    """
    A simple utility script to select all Empty objects in the Blender scene.

    Returns:
        all_objects (list of bpy_types.Object): A list of all Empty objects in the scene
    """
    objects = context.scene.objects
    for obj in objects:
        obj.select_set(obj.type == 'EMPTY')
    all_objects = context.selected_objects
    
    return all_objects

def analyze_mesh(repair, repair_type):
    """
    Will scan the input file to determine whether objects in the scene are manifold, or have self-intersections.
    It will also do a polygon and vertex count summation for the scene.

    Args:
        repair (bool): whether or not to repair non-manifold errors
        repair_type (str): type of repair to run if run.
      
    Returns:
        polys (int): What is the total polygon count in the scene
        verts (int): What is the total vertex count in the scene
        manifold (list of str): names of objects that are not manifold
        intersections (list of str): names of objects that are self-intersecting
    """
    
    #skip checks for STL because it's a waste to check, they will always all be False.
    manifold = check_manifold(repair, True, repair_type)
    intersections = check_intersections()
    verts, polys = count_polys()
        
    logging.info('Starting Verts: %s' %verts)
    logging.info('Starting Polys: %s' %polys)
    
    return polys, verts, manifold, intersections


def count_polys():
    """
    Will count the total number of vertices and polygons in the scene.

    Returns:
        verts (int): total number of vertices in the scene
        polys (int): total number of polygons in the scene

    """
    verts, polys = 0, 0
    dg = bpy.context.evaluated_depsgraph_get()  # Getting the dependency graph
    for obj in select_all_meshes():
        obj = obj.evaluated_get(dg)
        mesh = obj.to_mesh()
        verts += len(mesh.vertices)
        polys += len(mesh.polygons)
    return verts, polys
  
         
def generate_outputs(formats, suffix_png,suffix, file_locations, wire = True, glb = True):
    """
    Will lock the camera to the object(s), render a png, then output files in formats from a provided list.  It may or
    may not output the wireframe images and/or the glb file (defaults to True)

    Args:
        formats (list of str): the extensions that need to be output
        suffix_png (str): the suffix that needs to be added to the png image
        suffix (str): the suffix that needs to be added to the mesh files
        file_locations (object): an object containing urls and filenames for input/output
        wire (bool): is the wireframe rendering needed?
        glb (bool): is the glb mesh output needed?
    """

    #orient the camera to frame the mesh
    bpy.ops.object.mode_set(mode='OBJECT')
    select_all_meshes()
    bpy.ops.view3d.camera_to_view_selected()

    #render image
    # render_png(suffix_png, file_locations)

    #output files
    output_files(suffix,formats, glb, file_locations)
    
    # Create an empty dictionary to store object volumes.
    objs = select_all_meshes()
    object_materials = {}
    for obj in objs:
        object_materials[obj.name] = obj.active_material
    
    #output wireframe images if requested
    if wire:
        objs = select_all_meshes()
        wire_solid = create_wire_mat()
        for ob in objs:
            apply_mat(wire_solid)
        
        # render_png("_wire_solid" + suffix, file_locations)
        
        #restore original materials
        objects = select_all_meshes()
        for ob in objs:
            if ob.data.materials:
                # print(ob.name)
                # print(object_materials[ob.name])
                ob.data.materials[0] = object_materials[ob.name] 
            else:
                ob.data.materials.append(object_materials[ob.name])
        
            
def apply_mat(mat):
    """
    Apply material to object

    Args:
        mat (bpy.types.Material): apply the material to the object
    """
    objects = select_all_meshes()
    for obj in objects:
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    
def output_files(suffix,formats, glb, file_locations):
    """
    Output files depending on a provided list of formats and filename suffixes.

    Args:
        suffix (str): suffix to append to the output mesh file
        formats (list of str): list of formats to export
        glb (bool): whether to export the glb format (generally True)
        file_locations (object): an object containing urls and filenames for input/output
    """
    output_dir = file_locations.output_dir
    filestem = file_locations.filestem
    extension = file_locations.extension
    source_path = file_locations.source_path

    stem = output_dir + filestem + suffix
    
    output_separate_dir = './output/LOD/'
    output_LOD_dir = os.path.join(output_separate_dir, 'LOD' + suffix)

    if not os.path.exists(output_LOD_dir):
        os.makedirs(output_LOD_dir)
    stem_separate = os.path.join(output_LOD_dir, filestem)

    if glb:
        bpy.ops.export_scene.gltf(filepath=stem, export_format='GLB', export_cameras=False)
        bpy.ops.export_scene.gltf(filepath=stem_separate, export_format='GLB', export_cameras=False)
    for format in formats:
        out_path = stem + format
        if format == ".fbx":            
            # case ".fbx":
                bpy.ops.export_scene.fbx(filepath=out_path, path_mode="COPY", embed_textures=True)         
           
def create_wire_mat():
    """
    Create the wireframe materials

    Returns:
        mat (bpy.types.Material): the created material
    """
    # define a new material that will use the node setup
    mat_name = "wire_solid"
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True

    # clear any existing nodes and connections
    if mat.node_tree:
        mat.node_tree.links.clear()
        mat.node_tree.nodes.clear()

    # define the shader nodes that will be used
    nodes = mat.node_tree.nodes
    output = nodes.new(type='ShaderNodeOutputMaterial')
    wireframe = nodes.new(type='ShaderNodeWireframe')
    diffuse = nodes.new(type='ShaderNodeBsdfDiffuse')


    shader = nodes.new(type='ShaderNodeBsdfPrincipled')
    shader.inputs[0].default_value = (0.2,0.2,0.2, 1)
    shader.inputs[7].default_value = 0.5
    shader.inputs[6].default_value = 0
    shader.inputs[9].default_value = 0.5

    mix = nodes.new(type='ShaderNodeMixShader')
    
    wireframe.use_pixel_size = True
    wireframe.inputs[0].default_value =1
    
    diffuse.inputs[0].default_value = (0,0,0,1)

    # link the nodes together to make the material
    links = mat.node_tree.links
    links.new(wireframe.outputs[0], mix.inputs[0])
    links.new(shader.outputs[0], mix.inputs[1])
    links.new(diffuse.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs[0])
    
    return mat

 
def setup_scene(hdr):
    """
    Set up the rendering

    Args:
        hdr (str): url to the image used for hdr lighting
    """

    context.scene.render.resolution_percentage = 150

    # set up the renderer
    bpy.data.scenes["Scene"].render.engine = 'CYCLES'
    context.scene.cycles.samples = 128

    # set the size of the camera frame
    context.scene.render.resolution_x = 500
    context.scene.render.resolution_y = 500

    bpy.data.scenes["Scene"].camera.location = [0, -10, 0]
    bpy.data.scenes["Scene"].camera.rotation_mode = 'XYZ'
    bpy.data.scenes["Scene"].camera.rotation_euler = [math.radians(90), 0, 0]
    bpy.data.scenes["Scene"].camera.lock_rotation[0] = True
    bpy.data.scenes["Scene"].camera.lock_rotation[1] = True
    bpy.data.scenes["Scene"].camera.lock_rotation[2] = True

    # adjust the clipping plane for large objects
    context.scene.camera.data.clip_start = 0.01
    context.scene.camera.data.clip_end = 1000000
    context.scene.render.use_persistent_data = True
    
    # sets up the HDR lighting with a custom image and rotation
    setup_lighting(hdr)
 
    
def render_png(suffix, file_locations):
    """
    Render the PNG with the provided suffix

    Args:
        suffix (str): suffix to append to the filename
        file_locations (object): an object containing urls and filenames for input/output
    """
    output_dir = file_locations.output_dir
    filestem = file_locations.filestem

    print("filestem: ", filestem)

    out_path = output_dir + filestem + suffix + "_tmb_NIH3D.png"
    bpy.data.scenes["Scene"].render.image_settings.file_format = 'PNG'
    bpy.data.scenes["Scene"].render.filepath = out_path
    bpy.ops.render.render(write_still=1)
    
def setup_lighting(hdr):
    """
    Setup the lighting environment

    Args:
        hdr (str): path to the texture used for lighting
    """

    # Get the environment node tree of the current scene
    node_tree = bpy.data.scenes["Scene"].world.node_tree
    tree_nodes = node_tree.nodes

    # Clear all nodes
    tree_nodes.clear()

    # Add Background node
    node_background = tree_nodes.new(type='ShaderNodeBackground')

    # Add Environment Texture node
    node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
    node_texture = tree_nodes.new("ShaderNodeTexCoord")
    node_mapping = tree_nodes.new("ShaderNodeMapping")

    # Load and assign the HDR image to the node property
    node_environment.image = bpy.data.images.load(hdr)  # Relative path

    # Add Output node
    node_output = tree_nodes.new(type='ShaderNodeOutputWorld')

    # Link all nodes
    links = node_tree.links
    links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
    links.new(node_background.outputs["Background"], node_output.inputs["Surface"])
    links.new(node_texture.outputs[0], node_mapping.inputs[0])
    links.new(node_mapping.outputs[0], node_environment.inputs[0])

    bpy.context.scene.cycles.use_fast_gi = True
    bpy.context.scene.world.light_settings.ao_factor = 1
    bpy.context.scene.world.light_settings.distance = 50

    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[1].default_value = 4.0
    bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[1] = math.radians(-25.0)
    bpy.data.worlds["World"].node_tree.nodes["Mapping"].inputs[2].default_value[2] = math.radians(75.0)

    # Set the environment to transparent
    context.scene.render.film_transparent = True

    # Set the png color space so it can render the transparency
    context.scene.render.image_settings.color_mode = 'RGBA'

    
def decimate(value):
    """
    Decimate the mesh

    Args:
       value (float): decimation ratio to use for decimation
    """
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.decimate(ratio=value)
    
 
def check_manifold(repair, append, repair_type):
    """
    Check whether ANY object in the file is non-manifold

    Args:
        repair (bool): whether or not to conduct repair on the mesh
        append (bool): whether or not to append results to results
        repair_type (str): type of repair to run.  Either full 3D print clean-up or simple doubles removal.

    Returns:
       manifold_results (list of str): list of object names that are not manifold
    """
    if repair_type != "none":
        bpy.ops.object.mode_set(mode='OBJECT')
    objs = select_all_meshes()
    bpy.ops.object.select_all(action='DESELECT')
    manifold_results = []
    for obj in objs:
        bm = mesh_helpers.bmesh_copy_from_object(obj, transform=False, triangulate=False)
        edges_non_manifold = array.array('i', (i for i, ele in enumerate(bm.edges) if not ele.is_manifold))
        if (len(edges_non_manifold)) != 0:
            if append:
                manifold_results.append(obj.name)
            if repair:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                print("%s is not manifold.  Clean-up" %obj.name)
                if repair_type == "print":
                    bpy.ops.mesh.print3d_clean_non_manifold()
                elif repair_type == "doubles":
                    clean_up()
    return manifold_results


def output_results(output_root):
    """
    Output reporting that was collecting throughout processing.

    Will create a csv file that is populated with each model iteration.  This is not needed for the NIH 3D workflows,
    it is used for internal testing.

    Args:
        output_root (str): directory for the output files
    """
    
    csv_path = output_root + "analyze_inputs.csv"
    
    df = pd.DataFrame(list(zip(df_filename,  df_stpolys, df_polys80, df_polys40, df_polys20, df_time, df_manifold, df_intersections)),
        columns=['Filename', 'Start Polys', 'Polys 80%', 'Polys 40%', 'Polys 20%','Elapsed Time', 'Non-Manifold Parts', 'Self Intersections?'])
    df.to_csv(csv_path)
    
    print(df)
    
def output_export_results(output_root):
    """
    Output of analysis done on exported files

    Will create a csv file that is populated with each model iteration.  This is not needed for the NIH 3D workflows,
    it is used for internal testing.

    Args:
        output_root (str): directory for the output files
    """
    csv_path = output_root + "analyze_outputs.csv"
    
    df = pd.DataFrame(list(zip(ex_filename, ex_polys, ex_manifold, ex_intersection)),
        columns=['Filename', 'Polycount', 'Non-Manifold Parts', 'Self Intersecting Parts'])
    df.to_csv(csv_path)
    
    print(df)
    

def setup_logging(output_root):
    """
    Logging system

    Args:
        output_root (str): directory for the output files
    """
    now = datetime.now()
    dt_string = now.strftime("%H%M%S")
    log_location = output_root + 'output_' + dt_string + '.log'
    logging.basicConfig(filename=log_location, encoding='utf-8', level=logging.DEBUG)

def convert_time(seconds):
    """convert time from seconds to hrs:min:sec"""
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    min = seconds // 60
    seconds %= 60
   
    return "%02d:%02d:%02d" % (hour, min, seconds)

def main(repair_type):
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

    # input_dir = "D:\\hra-organ-gallery-assets\\Kristen LOD Processing\\INPUT\\"
    # hdr = 'D:\\hra-organ-gallery-assets\\Kristen LOD Processing\\studio_small_01_4k.exr'
    input_dir = "./downloaded_organs/"
    hdr = "./studio_small_01_4k.exr"

    paths = []
    extensions = ['glb']
    for path, subdirs, files in os.walk(input_dir):
        for name in files:
            res = list(filter(name.endswith, extensions)) != []
            if res:
                paths.append(os.path.join(path, name))

    # print(paths)
    # output_root = 'D:\\hra-organ-gallery-assets\\Kristen LOD Processing\\OUTPUT\\Doubles\\'
    output_root = './output/doubles/'

    # Ensure the input and output directories exist
    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        return

    if not os.path.exists(output_root):
        os.makedirs(output_root)

    setup_logging(output_root)

    for i in range(len(paths)):
        #remove default objects and create new camera
        clean_scene()
        camera_data = bpy.data.cameras.new(name='Camera')
        camera_object = bpy.data.objects.new('Camera', camera_data)
        bpy.context.scene.collection.objects.link(camera_object)
        bpy.context.scene.camera = camera_object
 
        # get split up the path into variables to use downstream.  I'm using globals which is probably naughty, but worked
        # for testing in Blender
        # paths[i] = paths[i].lower()

        #path to the source file
        source_path = paths[i]
        split_path = os.path.splitext(source_path)
        
        #extension for the source file
        extension = split_path[1]
        
        #store the filename without the extension
        filestem = os.path.split(split_path[0])[1]
        
        #store the complete filename
        filename = filestem + extension
        
        #output directory for output files (testing only)

        output_dir = output_root + filename + '/'
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

        logging.info('processing: ' + paths[i])

        file_locations = FileLocations(filename, filestem, extension, source_path, output_dir, output_root, hdr)

        #process the files
        mesh_process(file_locations, repair_type)
        

        #output results for local test review
        output_results(output_root)
        
def analyze_outputs(repair_type):
    """
    Will analyze the output meshes

    Different repair types can be set for the process:


    Args:
        repair_type (str): Set to "none" so will not try any repair during the analsis
    """

    
    input_dir = './models/doubles/'
    output_root = './models/doubles/'
    hdr = './studio_small_01_4k.exr'
    
    
    paths = []
    extensions = ['fbx']
    for path, subdirs, files in os.walk(input_dir):
        for name in files:
            res = list(filter(name.endswith, extensions)) != []
            if res:
                paths.append(os.path.join(path, name))
                
    for i in range(len(paths)):
        #remove default objects and create new camera
        clean_scene()
        
        # get split up the path into variables to use downstream.  I'm using globals which is probably naughty, but worked
        # for testing in Blender
        paths[i] = paths[i].lower()

        #path to the source file
        source_path = paths[i]
        split_path = os.path.splitext(source_path)
        
        #extension for the source file
        extension = split_path[1]
        
        #store the filename without the extension
        filestem = os.path.split(split_path[0])[1]
        
        #store the complete filename
        filename = filestem + extension
        
        output_dir = output_root + filename + '/'
        
        file_locations = FileLocations(filename, filestem, extension, source_path, output_dir, output_root, hdr)
            
        #import the source file
        ex_filename.append(file_locations.filename)
        print("Import File: %s" %file_locations.filename)

        bpy.ops.import_scene.fbx(filepath=source_path)

        objs = select_all_meshes()
        #analyze the mesh to determine the attributes of the input file
        #We should return this values as attributes of the input file when integrated into the NIH 3D workflows.
        polys, verts, manifold, intersections = analyze_mesh(False, repair_type)
        
        print("Analyze mesh...")
        print("Polys: %s" %polys)
        print("Non-Manifold Objects: %s" %manifold)
        print("Objects with self-intersections: %s" %intersections)
        
        ex_polys.append(polys)
        ex_manifold.append(manifold)
        ex_intersection.append(intersections)
        
        output_export_results(output_root)
        
   
# main("doubles")

# analyze_outputs("none")