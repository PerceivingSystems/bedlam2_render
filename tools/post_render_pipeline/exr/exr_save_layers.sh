#/bin/bash
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Extract layers from multilayer EXR
# + Unreal meta information will be preserved in generated PNG/EXR images
# + Existing target layers will be skipped
# + Can convert single EXR file or use multiprocessing for EXR directory
#
# Requirements:
# + oiiotool (sudo apt install openimageio-tools, 2.2.18+)
# + GNU parallel (sudo apt install parallel, 20210822)
#

# Export multilayer exr to individual layers using oiiotool
# Sample input path: C:\bedlam2\images\testrender\exr\seq_000000\seq_000000_0000.exr
process_exr() {
    local input_exr=$1
    local output_prefix=$(basename "${input_exr%.exr}")
    local sequence_name=$(basename "$(dirname "$input_exr")")
    local output_root="$(dirname "$(dirname "$(dirname "$input_exr")")")/exr_layers"
    local NUM_THREADS=1 # Default setting of 0 uses all cores and is slower
    local COLORCONVERT="--colorconvert linear sRGB"

    echo "Processing: '$input_exr'"

    # Image, 8-bit RGB (sRGB)
    local type=image
    local output_dir="${output_root}/${type}/${sequence_name}"
    if [ ! -d "$output_dir" ]; then
        mkdir -p $output_dir
    fi
    local output="${output_dir}/${output_prefix}_${type}.png"
    if [ -f "$output" ]; then
        echo "  Skipping. File exists: '$output'"
    else
        oiiotool --threads $NUM_THREADS "$input_exr" --ch R,G,B $COLORCONVERT -o "$output"
    fi

    # Optional: CameraNormal, 8-bit RGB (linear)
    type=cameranormal
    channel_name="FinalImageMovieRenderQueue_CameraNormal"
    if oiiotool --info -v "$input_exr" | grep -Fq "$channel_name"; then
        output_dir="${output_root}/${type}/${sequence_name}"
        if [ ! -d "$output_dir" ]; then
            mkdir -p $output_dir
        fi
        output="${output_dir}/${output_prefix}_${type}.png"
        if [ -f "$output" ]; then
            echo "  Skipping. File exists: '$output'"
        else
            oiiotool --threads $NUM_THREADS "$input_exr" --ch ${channel_name}.R,${channel_name}.G,${channel_name}.B -o "$output"
        fi
    fi

    # Optional: WorldNormal, 8-bit RGB (linear)
    type=worldnormal
    channel_name="FinalImageMovieRenderQueue_WorldNormal"
    if oiiotool --info -v "$input_exr" | grep -Fq "$channel_name"; then
        output_dir="${output_root}/${type}/${sequence_name}"
        if [ ! -d "$output_dir" ]; then
            mkdir -p $output_dir
        fi
        output="${output_dir}/${output_prefix}_${type}.png"
        if [ -f "$output" ]; then
            echo "  Skipping. File exists: '$output'"
        else
            oiiotool --threads $NUM_THREADS "$input_exr" --ch ${channel_name}.R,${channel_name}.G,${channel_name}.B -o "$output"
        fi
    fi

    # WorldDepth, EXR (16-bit float)
    type=depth
    output_dir="${output_root}/${type}/${sequence_name}"
    if [ ! -d "$output_dir" ]; then
        mkdir -p $output_dir
    fi
    output="${output_dir}/${output_prefix}_${type}.exr"
    if [ -f "$output" ]; then
        echo "  Skipping. File exists: '$output'"
    else
        oiiotool --threads $NUM_THREADS "$input_exr" --ch FinalImageMovieRenderQueue_WorldDepth.R --chnames Depth -d half -o "$output"
    fi
}

###############################################################################
# Main
###############################################################################

if [ -z "$1" ]; then
    script_name=$(basename "$0")
    echo "Usage:"
    echo "  Single file: $script_name INPUT_MULTILAYER_EXR"
    echo "  Directory:   $script_name INPUT_MULTILAYER_EXR_DIR NUM_PROCESSES"
    echo "               Example: $script_name /path/to/multilayer/exr/dir/ 12"
    exit 1
fi

input_exr=$1

if [ -z "$2" ]; then
    # Single file processing
    echo "Input multilayer EXR: '$input_exr'"
    process_exr "$input_exr"
else
    num_processes=$2
    echo "Multiprocessing mode: $2 processes"
    echo "Input multilayer EXR directory: '$input_exr'"

    # Export process function so that parallel can access it
    export -f process_exr

    # Use GNU parallel for multiprocess conversion of target file list.
    # Exit when first job fails but let running jobs complete.
    # Note: Passing filenames via argument fails with "argument list too long" error if there are too many files
    #         parallel --halt soon,fail=1 -j "$num_processes" process_exr ::: "$exr_files"
    find "$input_exr" -name "*.exr" | parallel --halt soon,fail=1 -j "$num_processes" process_exr {}
fi

echo "EXR layer extraction finished. Status: $?" 1>&2
