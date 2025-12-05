# SMPL-X Animation Data ABC Preparation for Unreal
This tool lets you batch convert a folder of BEDLAM2 SMPL-X .npz animation data files to animated SMPL-X (locked head, no head bun) bodies in [Alembic](http://www.alembic.io) ABC format using :heart:Blender:heart:.

We later import these ABC files into Unreal but they can also be used in other tools like Blender. Blender import and playback of ABC is very fast.

Note that the SMPL-X pose correctives are baked in the Alembic geometry cache and will be automatically applied when playing back the Alembic files after importing. Additional plugins do not need to be installed for proper playback.

# Requirements
+ Windows 10 or later
    + Data preparation stage will likely also work under Linux or macOS thanks to Blender but we have not tested this and are not providing support for this option
+ [Python for Windows (3.10.6 or later)](https://www.python.org/downloads/windows/)
+ [Blender 4.0.2+ for Windows](https://www.blender.org)
+ SMPL-X Blender add-on (20241129 or later)
    + This tool will let you import BEDLAM2 .npz animation files into Blender as animated SMPL-X (locked head, no head bun) mesh
    + Installation instructions:
        + Register at https://smpl-x.is.tue.mpg.de and download the SMPL-X for Blender add-on (latest release). The ZIP release file will include the required SMPL-X model which is not included in the add-on code repository.
        + Follow instructions at https://gitlab.tuebingen.mpg.de/jtesch/smplx_blender_addon


If you want to use the BEDLAM2 animations:
+ Download BEDLAM2 .npz animation archive (`b2_motions_npz_training.tar`) from https://bedlam2.is.tuebingen.mpg.de
+ Extract the .npz files to your filesystem
    + Example: `C:\bedlam2\animations\training\it_4001_XL_2400.npz`

# Usage
1. Edit [smplx_anim_to_alembic_batch.py](smplx_anim_to_alembic_batch.py) and change `BLENDER_APP_PATH` to point to where you installed Blender with the SMPL-X Blender add-on
2. Open Windows command prompt where you have access to your installed Python version
3. Run multiprocess batch conversion. The following example uses 12 CPU cores. Depending on your available CPU core count and available main memory (128GB+ recommended) you can increase or need to decrease the amount of processes. For fastest processing make sure that you have a fast SSD with large enough space (4TB). Due to the large amount of BEDLAM2 animation files, we recommend to first benchmark memory usage and conversion time on your system with a smaller subset of animations.

Example:
```
py -3 smplx_anim_to_alembic_batch.py C:\bedlam2\animations\training C:\bedlam2\animations\abc 12
```

# Notes
+ BEDLAM2 .npz files use Y-Up format in SMPL-X OpenGL coordinate frame notation. To properly manually import them into Blender with the add-on, you need to make sure that `Locked Head` is selected as SMPL-X Model version in the add-on panel before clicking on the `Add Animation` button. Then make sure that `Format:SMPL-X` is selected in the import dialog options. The automation script is always using these options while it is running.
+ If you want to import AMASS SMPL-X .npz animations with the automation script you need to change [smplx_anim_to_alembic.py](smplx_anim_to_alembic.py) to use `anim_format="AMASS"`
+ If you want to play the 30fps ABC files in Blender then make sure that your Blender framerate was changed to 30fps from the default 24fps before you import the file. We recommend to change to 30fps once and then save as default via `File>Defaults>Save Startup File`.
