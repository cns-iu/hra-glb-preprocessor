# hra-glb-preprocessor

**Version:** 1.0.0

**Release date:** 15 June 2024

## Overview:
hra-glb-preprocessor project includes:
1. Preprocess (fix non-manifold meshes and filling holes) 3D models using Blender Python API.
2. Generate OFF file for a single mesh from GLB if needed. 

## Installation Instructions
1. Install Blender
    - Ubuntu:
        1. Please follow instructions at https://docs.blender.org/manual/en/latest/getting_started/installing/linux.html.
        2. Add blender to path: https://docs.blender.org/manual/en/latest/advanced/command_line/launch/linux.html
    - MacOS:
        1. Please follow instructions at https://docs.blender.org/manual/en/latest/getting_started/installing/macos.html 
        2. Add blender to path: https://docs.blender.org/manual/en/latest/advanced/command_line/launch/macos.html
    - Windows:
        1. Please follow instructions at https://docs.blender.org/manual/en/latest/getting_started/installing/windows.html
        2. Add blender to path:
           1. Find the directory where Blender is installed, e.g., [C:\Program Files\Blender Foundation\Blender\blender.exe]()
           2. Add both [C:\Program Files\Blender Foundation\Blender\blender.exe](), [C:\Program Files\Blender Foundation\Blender]() (Please replace the two paths using your blender installation path) to environment variable. Please see https://www.computerhope.com/issues/ch000549.htm if you are not sure how to add environment variables on Windows.
           3. Restart the cmd or powershell.
           4. Test by entering "blender" in cmd. If Blender is started automatically, the environment variables are successfully added.
    

2. Install Pandas in Blender Python
    - Linux & MacOS & Windows
        ```bash
        blender --background --python install_package.py
        ```

## Usage 
1. Change directory to mesh_processing_blender
   ```bash
   cd mesh_processing_blender
   ```
   
2. To pre-process a single model, run glb_preprocessor.py by specifying input_glb_path and output_glb_path  
    ```bash
    python3 glb_preprocessor.py input_glb_path output_glb_path
    ```
    e.g., 
    ```bash
    python3 glb_preprocessor.py ../model/3d-vh-f-blood-vasculature.glb ../output/3d-vh-f-blood-vasculature.glb
    ```
3. Download and pre-process all organ models
    ```bash
    python3 glb_preprocessor_all_organs.py --url url --downloaded_dir downloaded_dir --output_glb_model_dir preprocessed_glb_model_dir --output_off_model_dir preprocessed_off_model_dir
    ```
    There are three arguments:

    - **url** is the endpoint to download all the latest reference organ models; the default value is https://apps.humanatlas.io/api/v1/reference-organs.
    - **downloaded_dir** is the directory to cache all the models; the default value is downloaded_organs/.
    - **output_glb_model_dir** is the output diretory to store all the preprocessed GLB models; the default value is all_preprocessed_glb_models/.
    - **output_off_model_dir** is the output directory to store all the preprocessed OFF models, which are generated based on the GLB models; the default value is all_preprocessed_off_models.
    
    e.g., 
    ```bash
    python3 glb_preprocessor_all_organs.py --url https://apps.humanatlas.io/api/v1/reference-organs --downloaded_dir downloaded_folder/ --output_glb_model_dir all_preprocessed_glb_models/ --output_off_model_dir all_preprocessed_off_models/
    ```
