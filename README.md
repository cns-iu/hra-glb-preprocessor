# hra-glb-preprocessor
Make meshes manifold and filling holes. Generate OFF file for a single mesh from GLB 

**Version:** 1.0.0

**Release date:** 15 June 2024

## Overview:
hra-glb-preprocessor project includes:
1. Preprocess (fix non-manifold meshes and filling holes) 3D models using Blender Python API. 

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

```bash
python3 glb_preprocessor.py input_glb_path output_glb_path
```
e.g., 
```bash
python3 glb_preprocessor.py ../model/3d-vh-f-blood-vasculature.glb ../output/3d-vh-f-blood-vasculature.glb
```
