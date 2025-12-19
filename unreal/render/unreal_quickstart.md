# Quickstart for BEDLAM2 Unreal Rendering
The following instructions explain how to setup BEDLAM2 Unreal 5.3.2 rendering using the Unreal Assets Starter Pack and related core assets provided in the download area of the BEDLAM2 project website.

The starterpack contains a subset of 150 motions with simulated clothing for 51 body shapes setup for rendering with shoes (toeless foot) and hair. Also included are body and clothing textures, hair and shoe assets, and HDR images. Additional Blender data preparation and `unreal/import/` scripts are not needed.

## Requirements
+ Windows 11
+ Unreal Engine 5.3.2

## Installation
+ Close all running instances of Unreal Editor
+ Download and install the following assets from BEDLAM2 website. Follow the instructions in the contained README files.
  + `BE_Core`
  + `BE_IBL` sample project
  + `BE_EnginePlugin`
  + `BE_MRQ`
    + Install as plugin in `BE_IBL/Plugins` folder

+ Download and install the Unreal Assets Starter Pack components from BEDLAM2 website. Follow the instructions in the contained README files.
  + Animated bodies
  + Body textures
  + Simulated clothing and textures
  + Hair
  + Shoes
  + HDR images

## Create render definition data
+ Download and extract ground truth motion `.npz` files to `C:\bedlam2\animations\training`
+ Go to folder `tools\sequence_generation\`
+ `be_generate_sequences_crowd_config.py`
  + Edit `WHITELIST_PATH` to use `whitelist_animations_starterpack.json`
+ `be_make_hdri_template.sh`
  + Edit `renderjob` and `grouptype` to use starterpack configuration
+ Run `be_make_hdri_template.sh`
  + will generate `be_seq.csv` and `be_camera_animations.json` files in `C:\bedlam2\images\starterpack`

## Setup Unreal rendering
+ Open `BE_IBL` project in Unreal Editor
+ Open Bedlam/IBLMap
+ Run BEDLAM2 Editor Utility Widget and dock it in Unreal UI if not already active
  + Make sure that "Show Engine Content" is activated in Content Browser settings
  + Select in Content Browser `/Engine/PS/Bedlam/Core/EditorScripting/BEDLAM2`, right-click, Run Editor Utility Widget
+ Change path in BEDLAM2 UI to target render folder
  + Example: `C:\bedlam2\images\starterpack`
+ Click on `[Create LevelSequences]` and wait for them be created under `/Game/Bedlam/LevelSequences/`
  + Button will turn green at the end when LevelSequence generation was successful
  + Details: [create_level_sequences_csv.py](Core/Python/create_level_sequences_csv.py)
+ Select render preset
  + `1-1-7_EXR_PNG`: Render every frame (30fps image sequences, 7 temporal samples, motion blur), create EXR files with ground truth information, create PNG files
+ Activate `Save MRQ Batches` to create necessary data for command-line rendering
  + Rendering via command-line will render in smaller batches and auto-restart editor to avoid out-of-memory issues
+ Select all 150 LevelSequences in Content Browser `Bedlam/LevelSequences` folder
+ Click on `[Create MovieRenderQueue]` to create movie render jobs based on LevelSequence selection and render preset
  + Details: [create_movie_render_queue.py](Core/Python/create_movie_render_queue.py)
+ Close Unreal Editor

## Batch render with Unreal from command-line
+ Run command-line rendering
  + See [remote_execution/start_batch_render.py](remote_execution/start_batch_render.py) for further command-line rendering details
  + Render should complete in about 1h on RTX4090 GPU

## Post-process rendered data
+ Go to folder `tools\post_render_pipeline\`
+ Run `./be_post_render_pipeline.sh /mnt/c/bedlam2/images/starterpack/ landscape`
+ Will generate additional data under `C:\bedlam2\images\starterpack\`
  + `png`: 41799 PNG images, 57 GB
  + `mp4`: 150 MP4 videos
  + `ground_truth`: world-space camera poses in CSV and JSON
  + `overview`: overview images, camera plots for intrinsics and extrinsics
+ Optional: delete `exr_image` folder once ground truth was successfully extracted
