# BEDLAM2 Unreal Rendering
BEDLAM2 Unreal image rendering tools utilize Python editor scripting in combination with a custom BEDLAM2 Unreal Editor UI to automate the following tasks:
+ Auto-generate Unreal Sequencer `LevelSequence` assets based on selected body scene data definition file (`be_seq.csv`)
+ Setup [Movie Render Queue](https://dev.epicgames.com/documentation/en-us/unreal-engine/render-cinematics-in-unreal-engine?application_version=5.3) render jobs for selected `Level Sequence` assets.
  + DX12 rasterizer with 7 temporal samples for motion blur
  + If depth maps and segmentation masks are desired a second optional render pass can output EXR files (16-bit float, multilayer, cryptomatte) without spatial and temporal samples
+ Setup data for command-line rendering or start immediate rendering from Editor

# Special Unreal plugins for BEDLAM2
BEDLAM2 rendering can use the following special plugins:
+ Customized Movie Render Queue plugin for storing camera ground truth for all temporal subframes
  + This is mandatory for obtaining correct center subframe camera ground truth information
    + Without this the EXR pass will always store last subframe camera ground truth
  + Available in https://bedlam2.is.tuebingen.mpg.de/ download area
    + Unreal Engine Assets for Rendering
      + BE_MRQ

+ BEDLAM engine plugin
  + Optional, only needed when using deterministic Perlin noise camera shake variations
  + Available in https://bedlam2.is.tuebingen.mpg.de/ download area
    + Unreal Engine Assets for Rendering
      + BE_EnginePlugin

# Requirements
+ Windows 11
+ Unreal Engine 5.3.2
+ BEDLAM2 Unreal Core assets in Unreal Editor `UE_5.3/Engine/Content/PS/Bedlam/Core` content folder
  + Installation:
    + Close Unreal Editor if running
    + Download BE_Core Unreal assets
      + Available in https://bedlam2.is.tuebingen.mpg.de/ download area
        + Unreal Engine Assets for Rendering
          + BE_Core
    + Copy BE_Core folder contents to `UE_5.3\Engine\Content\PS\Core` Engine install directory
      + See [unreal_editor_assets.md](unreal_editor_assets.md) for expected folder layout

+ Imported BEDLAM2 body and clothing assets under `UE_5.3\Engine\Content\PS` Engine install directory
  + `UE_5.3\Engine\Content\PS\Bedlam\SMPLX_LH`: SMPL-X (locked head) animated bodies as GeometryCache (required)
  + `UE_5.3\Engine\Content\PS\Bedlam\SMPLX_LH_animations`: SMPL-X (locked head) animated bodies as SkeletalMesh (only required when targeting body parts with camera)
  + `UE_5.3\Engine\Content\PS\Bedlam\Clothing`: simulated clothing and textures
  + `UE_5.3\Engine\Content\PS\Bedlam\Hair`: strand-based hair grooms
  + `UE_5.3\Engine\Content\PS\Bedlam\HDRI\8k`: 8K HDR images
  + `UE_5.3\Engine\Content\PS\Bedlam\Shoes`: displacement map shoes
  + `UE_5.3\Engine\Content\PS\Meshcapade\SMPLX`: body textures (UV2023) and materials

+ Unreal Engine project with the following active plugins
  + [Python Editor Script Plugin](https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python?application_version=5.3)
  + Editor Scripting Utilities
  + Sequencer Scripting
  + Movie Render Queue
  + Movie Render Queue Additional Render Passes
    + only needed if you also want to generate depth maps and segmentation masks
  + Groom
    + needed for strand-based hair
  + Geometry Script
    + only needed for stage location definitions with optional occlusion areas

+ Add path to `UE_5.3\Engine\Content\PS\Bedlam\Core\Python` engine folder to your project settings
  + Edit>Project Settings>Plugins>Python>Additional Paths: `../../Content/PS/Bedlam/Core/Python`

+ Recommended PC Hardware:
  + CPU: Modern multi-core CPU with high clock speed (Intel i9-12900K, AMD Ryzen Threadripper PRO 7955WX)
  + GPU: NVIDIA RTX3090 or higher
  + Memory: 128GB or more
  + Storage: Fast SSD with 16TB of free space

# Usage
+ Copy `be_seq.csv` and `be_camera_animations.json` to target render folder
  + Example: `C:\bedlam2\images\test\be_seq.csv`
+ Run BEDLAM2 Editor Utility Widget and dock it in Unreal UI if not already active
  + Make sure that "Show Engine Content" is activated in Content Browser settings
  + Select in Content Browser `/Engine/PS/Bedlam/Core/EditorScripting/BEDLAM2`, right-click, Run Editor Utility Widget
+ Open target Level map
  + It is important to have the Level map open before you try to generate sequences since our LevelSequences depend on Level assets
+ Setup level with BEDLAM2 camera system actors
  + Create BEDLAM/ folder in Outliner and add following items to it
  + Add Actor at origin and rename it to `BE_CameraTarget`
  + Add `BE_CameraOperator` from BEDLAM2 Core assets at origin
    + Set `BE_CameraTarget` as follow source
  + Add Actor at origin and rename it to `BE_CameraRoot`
    + Add `BE_CineCameraActor_Blueprint` from Core assets as child at origin
      + in Lookat Tracking Settings
        + set `BE_CameraTarget` as Actor To Track
        + set Interp Speed to 0.5 for smooth tracking
        + enable Allow Roll
+ Change path in BEDLAM2 UI to target render folder
  + Example: `C:\bedlam2\images\test`
+ Click on `[Create LevelSequences]` and wait for them be created under `/Game/Bedlam/LevelSequences/`
  + Button will turn green at the end when LevelSequence generation was successful
  + Details: [create_level_sequences_csv.py](Core/Python/create_level_sequences_csv.py)
+ Select render preset
  + `1-1-7_EXR_PNG`: Render every frame (30fps image sequences, 7 temporal samples, motion blur), create EXR files with ground truth information, create PNG files
  + `1-1-1_DepthMask`: Render depth pass for every frame with only 1 spatial and 1 temporal sample (no motion blur), create only EXR files
    + EXR files are in multilayer format and contain 16-bit depth information, RGB image and Cryptomatte masks
+ Recommended: Activate `Save MRQ Batches` to create necessary data for command-line rendering
  + Rendering via command line will render in smaller batches and auto-restart editor to avoid out-of-memory issues
+ Select desired subset of LevelSequences in Content Browser
  + For 128GB systems and immediate rendering (not via command line) you might want to limit this to less than 250 sequences when rendering simulated clothing to avoid out-of-memory errors
+ Click on `[Create MovieRenderQueue]` to create movie render jobs based on LevelSequence selection and render preset
  + Details: [create_movie_render_queue.py](Core/Python/create_movie_render_queue.py)
+ If you use command-line rendering (recommended):
  + Close Unreal Editor
  + See [remote_execution/start_batch_render.py](remote_execution/start_batch_render.py) for further details
+ If not using the command-line rendering:
  + Click on `[Render]` to immediately start rendering from Editor
    + Details: [render_movie_render_queue.py](Core/Python/render_movie_render_queue.py)
