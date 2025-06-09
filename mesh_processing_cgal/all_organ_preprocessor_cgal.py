import argparse
import json
import os
import subprocess

import requests
from glb_parser import glb_parser_all


# Naive Hashing for url
def convert_url_to_file(glb_url):
    parts = glb_url.split('/')
    return next((parts[i + 1] for i, part in enumerate(parts[:-1]) if part == 'ref-organ'), None)

# Get the latest version models
def download_model(glb_urls, output_folder):
    """A function to download GLB URLs
    """

    glb_urls = open(glb_urls).read().strip().split('\n');

    # Make folder for GLB files or check if already present
    os.makedirs(output_folder, exist_ok=True)

    # Get download URLs
    for glb_url in glb_urls:
        glb_file = convert_url_to_file(glb_url)
        if glb_file == None:
            print(glb_url, "looks wrong. skipping.")
            continue

        file_path = os.path.join(output_folder, glb_file + ".glb")
        
        # Already downloaded, skip it. 
        if os.path.exists(file_path):
            continue
        
        if glb_url:
            glb_response = requests.get(glb_url)
            
            # Download model
            if glb_response.status_code == 200:
                with open(file_path, "wb") as file:
                    file.write(glb_response.content)
                    print(f"Downloaded {glb_file}")


if __name__ == "__main__":
    # Use `argparse` to build URL
    parser = argparse.ArgumentParser(
        description="CGAL Preprocessor for GLB files")
    parser.add_argument("--urls", type=str,
                        help="File with a list of GLB URLs to download")
    parser.add_argument("--downloaded_dir", type=str,
                        help="Folder to save downloaded GLB files", default="downloaded_organs/")
    parser.add_argument("--preproceesed_models_stage_1", type=str,
                        help="Folder to save preprocessed GLB models from Stage 1", default="./downloaded_organs/")
    parser.add_argument("--output_off_model_dir", type=str,
                        help="Directory to the preprocessed OFF models", default="manifold_cgal/")
    parser.add_argument("--temp_plain_model_dir", type=str, help="Directory to the temp plain model directory", default="temp_plain_model_off/")
    args, unknown = parser.parse_known_args()

    # Download undownloaded models 
    glb_urls = args.urls
    downloaded_dir = args.downloaded_dir
    download_model(glb_urls, downloaded_dir)

    preproceesed_models_stage_1 = args.preproceesed_models_stage_1
    output_off_model_dir = args.output_off_model_dir
    temp_plain_model_dir = args.temp_plain_model_dir

    glb_parser_all(preproceesed_models_stage_1, temp_plain_model_dir)

    subprocess.run(['mesh_hole_filling', temp_plain_model_dir, output_off_model_dir])
