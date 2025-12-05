# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
from pathlib import Path
from typing import NamedTuple

# Globals
SUBJECT_GENDER_PATH = Path("../../config/gender.csv")                       # Gender information for each subject
TEXTURES_OVERLAY_PATH = Path("../../config/textures_clothing_overlay.json") # List of available overlay textures per gender

# Predefined configurations
# Notes:
#   hfov = 65.470451 : 28mm lens on 36x20.25 DSLR filmback
class ConfigCamera(NamedTuple):
    hfov: float = -1.0 # Default: use existing hfov from source
    hfov_min: float = -1.0
    hfov_max: float = -1.0
    x_offset_max: float = 0.0
    y_offset_max: float = 0.0
    z_offset_max: float = 0.0
    yaw_min: float = 0.0
    yaw_max: float = 0.0
    pitch_min: float = 0.0
    pitch_max: float = 0.0
    roll_min: float = 0.0
    roll_max: float = 0.0
    hfov: float = 0.0
    override_cam_position: bool = False
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    pitch_from_height: bool = False
    z_min: float = 100.0
    pitch_z_min: float = 5.0
    z_max: float = 250.0
    pitch_z_max: float = -40.0
    camera_autodistance_ref: float = 200.0 # horizontal distance for HFOV=52, larger values will increase distance to body when calculating distance from HFOV

configs_camera = {}

# Default camera configuration
config_default = ConfigCamera()
configs_camera["cam_default"] = config_default

configs_camera["cam_random_a"] = ConfigCamera(x_offset_max=100.0, y_offset_max=100.0, z_offset_max=15.0, yaw_min=-5, yaw_max=5, pitch_min=-15, pitch_max=5, roll_min=-3, roll_max=3)

configs_camera["cam_random_b"] = ConfigCamera(x_offset_max=0.0, y_offset_max=0.0, z_offset_max=0.0, yaw_min=0, yaw_max=0, pitch_min=-18, pitch_max=3, roll_min=-3, roll_max=3)

configs_camera["cam_random_c"] = ConfigCamera(x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-18, pitch_max=3, roll_min=-3, roll_max=3)

configs_camera["cam_random_d"] = ConfigCamera(x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-5, pitch_max=3, roll_min=-3, roll_max=3)

configs_camera["cam_random_e"] = ConfigCamera(x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-10, pitch_max=3, roll_min=-3, roll_max=3)

configs_camera["cam_random_f"] = ConfigCamera(override_cam_position=True, x = -1000, z = 170, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-10, pitch_max=3, roll_min=-3, roll_max=3)

configs_camera["cam_random_g"] = ConfigCamera(hfov=25, override_cam_position=True, x = -1000, z = 170, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-1, yaw_max=1, pitch_min=-5, pitch_max=2, roll_min=-3, roll_max=3)

configs_camera["cam_random_h"] = ConfigCamera(x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-18, pitch_max=-10, roll_min=-3, roll_max=3)

configs_camera["cam_random_i"] = ConfigCamera(x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=0, pitch_max=3, roll_min=-3, roll_max=3)


# Low camera, world ground plane height at 263.75
configs_camera["cam_stadium_a"] = ConfigCamera(override_cam_position=True, x = -1000, z = (263.75 + 15.0), x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=5, pitch_max=15, roll_min=-3, roll_max=3)

# High camera, world ground plane height at 263.75
configs_camera["cam_stadium_b"] = ConfigCamera(override_cam_position=True, x = -1000, z = (263.75 + 300.0), x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-20, pitch_max=-10, roll_min=-3, roll_max=3)
configs_camera["cam_stadium_c"] = ConfigCamera(hfov=65.470451, override_cam_position=True, x = -1000, z = (263.75 + 300.0), x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-25, pitch_max=-5, roll_min=-3, roll_max=3)

configs_camera["cam_stadium_d"] = ConfigCamera(override_cam_position=True, x = -1000, z = (263.75 + 170.0), x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-10, pitch_max=3, roll_min=-3, roll_max=3)

# Closeup camera, 2m distance, 28mm, portrait mode
configs_camera["cam_closeup_a"] = ConfigCamera(hfov=65.470451, override_cam_position=True, x = -200, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-2, yaw_max=2, pitch_min=-2, pitch_max=2, roll_min=87, roll_max=93, pitch_from_height=True)
configs_camera["cam_closeup_b"] = ConfigCamera(hfov=39.597752, override_cam_position=True, x = -200, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-2, yaw_max=2, pitch_min=-2, pitch_max=2, roll_min=-3, roll_max=3, pitch_from_height=True, pitch_z_min=5, pitch_z_max=-25)

# Zoom camera
configs_camera["cam_zoom_a"] = ConfigCamera(override_cam_position=True, x=-1000.0, z=170.0, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-10, pitch_max=0, roll_min=-3, roll_max=3)

# Orbit camera
configs_camera["cam_orbit_a"] = ConfigCamera(override_cam_position=True, x=-450.0, z=170.0, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-15, pitch_max=-5, roll_min=-3, roll_max=3)
configs_camera["cam_orbit_b"] = ConfigCamera(override_cam_position=True, x=-450.0, z=100.0, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-10, pitch_max=10, roll_min=-3, roll_max=3)

# Big office
configs_camera["cam_bigoffice_a"] = ConfigCamera(override_cam_position=True, x=-350.0, z=170.0, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=5.0, yaw_min=-3, yaw_max=3, pitch_min=-15, pitch_max=-5, roll_min=-3, roll_max=3)

# A Pose
configs_camera["cam_apose_a"] = ConfigCamera(override_cam_position=True, x=-400.0, z=170.0, x_offset_max=0.0, y_offset_max=0.0, z_offset_max=0.0, yaw_min=-0, yaw_max=0, pitch_min=-10, pitch_max=-10, roll_min=-0, roll_max=0)

# Tracking
configs_camera["cam_tracking_hdri"] = ConfigCamera(x_offset_max=5.0, y_offset_max=5.0, z_offset_max=10.0, yaw_min=0, yaw_max=0, pitch_min=0, pitch_max=0, roll_min=-3, roll_max=3)

# HDRI
configs_camera["cam_hdri_moyo_70_200"] = ConfigCamera(hfov_min=10.285528, hfov_max=28.841545, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=0.0, roll_min=-3, roll_max=3)
configs_camera["cam_hdri_moyo_100-400"] = ConfigCamera(hfov_min=5.153143, hfov_max=20.407946, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=0.0, roll_min=-3, roll_max=3)

configs_camera["cam_hdri_80-120"] = ConfigCamera(camera_autodistance_ref=120, hfov_min=17.061531, hfov_max=25.360765, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=0.0, roll_min=-3, roll_max=3)
configs_camera["cam_hdri_18-120"] = ConfigCamera(camera_autodistance_ref=150, hfov_min=17.061531, hfov_max=90.0, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=0.0, roll_min=-3, roll_max=3)
configs_camera["cam_hdri_50-100"] = ConfigCamera(camera_autodistance_ref=260, hfov_min=20.407946, hfov_max=39.597752, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=10.0, roll_min=-3, roll_max=3)
configs_camera["cam_hdri_18-100"] = ConfigCamera(camera_autodistance_ref=260, hfov_min=20.407946, hfov_max=90.0, x_offset_max=10.0, y_offset_max=10.0, z_offset_max=10.0, roll_min=-3, roll_max=3)
