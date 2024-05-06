import argparse
import subprocess


parser = argparse.ArgumentParser(description='Python wrapper for Blender')
parser.add_argument('input_glb_path', help='input glb file path')
parser.add_argument('output_glb_path', help='output glb file path')
args = parser.parse_args()

input_glb_path = args.input_glb_path
output_glb_path = args.output_glb_path

cmd = ['blender', '--background', '--python', 'single_organ_reduction.py', '--', '-input_file_path', input_glb_path, '-lod', 100, output_glb_path]

print(" ".join(cmd))
subprocess.run(cmd)

