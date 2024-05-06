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
        ```bash
        sudo snap install blender --classic
        ```
    - MacOS:
        1. Please follow instructions at https://docs.blender.org/manual/en/latest/getting_started/installing/macos.html 
        2. Add blender to path: https://docs.blender.org/manual/en/latest/advanced/command_line/launch/macos.html
    - Windows:
        1. Please follow instructions at https://docs.blender.org/manual/en/latest/getting_started/installing/windows.html
        2. Add blender to path: https://docs.blender.org/manual/en/latest/advanced/command_line/launch/windows.html
    

2. Install Pandas in Blender Python
    - Linux & MacOS 
        ```bash
        blender --background --python install_package.py
        ```
    - Windows (to be finished)

## Usage 

```bash
python3 glb_preprocessor.py input_glb_path output_glb_path
```
e.g., 
```bash
python3 glb_preprocessor.py ../model/3d-vh-f-blood-vasculature.glb ../output/3d-vh-f-blood-vasculature.glb
```
