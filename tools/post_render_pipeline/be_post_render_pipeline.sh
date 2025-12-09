#/bin/bash
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Post render pipeline for BEDLAM2 image EXR (camera ground truth) and depth pass EXR renderings
#
# + Remove warmup frames from rendered image folders
# + Generate H.264 .mp4 movies for rendered sequences
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

echo "Usage: $0 render_output_directory landscape|portrait [extract_layers] [extract_masks]"

framerate=30

if [ $# -lt 2 ] ; then
    exit 1
fi
render_output_directory=$1

orientation=$2
if [ "$orientation" != "landscape" ] && [ "$orientation" != "portrait" ]; then
    echo "Invalid orientation mode: '$orientation'"
    exit 1
fi

rotate=
if [ "$orientation" = "portrait" ]; then
    rotate="rotate"
fi

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
echo "Orientation mode: $orientation"
echo "Movie framerate: $framerate"
echo "Extract EXR layers: $extract_layers"
echo "Extract masks from EXR depth pass: $extract_masks"

# Check for EXR+PNG render output
png_folder="${render_output_directory%/}/png/"
exr_image_folder="${render_output_directory%/}/exr_image/"
if [ -d "$exr_image_folder" ]; then
    echo "INFO: exr_image directory detected: $exr_image_folder"

    # Check if EXR was rendered with BEDLAM MRQ plugin for proper center subframe ground truth
    echo "  Checking if EXR metadata contains subframe ground truth information (rendered with BEDLAM MRQ plugin)"
    exr_testfile=$(find "$exr_image_folder" -type f -name "*_0000.exr" | head -n 1)
    echo "    Testfile: $exr_testfile"
    exr_token="unreal/camera/bedlam"
    result=$(exrheader "$exr_testfile" | grep -m 1 "$exr_token") # check for BEDLAM tokens in EXR metadata
    if [ $? -ne 0 ]; then
        echo "ERROR: Cannot find BEDLAM token in EXR: '$exr_token'"
        echo "EXR data was not rendered with BEDLAM MRQ plugin. Aborting."
        exit 1
    else
        echo "    [OK]"
    fi

    echo "  Moving existing PNG files to png/ folder"
    echo $png_folder
    if [ ! -d "$png_folder" ]; then
        echo "  Creating png image folder: $png_folder"
        mkdir -p "$png_folder"
    fi
    echo "  Moving PNG images from exr_image/ to png/"
    for source_dir in "${exr_image_folder%/}"/*; do
        sequence_name=$(basename "$source_dir")
        echo "  $sequence_name"
        target_dir="${png_folder}$sequence_name/"
        mkdir -p "${target_dir}"
        mv "${source_dir}"/*.png "$target_dir"
    done
fi

if [ ! -d "$png_folder" ]; then
    echo "ERROR: PNG image directory not existing: '$png_folder'"
    exit 1
fi

exr_folder="${render_output_directory%/}/exr_depth/"
if [ ! -d "$exr_folder" ]; then
    echo "WARNING: multilayer EXR (depth/mask/image/gt) directory not existing: '$exr_folder'"
fi

# Delete all warmup frames (images with negative frame numbers)
if [ -d "$png_folder" ]; then
echo "Deleting warmup frames: '$png_folder'"
find "$png_folder" -maxdepth 2 -name "*-????.png" -type f -delete
fi

if [ -d "$exr_image_folder" ]; then
echo "Deleting warmup frames: '$exr_image_folder'"
find "$exr_image_folder" -maxdepth 2 -name "*-????.exr" -type f -delete
fi

if [ -d "$exr_folder" ]; then
echo "Deleting warmup frames: '$exr_folder'"
find "$exr_folder" -maxdepth 2 -name "*-????.exr" -type f -delete
fi

if [ -d "$png_folder" ]; then
num_png_sequences=$(ls -1 $png_folder | wc -l)
num_png_images=$(find $png_folder -type f -name "*.png" | wc -l)
echo "Number of rendered png buffer sequences: $num_png_sequences [Images: $num_png_images]"
fi

if [ -d "$exr_image_folder" ]; then
num_exr_sequences=$(ls -1 $exr_image_folder | wc -l)
num_exr_images=$(find $exr_image_folder -type f -name "*.exr" | wc -l)
echo "Number of rendered exr image sequences: $num_exr_sequences [Images: $num_exr_images]"
fi

if [ -d "$exr_folder" ]; then
num_exr_sequences=$(ls -1 $exr_folder | wc -l)
num_exr_images=$(find $exr_folder -type f -name "*.exr" | wc -l)
echo "Number of rendered multilayer EXR (depth/mask/image/gt) sequences: $num_exr_sequences [Images: $num_exr_images]"
fi

read -p "Continue (y/n)?" answer
if [ ! "$answer" = "y" ]; then
    exit 1
fi

# Extract EXR image render camera ground truth
if [ -d "$exr_image_folder" ]; then
    echo "Extracting EXR camera ground truth information"
    source "$venv_path/bin/activate"
    ./exr/exr_save_ground_truth.py "$exr_image_folder" meta_exr 16 > /dev/null
    deactivate
    echo "Generating ground truth CSV from EXR JSON"
    ./exr/exr_gt_json_to_csv.py "$render_output_directory" meta_exr > /dev/null
fi

# Generate movies
movie_folder="${render_output_directory%/}/mp4/"
echo "Generating sequence movies (H.264 .mp4): '$movie_folder'"
python3 ./create_movies_from_images.py "$png_folder" "$movie_folder" $framerate $rotate

if [ -d "$exr_image_folder" ]; then
    # Generate overview images
    echo "Generating overview images"
    ./analysis/be_overview_images.py "$render_output_directory" $rotate

    # Generate plots
    echo "Generating camera overview plots"
    ./analysis/be_plot_camera_analysis.py "$render_output_directory"
fi

# Extract EXR depth render camera ground truth
if [ -d "$exr_folder" ]; then
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
fi
