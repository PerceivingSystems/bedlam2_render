#/bin/bash
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Post render pipeline for separate BEDLAM2 EXR depth pass render
#
# + Remove warmup frames from rendered image folders
#
# Requirements:
#
#   Command-line tools
#   + exrheader (openexr package)
#
#   Python venv:
#   + numpy 2.2.6
#   + opencv-python-headless 4.12.0.88
#   + OpenEXR 3.4.4
#
#   + if you use extract_layers mode:
#     + see exr/exr_save_layers.sh for additional requirements
#
venv_path="$HOME/.virtualenvs/bedlam2"

echo "Usage: $0 render_output_directory [extract_layers] [extract_masks]"

if [ $# -lt 1 ] ; then
    exit 1
fi
render_output_directory=$1

extract_layers=0
extract_masks=0
# Iterate over all arguments
for arg in "$@"; do
    if [ "$arg" == "extract_layers" ]; then
        extract_layers=1
    elif [ "$arg" == "extract_masks" ]; then
        extract_masks=1
    fi
done

echo "Processing render directory: '$render_output_directory'"
echo "Extract EXR layers: $extract_layers"
echo "Extract masks from EXR depth pass: $extract_masks"

exr_folder="${render_output_directory%/}/exr_depth/"
if [ ! -d "$exr_folder" ]; then
    echo "ERROR: multilayer EXR (depth/mask/image/gt) directory not existing: '$exr_folder'"
    exit 1
fi

# Delete all warmup frames (images with negative frame numbers)
echo "Deleting warmup frames: '$exr_folder'"
find "$exr_folder" -maxdepth 2 -name "*-????.exr" -type f -delete
num_exr_sequences=$(ls -1 $exr_folder | wc -l)
num_exr_images=$(find $exr_folder -type f -name "*.exr" | wc -l)
echo "Number of rendered multilayer EXR (depth/mask/image/gt) sequences: $num_exr_sequences [Images: $num_exr_images]"

read -p "Continue (y/n)?" answer
if [ ! "$answer" = "y" ]; then
    exit 1
fi

# Extract EXR depth render camera ground truth
echo "Extracting EXR depth camera ground truth information"
source "$venv_path/bin/activate"
./exr/exr_save_ground_truth.py "$exr_folder" meta_exr_depth 16 > /dev/null
deactivate
echo "Generating ground truth depth camera CSV from EXR depth JSON"
./exr/exr_gt_json_to_csv.py "$render_output_directory" meta_exr_depth > /dev/null

if [ "$extract_layers" -eq 1 ]; then
    echo "Extracting EXR layers to exr_layers/ folder"
    ./exr/exr_save_layers.sh "$exr_folder" 12 > /dev/null
fi

if [ "$extract_masks" -eq 1 ]; then
    echo "Extracting body segmentation masks to exr_layers/masks/ folder"
    ./exr/exr_save_masks.py "$exr_folder" 16 > /dev/null
fi
