# BEDLAM2 Render Tools
![status](https://img.shields.io/badge/status-work--in--progress-orange)
![eta](https://img.shields.io/badge/ETA-December%2019%202025-blue)

This repository contains the render pipeline tools used for the generation of the [BEDLAM2.0](https://bedlam2.is.tue.mpg.de) synthetic video dataset (NeurIPS 2025, Datasets and Benchmarks track).

It includes automation scripts for SMPL-X data preparation in Blender, Unreal Engine 5.3.2 data import and rendering, and data post processing.

---
⚠️ **Work in Progress** ⚠️

This project is actively under development for public code release. The render pipeline code with required dependencies and documentation is expected to be completed by **December 19, 2025**. Please see [Issue Tracker](https://github.com/PerceivingSystems/bedlam2_render/issues) for additional details. You can use the GitHub repo  **Watch button** if you want to get notified about incoming updates.

---

Related repositories:
+ Machine Learning
  + Images
    + [BEDLAM2 image model (CameraHMR) training, evaluation and demo Python code](https://github.com/pixelite1201/CameraHMR/blob/master/docs/bedlam2.md)
    + [BEDLAM2 image data processing and visualization Python code](https://github.com/pixelite1201/BEDLAM/tree/master/data_processing#bedlam-v2-data-processing)
  + Videos
    + GVHMR: [Training and evaluation code of GVHMR on BEDLAM2 dataset](https://github.com/mkocabas/GVHMR_BEDLAM2)
    + PromptHMR: [Checkpoints of PromptHMR-video trained on BEDLAM1 and BEDLAM2 datasets](https://github.com/yufu-wang/PromptHMR)
+ [BEDLAM2 Retargeting](https://github.com/PerceivingSystems/bedlam2_retargeting)
+ Rendering: [BEDLAM CVPR2023 render pipeline tools for Unreal 5.0](https://bedlam.is.tue.mpg.de)

# Render Pipeline

## Data preparation

### Data preparation for Unreal (Blender)
+ Create animated [SMPL-X](https://smpl-x.is.tue.mpg.de/) bodies (locked head, no head bun, neutral model, UV map 2023) from SMPL-X animation data files and export in Alembic ABC format. SMPL-X pose correctives are baked in the Alembic geometry cache and will be used in Unreal without any additional software requirements.
+ Details: [blender/smplx_anim_to_alembic/](blender/smplx_anim_to_alembic/)

### Data import (Unreal)
+ Import simulated clothing and SMPL-X Alembic ABC files as `GeometryCache`
+ Import body and clothing textures
+ Import high-dynamic range panoramic images (HDRIs) for image-based lighting
+ Import hair grooms
+ Import shoe color textures and displacement maps
+ Details: [unreal/import/](unreal/import/)

## Render sequence generation
BEDLAM2 Unreal render setup utilizes a data-driven design approach where external data files (`be_seq.csv`, `be_camera_animations.json`) are used to define the setup of the required Unreal assets for rendering.

+ Generate body scene definition (`be_seq.csv`) based on randomization configuration for all the sequences in the desired render job
+ Generate camera motion definition for all the sequences in the desired render job (`be_camera_animations.json`)
+ Details: [tools/sequence_generation/](tools/sequence_generation/)

## Rendering (Unreal)
+ Auto-generate Unreal Sequencer `LevelSequence` assets based on selected body scene and camera motion setup files
+ Render generated Sequencer assets with [Movie Render Queue](https://dev.epicgames.com/documentation/en-us/unreal-engine/render-cinematics-in-unreal-engine?application_version=5.3) using DX12 rasterizer with 7 temporal samples for motion blur
+ If depth maps and segmentation masks are desired, a second optional render pass can output EXR files (16-bit float, multilayer, cryptomatte) without spatial and temporal samples
+ Camera ground truth poses in Unreal coordinates are stored in EXR image metadata during rendering and later extracted in post-process stage to CSV and JSON format
+ Details: [unreal/render/](unreal/render/)

## Post processing
+ Extract world-space camera ground truth information for center subframe
+ Generate MP4 movies from image sequences with ffmpeg
+ Generate overview images for first/middle/last image of each sequence
+ Generate camera motion plots from extracted camera ground truth
+ Extract separate depth maps (EXR) and segmentation masks (PNG) if required EXR data is available
+ Details: [tools/post_render_pipeline/be_post_render_pipeline.sh](tools/post_render_pipeline/be_post_render_pipeline.sh)

# Getting Started

## Requirements
+ Rendering: [Unreal Engine 5.3.2 for Windows](https://www.unrealengine.com) and good knowledge of how to use it
+ Data preparation: [Blender](https://www.blender.org) (4.0.2 or later)
+ Windows 11
    + Data preparation stage will likely also work under Linux or macOS thanks to Blender but we have not tested this and are not providing support for this option
    + Windows WSL2 subsystem for Linux with Ubuntu 22.04 or 24.04
    + [Python for Windows (3.10.6 or later)](https://www.python.org/downloads/windows/)
+ Recommended PC Hardware:
  + CPU: Modern multi-core CPU with high clock speed (Intel i9-12900K, AMD Ryzen Threadripper PRO 7955WX)
  + GPU: NVIDIA RTX3090 or higher
  + Memory: 128GB or more
  + Storage: Fast SSD with 16TB of free space

## Setup
1. Clone repository to `C:\bedlam2\render` folder
```
C:\bedlam2\render
├── LICENSE.md
├── README.md
├── blender
├── config
├── stats
├── tools
└── unreal
```

2. Create WSL2 Python 3.10.6+ venv, activate it and install required packages
```
pip install -r requirements.txt
```

# Notes
+ GitHub
  + Issues
    + Please check first if your issue was already reported in the issue tracker before opening a new one. Make sure to check both [open](https://github.com/PerceivingSystems/bedlam2_render/issues) and also [closed](https://github.com/PerceivingSystems/bedlam2_render/issues?q=is%3Aissue+is%3Aclosed) issues.
    + Use descriptive name for your issue which clearly states the problem
    + Do not ask several unrelated questions on the same issue
  + Pull requests
    + We are not accepting unrequested pull requests

# Citation
```
@inproceedings{tesch2025bedlam2,
  title={{BEDLAM}2.0: Synthetic humans and cameras in motion},
  author={Joachim Tesch and Giorgio Becherini and Prerana Achar and Anastasios Yiannakidis and Muhammed Kocabas and Priyanka Patel and Michael J. Black},
  booktitle={The Thirty-ninth Annual Conference on Neural Information Processing Systems Datasets and Benchmarks Track},
  year={2025}
}
```
