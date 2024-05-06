import sys
import os
import subprocess
import argparse


blender_python_dir = sys.exec_prefix
blender_python_bin = os.path.join(blender_python_dir, 'bin')
python_path = ""

for exe in os.listdir(blender_python_bin):
    if exe.startswith('python'):
        python_path = os.path.join(blender_python_bin, exe)
        break

if not python_path:
    print('Blender Python does not exist')

print('Blender Python path: ', python_path)
subprocess.call([python_path, "-m", "pip", "install", "pandas"])