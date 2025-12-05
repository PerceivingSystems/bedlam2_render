#/bin/bash
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Post render pipeline for separate BEDLAM EXR depth pass render
#
# + Remove warmup frames from rendered image folders
#
# Requirements:
#
#   Command-line tools
#   + exrheader (openexr package)
#
#   Python venv:
#   + numpy 1.24.2+
#   + opencv-python-headless 4.7.0.72+
#   + OpenEXR 1.3.9+
#
venv_path="$HOME/.virtualenvs/openexr"

echo "Usage: $0 render_output_directory"

if [ $# -lt 1 ] ; then
    exit 1
fi
render_output_directory=$1

echo "Processing render directory: '$render_output_directory'"

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
