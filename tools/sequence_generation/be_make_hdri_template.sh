#!/bin/bash
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#

renderroot="/mnt/c/bedlam2/images"

renderjob="test_hdri"
grouptype="be_hdri_1_10_test"
cameratype_modify="cam_hdri_18-100"
cameratype_animate="cam_hdri_18-100"
outputroot="$renderroot/$renderjob"

mkdir -p "$outputroot"
# Create body sequences on stage at origin
./be_generate_sequences_crowd.py $grouptype ../../config/whitelist_hdri.txt  | tee "$outputroot/be_seq_default.csv"

# Move stage forward for defined camera focal length range
./be_modify_sequences.py "$outputroot/be_seq_default.csv" autodistance $cameratype_modify

# Rotate stage and camera around origin for randomized view into HDR panorama
./be_modify_sequences.py "$outputroot/be_seq_default_autodistance.csv" sequenceroot -180 180
cp -v "$outputroot/be_seq_default_autodistance_sequenceroot.csv" "$outputroot/be_seq.csv"

# Generate camera animations (be_camera_animations.json)
./be_generate_camera_animations.py "$outputroot/be_seq.csv" $cameratype_animate
