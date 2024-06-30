import os
import json
import argparse
import subprocess
import requests

# Naive Hashing for url
def convert_url_to_file(url):
    # Replace illegal chars using underscore
    illegal_chars = ['/', ':', '@', '&', '*']
    
    for c in illegal_chars:
        url = url.replace(c, '_')
    
    return url

# Get the latest version models
def download_model(api_url, output_folder):
    """A function to get download URLs for all 3D Reference Objects in the HRA
    """

    # send request
    response = requests.get(api_url).text
    data = json.loads(response)

    # Make folder for GLB files or check if already present
    os.makedirs(output_folder, exist_ok=True)

    # Get download URLs
    for organ in data:
        glb_url = organ['object']['file']
        file_name = convert_url_to_file(glb_url)
        file_path = os.path.join(output_folder, file_name)
        
        # Already downloaded, skip it. 
        if os.path.exists(file_path):
            continue
        
        if glb_url:
            glb_response = requests.get(glb_url)
            
            # Download model
            if glb_response.status_code == 200:
                with open(file_path, "wb") as file:
                    file.write(glb_response.content)
                    print(f"Downloaded {file_name}")


if __name__ == "__main__":
    # get data from HRA API endpoint
    endpoint = "https://apps.humanatlas.io/api/v1/reference-organs"

    # Use `argparse` to build URL
    parser = argparse.ArgumentParser(
        description="Download GLB files from CCF API")
    parser.add_argument("--url", type=str,
                        help="URL of the API", default=endpoint)
    parser.add_argument("--output-folder", type=str,
                        help="Folder to save downloaded GLB files", default="downloaded_organs/")
    parser.add_argument("--output_model_dir", type=str,
                        help="Directory to the preprocessed models", default="all_preprocessed_models/")
    args, unknown = parser.parse_known_args()

    # Download undownloaded models 
    api_url = args.url
    output_folder = args.output_folder
    download_model(api_url, output_folder)

    # The input model directory is the downloaded model directory
    input_model_dir = output_folder
    output_model_dir = args.output_model_dir
    cmd = ['blender', '--background', '--python', 'all_organs_preprocess.py', '--', '-input_model_dir', input_model_dir, '-output_model_dir', output_model_dir]

    print(" ".join(cmd))
    subprocess.run(cmd)