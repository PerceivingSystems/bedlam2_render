# Render Sequence Generation
BEDLAM2 Unreal render setup utilizes a data-driven design approach where external data files (`be_seq.csv`, `be_camera_animations.json`) are used to define the setup of the required Unreal assets for rendering.

The files in this folder are used to generate and modify these files.

The generated body scene and camera definition files will later be used by the Unreal automation tool to generate the required Unreal Sequencer `LevelSequence` assets for rendering.

# Scripts

## Generate initial scene definition
+ [be_generate_sequences_crowd.py](be_generate_sequences_crowd.py)
  + Run from WSL2 Python 3.10 venv
    + Dependencies: opencv-python-headless, numpy
  + If you want to use the BEDLAM2 animations:
    + Download BEDLAM2 .npz animation archive (`b2_motions_npz_training.tar`) from https://bedlam2.is.tuebingen.mpg.de
    + Extract the .npz files to your filesystem
      + Example: `C:\bedlam2\animations\training\it_4001_XL_2400.npz`
  + Adjust `DATA_SUBSET` and animation folder data path `SMPLX_NPZ_ANIMATION_FOLDER` at top of `be_generate_sequences_crowd_config.py` script if needed
    + Animation data must be in `.npz` format in SMPL-X orientation notation (Y-up)

+ Generate external body scene description (`be_seq.csv`) with desired number of animated sequences. Each sequence is randomized based on predefined randomization settings for
  +  Bodies per scene
  +  Body start locations and orientations
  +  Animation subsequences
  +  Body textures
  +  Simulated clothing and textures
  +  Hair (optional)
  +  Shoes (optional)
  +  HDR image (for IBL rendering)
+ Place randomized animated bodies on flat virtual performance stage.
+ Utilize simple binary ground occupancy masks to avoid overlap of animated bodies. See [BEDLAM Paper Supplementary Material](https://bedlam.is.tuebingen.mpg.de/) for details.
+ Body and camera pose information is in standard Unreal coordinate notation
  + [cm], X: forward, Y: right, Z: up
  + Rotations: Yaw (local=global) -> Pitch (local) -> Roll (local)
    + Rotation directions:
      + yaw: positive yaw rotates to the right (left-hand rule)
      + pitch: positive pitch rotates up (right-hand rule)
      + roll: positive roll rotates clockwise (right-hand rule)
  + Default camera direction: looking along +X axis
+ Ground trajectory images for generated sequence will be stored in `images/` subfolder

### Example
+ 5 subjects, 10 sequences, stage center at 1000cm distance from origin, no hair, no shoes

```
mkdir -p /mnt/c/bedlam2/images/test
./be_generate_sequences_crowd.py be_hdri_5_10_test | tee /mnt/c/bedlam2/images/test/be_seq.csv
```

## Modify existing scene definition
+ [be_modify_sequences.py](be_modify_sequences.py)
+ Modifies existing `be_seq.csv` body scene definition with desired option

## Generate camera animations
+ [be_generate_camera_animations.py](be_generate_camera_animations.py)
  + Generate optional camera motion definition in `be_camera_animations.json` for automated Unreal Engine camera setup
  + Camera motions
    + Synthetic camera motions
      + Static location with optional panning to target body part
      + Dolly (X, XY, Y, Z)
      + Follow/Tracking of target body part
      + Orbit
    + Captured camera motions (vcam)
      + Data sources: Handheld (phone/tablet), egocentric (Apple Vision Pro)
        + Standing
        + Orbit
        + Approach/retreat
      + If you want to use these then please follow setup instructions in `config/vcam/` folder
    + Optional Perlin-noise camera shake on top of above motions

## Example HDRI render setup
+ [be_make_hdri_template.sh](be_make_hdri_template.sh)
  + Create initial body sequences on stage at origin
    + 1 subject per sequence, 10 sequences, stage center at origin, no hair, no shoes
  + Modify sequences
    + Move stage forward for defined camera focal length range
    + Rotate stage and camera around origin for randomized view into HDR panorama
  + Generate camera animations (be_camera_animations.json)
