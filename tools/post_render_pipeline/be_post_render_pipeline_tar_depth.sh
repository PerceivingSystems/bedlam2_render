#!/bin/bash
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
#
# Post render pipeline for BEDLAM renderings depth/mask pass.
#
# Generate tar files on target directory root subfolder.
#
# Requirements:
#   + xxhsum (0.8.1+, https://github.com/Cyan4973/xxHash)
#

function archive_exr_meta () {
    mkdir -p "$TARGET_DIR/ground_truth"
    if [ -z "$1" ]; then
        EXR_TYPE=
    else
        EXR_TYPE="_$1"
    fi

    TARGET_TAR="${TARGET_DIR}/ground_truth/${DIRNAME}_gt_centersubframe_exr${EXR_TYPE}_meta.tar.gz"

    echo "Generating archive: '$TARGET_TAR'"

    if [ -f "$TARGET_TAR" ]; then
        echo "  Skipping: File exists"
    else
        # Check if camera animations config file is existing
        CAMERA_ANIMATIONS_CONFIG="$DIRNAME/be_camera_animations.json"
        if [ ! -f "$RENDER_OUTPUT_ROOT/$CAMERA_ANIMATIONS_CONFIG" ]; then
            CAMERA_ANIMATIONS_CONFIG=
        fi

        CAMERA_ANIMATIONS_DEPTH_CONFIG="$DIRNAME/be_camera_animations_depth.json"
        if [ ! -f "$RENDER_OUTPUT_ROOT/$CAMERA_ANIMATIONS_DEPTH_CONFIG" ]; then
            CAMERA_ANIMATIONS_DEPTH_CONFIG=
        fi

        tar -z -c -f "$TARGET_TAR" --verbose --directory="$RENDER_OUTPUT_ROOT" "$DIRNAME/be_seq.csv" $CAMERA_ANIMATIONS_CONFIG $CAMERA_ANIMATIONS_DEPTH_CONFIG "$DIRNAME/ground_truth/meta_exr${EXR_TYPE}/"
        if [ $? -eq 0 ]; then
            echo "Archive created successfully"
        else
            echo "Failed to create archive"
            exit 1
        fi

        TARGET_TAR_XXHSUM="$TARGET_TAR.xxh128"
        echo "  Generating XXH3 checksum: '$TARGET_TAR_XXHSUM'"
        xxhsum -H128 "$TARGET_TAR" | tr -d "\r" | tee "$TARGET_TAR_XXHSUM"  # Replace CRLF from xxhsum windows executable with LF
        sed --in-place -r "s/  .+\//  /" "$TARGET_TAR_XXHSUM" # Remove absolute path prefix from xxh128 file
    fi
}

function archive_exr_meta_csv () {
    mkdir -p "$TARGET_DIR/ground_truth"
    if [ -z "$1" ]; then
        EXR_TYPE=
    else
        EXR_TYPE="_$1"
    fi

    TARGET_TAR="${TARGET_DIR}/ground_truth/${DIRNAME}_gt_centersubframe_exr${EXR_TYPE}_meta_csv.tar.gz"

    echo "Generating archive: '$TARGET_TAR'"

    if [ -f "$TARGET_TAR" ]; then
        echo "  Skipping: File exists"
    else
        # Check if camera animations config file is existing
        CAMERA_ANIMATIONS_CONFIG="$DIRNAME/be_camera_animations.json"
        if [ ! -f "$RENDER_OUTPUT_ROOT/$CAMERA_ANIMATIONS_CONFIG" ]; then
            CAMERA_ANIMATIONS_CONFIG=
        fi

        CAMERA_ANIMATIONS_DEPTH_CONFIG="$DIRNAME/be_camera_animations_depth.json"
        if [ ! -f "$RENDER_OUTPUT_ROOT/$CAMERA_ANIMATIONS_DEPTH_CONFIG" ]; then
            CAMERA_ANIMATIONS_DEPTH_CONFIG=
        fi

        tar -z -c -f "$TARGET_TAR" --verbose --directory="$RENDER_OUTPUT_ROOT" "$DIRNAME/be_seq.csv" $CAMERA_ANIMATIONS_CONFIG $CAMERA_ANIMATIONS_DEPTH_CONFIG "$DIRNAME/ground_truth/meta_exr${EXR_TYPE}_csv/"
        if [ $? -eq 0 ]; then
            echo "Archive created successfully"
        else
            echo "Failed to create archive"
            exit 1
        fi

        TARGET_TAR_XXHSUM="$TARGET_TAR.xxh128"
        echo "  Generating XXH3 checksum: '$TARGET_TAR_XXHSUM'"
        xxhsum -H128 "$TARGET_TAR" | tr -d "\r" | tee "$TARGET_TAR_XXHSUM"  # Replace CRLF from xxhsum windows executable with LF
        sed --in-place -r "s/  .+\//  /" "$TARGET_TAR_XXHSUM" # Remove absolute path prefix from xxh128 file
    fi
}


function archive_dir () {
    SUBDIR=$1
    TYPE=$2
    SUBARCHIVES=$3

    mkdir -p "$TARGET_DIR/$SUBDIR"

    if [ -z "$SUBARCHIVES" ] ; then
        # Single tar archive
        TARGET_TAR="$TARGET_DIR/$SUBDIR/${DIRNAME}_$TYPE.tar"

        echo "Generating archive: '$TARGET_TAR'"

        if [ -f "$TARGET_TAR" ]; then
            echo "  Skipping: File exists"
        else
            tar -c -f "$TARGET_TAR" --verbose --directory="$RENDER_OUTPUT_ROOT" "$DIRNAME/$SUBDIR/"
            if [ $? -eq 0 ]; then
                echo "Archive created successfully"
            else
                echo "Failed to create archive"
                exit 1
            fi

            # xxh128
            TARGET_TAR_XXHSUM="$TARGET_TAR.xxh128"
            echo "  Generating XXH3 checksum: '$TARGET_TAR_XXHSUM'"
            xxhsum -H128 "$TARGET_TAR" | tr -d "\r" | tee "$TARGET_TAR_XXHSUM"  # Replace CRLF from xxhsum windows executable with LF
            sed --in-place -r "s/  .+\//  /" "$TARGET_TAR_XXHSUM" # Remove absolute path prefix from xxh128 file
        fi
    else
        # Generate multiple subarchives
        pushd "$RENDER_OUTPUT_ROOT"
        sequence_dirs=($DIRNAME/$SUBDIR/*/)
        popd
        num_sequence_dirs=${#sequence_dirs[@]}
        dirs_per_tar_file=$((($num_sequence_dirs + $SUBARCHIVES - 1) / $SUBARCHIVES))
        echo "  Directories per subarchive: $dirs_per_tar_file"

        for i in $(seq 0 $(($SUBARCHIVES - 1))); do
            TARGET_TAR="$TARGET_DIR/$SUBDIR/${DIRNAME}_$TYPE.$i.tar"
            echo "Generating archive: '$TARGET_TAR'"

            if [ -f "$TARGET_TAR" ]; then
                echo "  Skipping: File exists"
            else
                start_index=$(($i * $dirs_per_tar_file))
                slice_files=("${sequence_dirs[@]:$start_index:$dirs_per_tar_file}")

                tar -c -f "$TARGET_TAR" --verbose --directory="$RENDER_OUTPUT_ROOT" "${slice_files[@]}"
                if [ $? -eq 0 ]; then
                    echo "Archive created successfully"
                else
                    echo "Failed to create archive"
                    exit 1
                fi

                # xxh128
                TARGET_TAR_XXHSUM="$TARGET_TAR.xxh128"
                echo "  Generating XXH3 checksum: '$TARGET_TAR_XXHSUM'"
                xxhsum -H128 "$TARGET_TAR" | tr -d "\r" | tee "$TARGET_TAR_XXHSUM"  # Replace CRLF from xxhsum windows executable with LF
                sed --in-place -r "s/  .+\//  /" "$TARGET_TAR_XXHSUM" # Remove absolute path prefix from xxh128 file
            fi
        done

    fi

}

######################################################################
# Main
######################################################################

echo "Usage: $0 RENDER_OUTPUT_DIRECTORY TARGET_ROOT [NUM_TARFILES]"

if [ -z "$1" ] ; then
    exit 1
fi

if [ -z "$2" ] ; then
    exit 1
fi

NUM_TARFILES=10
if [ -n "$3" ] ; then
    NUM_TARFILES=$3
fi

RENDER_OUTPUT_DIRECTORY=${1%/}
RENDER_OUTPUT_ROOT=$(dirname "$RENDER_OUTPUT_DIRECTORY")
TARGET_ROOT=${2%/}
DIRNAME=$(basename "$RENDER_OUTPUT_DIRECTORY")
TARGET_DIR="$TARGET_ROOT/$DIRNAME"
echo "Render output directory: '$RENDER_OUTPUT_DIRECTORY'"
echo "Target output directory: '$TARGET_DIR'"
mkdir -p "$TARGET_DIR"

# Depth and masks
TYPE="exr_depth"
if [ -d "$RENDER_OUTPUT_DIRECTORY/$TYPE/" ]; then
    # EXR depth meta JSON information including camera pose
    archive_exr_meta depth
    # Camera ground truth CSV generated from EXR depth meta JSON
    archive_exr_meta_csv depth

    archive_dir $TYPE $TYPE $NUM_TARFILES
fi

# Optional: blacklist
if [ -f "$RENDER_OUTPUT_DIRECTORY/blacklist.txt" ]; then
    echo "Copying blacklist.txt"
    cp "$RENDER_OUTPUT_DIRECTORY/blacklist.txt" "$TARGET_DIR/"
fi

exit 0
