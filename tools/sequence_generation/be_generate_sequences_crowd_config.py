# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Sequence generation configurations for be_generate_sequences_crowd.py
from pathlib import Path
from typing import NamedTuple

# Globals
CV_IMAGESIZE = 101 # represents 10m distance with origin in center of image at (50,50)
CV_M_TO_PIXELS = 10
CV_BODY_RADIUS = 5  # 50cm body radius
#CV_BODY_RADIUS = 10  # 100cm body radius (MOYO multipeople)

CONFIG_ROOT = Path("../../config")
STATS_ROOT = Path("../../stats")

DATA_SUBSET="training"
USE_MOYO=False

SMPLX_NPZ_ANIMATION_FOLDER = Path(f"/mnt/c/bedlam2/animations/{DATA_SUBSET}")

WHITELIST_PATH = CONFIG_ROOT / f"whitelist_animations_{DATA_SUBSET}.json" # Per-subject whitelisted animations
#WHITELIST_PATH = CONFIG_ROOT / f"whitelist_animations_starterpack.json" # Starterpack animations

TEXTURES_BODY_PATH = CONFIG_ROOT / "textures_body.txt" # List of available body textures

# Override paths for MOYO renders
if USE_MOYO:
    WHITELIST_PATH = CONFIG_ROOT / f"whitelist_animations_moyo.json" # Per-subject whitelisted animations
    TEXTURES_BODY_PATH = CONFIG_ROOT / "textures_body_moyo.txt"

SUBJECT_GENDER_PATH = CONFIG_ROOT / f"gender_{DATA_SUBSET}.csv" # Gender information for each subject

OUTFIT_INFO_PATH = CONFIG_ROOT / f"motion2outfit_{DATA_SUBSET}.json" # Dictionary of motion outfits and available textures

MOTION_STATS_PATH = STATS_ROOT / f"motion_stats_{DATA_SUBSET}.csv"

WHITELIST_HAIR_PATH = CONFIG_ROOT / "whitelist_hair.json"
WHITELIST_HAIRCOLORS_PATH = CONFIG_ROOT / "whitelist_hair_colors.txt"

OUTPUT_IMAGE_ROOT = Path("images")

LOCATIONS_ROOT = CONFIG_ROOT / "locations/"

# Shoes
WHITELIST_SHOES_PATH = CONFIG_ROOT / "shoes" / "whitelist_shoes.txt"
SHOE_OFFSETS_PATH = CONFIG_ROOT / "shoes" / "shoe_offsets.csv"

# Predefined configurations
class Config(NamedTuple):
    bodies_min: int
    bodies_max: int
    x_offset: float = 0.0
    y_offset: float = 0.0
    z_offset: float = 0.0
    x_min: float = -100.0
    x_max: float = 100.0
    y_min: float = -100.0
    y_max: float = 100.0
    yaw_min: float = 0.0 # if use_body_yaw_reference=True then these values will be relative yaw change for body facing default camera
    yaw_max: float = 0.0
    num_sequences: int = 1
    unique_subjects: bool = True
    unique_sequences: bool = True # avoid repetition of subjects and animations between sequences
    use_all_animations: bool = False
    randomize_animations: bool = True
    camera_hfov_deg: float = 65.470451 # 28mm lens on 36x20.25mm DSLR filmback
    camera_height: float = 170.0
    override_cameraroot_location: bool = False
    safety_zone_width: float = 1000
    safety_zone_height: float = 1000
    use_hair: bool = False
    location_file: str = "" # Name of target stage location file in config/locations folder
    location_sequences: int = 10 # Number of sequences to render before moving to next stage location
    time_min: float = -1.0
    time_max: float = -1.0
    balance_subjects: str = "" # Utilize usage_subjects.csv to prefer subjects with lowest usage
    balance_animations: str = "" # Utilize usage_animations.csv to prefer animation with lowest usage for selected subject
    use_body_yaw_reference : bool = False # Use body world yaw from motion_stats.csv to normalize body directions, randomication yaw=0 will then result in body looking along negative X-axis towards default camera.
    use_shoes: bool = False # Use shoes and shoe height offsets

configs = {}

# be_1: 1 person in 8m x 8m area with center at camera distance 10m
config_1_1 = Config(bodies_min=1, bodies_max=1, x_offset=1000, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=1, unique_subjects=False)
configs["be_1_1"] = config_1_1

configs["be_1_apose"] = Config(bodies_min=1, bodies_max=1, x_offset=400, x_min=0, x_max=0, y_min=0, y_max=0, yaw_min=90, yaw_max=90, num_sequences=114, unique_subjects=True, camera_hfov_deg=52.0)
configs["be_1_apose_multicam"] = Config(bodies_min=1, bodies_max=1, x_offset=0, x_min=0, x_max=0, y_min=0, y_max=0, yaw_min=90, yaw_max=90, num_sequences=114, unique_subjects=True, camera_hfov_deg=52.0)
configs["be_1_apose_hair"] = Config(bodies_min=1, bodies_max=1, x_offset=0, x_min=0, x_max=0, y_min=0, y_max=0, yaw_min=90, yaw_max=90, num_sequences=114, unique_subjects=True, camera_hfov_deg=52.0, use_hair=True)

# be_2: 2 people in 8m x 8m area with center at camera distance 10m
config_2_1 = Config(bodies_min=2, bodies_max=2, x_offset=1000, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=1, unique_subjects=False)
configs["be_2_1"] = config_2_1

# be_4: 4 people in 8m x 8m area with center at camera distance 10m
config_4_1 = Config(bodies_min=4, bodies_max=4, x_offset=1000, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=1, unique_subjects=False)
configs["be_4_1"] = config_4_1

config_4_95 = Config(bodies_min=4, bodies_max=4, x_offset=1000, x_min=-300, x_max=300, y_min=-300, y_max=300, yaw_min=0, yaw_max=360, num_sequences=95, unique_subjects=True)
configs["be_4_95"] = config_4_95

# be_5: 5 people in 4m x 4m area with center at camera distance 5m
config_5_10 = Config(bodies_min=5, bodies_max=5, x_offset=500, x_min=-200, x_max=200, y_min=-200, y_max=200, yaw_min=0, yaw_max=360, num_sequences=10, unique_subjects=True)
configs["be_5_10"] = config_5_10


# be_10: 10 people in 8m x 8m area with center at camera distance 10m
config_10_1 = Config(bodies_min=10, bodies_max=10, x_offset=1000, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=1, unique_subjects=False)
configs["be_10_1"] = config_10_1

config_10_10 = Config(bodies_min=10, bodies_max=10, x_offset=1000, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=10, unique_subjects=True, camera_hfov_deg=65.470451)
configs["be_10_10"] = config_10_10

# be_10_95: Use all 95 HDRI images once
config_10_95 = Config(bodies_min=10, bodies_max=10, x_offset=1000, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=95, unique_subjects=False, camera_hfov_deg=65.470451)
configs["be_10_95"] = config_10_95

# 1 person at center, 28mm lens (HFOV 65.470451)
config_1_10 = Config(bodies_min=1, bodies_max=1, x_offset=650, x_min=0, x_max=0, y_min=0, y_max=0, yaw_min=0, yaw_max=360, num_sequences=10, unique_subjects=False, camera_hfov_deg=65.470451)
configs["be_1_10"] = config_1_10

config_1_200 = Config(bodies_min=1, bodies_max=1, x_offset=650, x_min=0, x_max=0, y_min=0, y_max=0, yaw_min=0, yaw_max=360, num_sequences=200, unique_subjects=True, camera_hfov_deg=65.470451)
configs["be_1_200"] = config_1_200

# 3 people
config_3_200 = Config(bodies_min=3, bodies_max=3, x_offset=650, x_min=-50, x_max=50, y_min=-250, y_max=250, yaw_min=0, yaw_max=360, num_sequences=200, unique_subjects=True, camera_hfov_deg=65.470451)
configs["be_3_200"] = config_3_200

configs["be_3_500"] = Config(bodies_min=3, bodies_max=3, x_offset=650, x_min=-50, x_max=50, y_min=-250, y_max=250, yaw_min=0, yaw_max=360, num_sequences=500, unique_subjects=True, camera_hfov_deg=65.470451)

configs["be_3_1000"] = Config(bodies_min=3, bodies_max=3, x_offset=650, x_min=-50, x_max=50, y_min=-250, y_max=250, yaw_min=0, yaw_max=360, num_sequences=1000, unique_subjects=True, unique_sequences=True, camera_hfov_deg=52.0)
configs["be_3_1000_65"] = Config(bodies_min=3, bodies_max=3, x_offset=350, x_min=-50, x_max=50, y_min=-150, y_max=150, yaw_min=0, yaw_max=360, num_sequences=1000, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451)
configs["be_3_250_65"] = Config(bodies_min=3, bodies_max=3, x_offset=500, x_min=-50, x_max=50, y_min=-150, y_max=150, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451)

# 50mm lens
configs["be_3-8_250_40"] = Config(bodies_min=3, bodies_max=8, x_offset=650, x_min=-250, x_max=250, y_min=-200, y_max=200, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=39.597752)

# 1 person
configs["be_1_500"] = Config(bodies_min=1, bodies_max=1, x_offset=650, x_min=-50, x_max=50, y_min=-250, y_max=250, yaw_min=0, yaw_max=360, num_sequences=500, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451)
configs["be_1_100"] = Config(bodies_min=1, bodies_max=1, x_offset=650, x_min=-50, x_max=50, y_min=-150, y_max=150, yaw_min=0, yaw_max=360, num_sequences=100, unique_subjects=True, unique_sequences=True, camera_hfov_deg=52.0)

# Sports Stadium
configs["be_sport_10_5"] = Config(bodies_min=10, bodies_max=10, x_offset=0, z_offset=263.75, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=5, unique_subjects=True, unique_sequences=True, camera_hfov_deg=52.0)
configs["be_sport_10_500"] = Config(bodies_min=10, bodies_max=10, x_offset=0, z_offset=263.75, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=500, unique_subjects=True, unique_sequences=True, camera_hfov_deg=52.0)
configs["be_sport_3-8_250"] = Config(bodies_min=3, bodies_max=8, x_offset=0, z_offset=263.75, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=52.0)

# Tracked person
configs["be_tracked_1_10_52"] = Config(bodies_min=1, bodies_max=1, x_offset=300, x_min=-50, x_max=50, y_min=-50, y_max=50, yaw_min=0, yaw_max=360, num_sequences=10, unique_subjects=True, unique_sequences=True, camera_hfov_deg=52.0)
configs["be_tracked_1_3000_52"] = Config(bodies_min=1, bodies_max=1, x_offset=300, x_min=-50, x_max=50, y_min=-50, y_max=50, yaw_min=0, yaw_max=360, num_sequences=3000, unique_subjects=True, unique_sequences=True, camera_hfov_deg=52.0)

# MOYO
configs["be_1_moyo_hair"] = Config(bodies_min=1, bodies_max=1, x_offset=0, x_min=0, x_max=0, y_min=0, y_max=0, yaw_min=90, yaw_max=90, num_sequences=197, unique_subjects=True, camera_hfov_deg=52.0, use_hair=True)
configs["be_1_moyo"] = Config(bodies_min=1, bodies_max=1, x_offset=500, x_min=-200, x_max=50, y_min=-200, y_max=200, yaw_min=0, yaw_max=360, num_sequences=171, unique_subjects=True, unique_sequences=True, camera_hfov_deg=52.0, safety_zone_width=200, safety_zone_height=200.0)

# Multi locations
configs["be_citysample_locations_1_114_apose"] = Config(bodies_min=1, bodies_max=1, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=114, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=10)
configs["be_citysample_locations_1_198"] = Config(bodies_min=1, bodies_max=1, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=198, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=10)
configs["be_citysample_locations_1_198_hair"] = Config(use_hair=True, bodies_min=1, bodies_max=1, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=198, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=10)
configs["be_citysample_locations_4_10_hair"] = Config(use_hair=True, bodies_min=4, bodies_max=4, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=10, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=1)
configs["be_citysample_locations_8_10_hair"] = Config(use_hair=True, bodies_min=8, bodies_max=8, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=10, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=10)
configs["be_citysample_locations_5_20_hair"] = Config(use_hair=True, bodies_min=5, bodies_max=5, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=20, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=1)

configs["be_stadium_locations_1_20_hair"] = Config(use_hair=True, bodies_min=1, bodies_max=1, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=20, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Stadium_Day_map_Lumen.csv", location_sequences=2)

# Bus Station
configs["be_busstation_5_20_hair"] = Config(use_hair=True, bodies_min=5, bodies_max=5, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=20, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_BusStation.csv", location_sequences=1)

# BE_AIUE_vol08_05
configs["be_ai0805_1_20_hair"] = Config(use_hair=True, bodies_min=1, bodies_max=1, x_min=-200, x_max=200, y_min=-200, y_max=200, yaw_min=0, yaw_max=360, num_sequences=20, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol8_05.csv", location_sequences=1)
configs["be_ai0805_1_500_hair"] = Config(balance_animations=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-200, x_max=200, y_min=-200, y_max=200, yaw_min=0, yaw_max=360, num_sequences=500, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol8_05.csv", location_sequences=1)
configs["be_ai0805_1_250_hair"] = Config(balance_animations=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-100, x_max=100, y_min=-100, y_max=100, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol8_05.csv", location_sequences=1)
configs["be_ai0805_1_250_hair_vcam"] = Config(use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol8_05_vcam.csv", location_sequences=1)

# BE_AIUE_vol10_04
configs["be_ai1004_1_20_hair"] = Config(use_hair=True, bodies_min=1, bodies_max=1, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=20, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol10_04.csv", location_sequences=1)
configs["be_ai1004_2_250_hair"] = Config(balance_animations=True, use_hair=True, bodies_min=2, bodies_max=2, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol10_04.csv", location_sequences=1)
#configs["be_ai1004_1_250_hair"] = Config(balance_subjects="usage_subjects_b2v2.csv", balance_animations="usage_animations_b2v2.csv", use_hair=True, bodies_min=1, bodies_max=1, x_min=-150, x_max=150, y_min=-150, y_max=150, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol10_04.csv", location_sequences=1)
configs["be_ai1004_1_250_hair"] = Config(balance_subjects="", balance_animations="usage_animations_b2v2.csv", use_hair=True, bodies_min=1, bodies_max=1, x_min=-150, x_max=150, y_min=-150, y_max=150, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol10_04.csv", location_sequences=1)
configs["be_ai1004_1_250_hair_vcam"] = Config(use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol10_04_vcam.csv", location_sequences=1)

# BE_YogaStudio
configs["be_yogastudio_1_171_hair"] = Config(randomize_animations=True, time_min=7.5, time_max=19.0, use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=0, num_sequences=171, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Yoga_Studio.csv", location_sequences=1)

# BE_CitySample/MOYO
configs["be_citysample_1_171_hair"] = Config(randomize_animations=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=171, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=9)
configs["be_citysample_5_100_hair"] = Config(randomize_animations=True, use_hair=True, bodies_min=5, bodies_max=5, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=100, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=5)
configs["be_citysample_5_200_hair"] = Config(randomize_animations=True, use_hair=True, bodies_min=5, bodies_max=5, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=200, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=10)

# BE_IBL/MOYO, camera_height will be later set in generate camera animations
configs["be_hdri_1_171_hair"] = Config(randomize_animations=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=171, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451)
configs["be_hdri_10_200_hair"] = Config(randomize_animations=True, use_hair=True, bodies_min=10, bodies_max=10, x_offset=1000, x_min=-450, x_max=450, y_min=-450, y_max=450, yaw_min=0, yaw_max=360, num_sequences=200, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451)

# BE_IBL
configs["be_hdri_1_200_hair"] = Config(randomize_animations=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=200, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451)
configs["be_hdri_1_300_hair"] = Config(randomize_animations=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=300, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451)
configs["be_hdri_10_500_hair"] = Config(balance_subjects=True, balance_animations=True, use_hair=True, bodies_min=10, bodies_max=10, x_offset=1000, x_min=-450, x_max=450, y_min=-450, y_max=450, yaw_min=0, yaw_max=360, num_sequences=500, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451)
configs["be_hdri_1_2337_hair"] = Config(use_all_animations=True, randomize_animations=False, use_hair=True, bodies_min=1, bodies_max=1, x_offset=0, x_min=-10, x_max=10, y_min=-10, y_max=10, yaw_min=0, yaw_max=360, num_sequences=2337, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451)
configs["be_hdri_1_1827_hair"] = Config(use_body_yaw_reference=True, safety_zone_width=1500.0, safety_zone_height=1500.0, use_all_animations=True, randomize_animations=False, use_hair=True, bodies_min=1, bodies_max=1, x_offset=0, x_min=-10, x_max=10, y_min=-10, y_max=10, yaw_min=-45, yaw_max=45, num_sequences=1827, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451)

# BE_Stadium
configs["be_stadium_1_171_hair"] = Config(use_hair=True, time_min=8.0, time_max=17.0, bodies_min=1, bodies_max=1, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=171, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Stadium_Day_map_Lumen.csv", location_sequences=1)
configs["be_stadium_1_500_hair"] = Config(use_hair=True, time_min=8.0, time_max=17.0, bodies_min=1, bodies_max=1, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=500, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Stadium_Day_map_Lumen.csv", location_sequences=1)

# BE_CitySample/b2, use all available animations
configs["be_citysample_1_1001_hair"] = Config(use_all_animations=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=1001, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=50)
configs["be_citysample_5_500_hair"] = Config(use_hair=True, bodies_min=5, bodies_max=5, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=500, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=25)
configs["be_citysample_5_200_hair"] = Config(use_hair=True, bodies_min=5, bodies_max=5, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=200, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Small_City_LVL.csv", location_sequences=10)

# BE_BusStation
configs["be_busstation_3_500_hair"] = Config(use_hair=True, bodies_min=3, bodies_max=3, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=500, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_BusStation.csv", location_sequences=72)
configs["be_busstation_4_250_hair"] = Config(balance_subjects=True, balance_animations=True, use_hair=True, bodies_min=4, bodies_max=4, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_BusStation.csv", location_sequences=36)
configs["be_busstation_5-10_250_hair"] = Config(balance_subjects="", balance_animations="", use_hair=True, bodies_min=5, bodies_max=10, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_BusStation_outdoors.csv", location_sequences=1)

# BE_ArchmodelsVol8
configs["be_archmodels8_5_250_hair"] = Config(balance_subjects=True, balance_animations=True, use_hair=True, bodies_min=5, bodies_max=5, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AM_UE5_Vol8.csv", location_sequences=36)
configs["be_archmodels8_1_250_hair"] = Config(balance_subjects=True, balance_animations=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-200, x_max=200, y_min=-200, y_max=200, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AM_UE5_Vol8.csv", location_sequences=36)

# BE_AIUE_vol09_01
configs["be_ai0901_1_250_hair"] = Config(balance_subjects=True, balance_animations=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-200, x_max=200, y_min=-200, y_max=200, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol9_01.csv", location_sequences=1)
configs["be_ai0901_1_250_hair_a"] = Config(use_hair=True, bodies_min=1, bodies_max=1, x_min=-100, x_max=100, y_min=-100, y_max=100, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol9_01.csv", location_sequences=1)

# BE_AIUE_vol11_01
#configs["be_ai1101_1_250_hair_vcam"] = Config(balance_subjects="usage_subjects_b2v1_vcam.csv", balance_animations="usage_animations_b2v1_vcam.csv", use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol11_01_vcam.csv", location_sequences=1)
configs["be_ai1101_1_250_hair_vcam"] = Config(balance_subjects="", balance_animations="", use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol11_01_vcam.csv", location_sequences=1)

# BE_AIUE_vol11_05
configs["be_ai1105_1_250_hair_vcam"] = Config(balance_subjects="usage_subjects_b2v2_vcam.csv", balance_animations="usage_animations_b2v2_vcam.csv", use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol11_05_vcam.csv", location_sequences=1)

# BE_AIUE_vol11_02
configs["be_ai1102_1_250_hair_vcam"] = Config(balance_subjects="", balance_animations="usage_animations_b2v2_vcam.csv", use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol11_02_vcam.csv", location_sequences=1)

########
# b2v3 #
########

# BE_IBL, with shoes
configs["be_hdri_1_4619_shoes"] = Config(use_shoes=True, use_body_yaw_reference=True, safety_zone_width=1500.0, safety_zone_height=1500.0, use_all_animations=True, randomize_animations=False, use_hair=True, bodies_min=1, bodies_max=1, x_offset=0, x_min=-10, x_max=10, y_min=-10, y_max=10, yaw_min=-60, yaw_max=60, num_sequences=4619, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451)
configs["be_hdri_1_10_shoes"] = Config(use_shoes=True, use_body_yaw_reference=True, safety_zone_width=1500.0, safety_zone_height=1500.0, use_all_animations=True, randomize_animations=False, use_hair=True, bodies_min=1, bodies_max=1, x_offset=0, x_min=-10, x_max=10, y_min=-10, y_max=10, yaw_min=0, yaw_max=0, num_sequences=10, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451)
configs["be_hdri_1_2120_shoes"] = Config(use_shoes=True, use_body_yaw_reference=True, safety_zone_width=1500.0, safety_zone_height=1500.0, use_all_animations=True, randomize_animations=False, use_hair=True, bodies_min=1, bodies_max=1, x_offset=0, x_min=-10, x_max=10, y_min=-10, y_max=10, yaw_min=-90, yaw_max=90, num_sequences=2120, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451)

# BE_ChemicalPlant, with shoes
configs["be_chemicalplant_5_250_shoes"] = Config(use_shoes=True, use_hair=True, bodies_min=5, bodies_max=5, x_min=-200, x_max=200, y_min=-200, y_max=200, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Map_ChemicalPlant_1.csv", location_sequences=1)
configs["be_chemicalplant_1_250_shoes_vcam"] = Config(balance_animations="usage_animations_b2v3_vcam.csv", use_shoes=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Map_ChemicalPlant_1.csv", location_sequences=1)
configs["be_chemicalplant_4-5_250_shoes"] = Config(balance_animations="usage_animations_b2v3.csv", use_shoes=True, use_hair=True, bodies_min=4, bodies_max=5, x_min=-200, x_max=200, y_min=-200, y_max=200, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Map_ChemicalPlant_1.csv", location_sequences=1)
configs["be_chemicalplant_1_250_shoes_upperbody"] = Config(balance_subjects="", balance_animations="usage_animations_b2v3_0_60_80.csv", use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Map_ChemicalPlant_1_a.csv", location_sequences=1)

configs["be_rome_1_250_shoes_vcam_approachshort"] = Config(balance_animations="usage_animations_b2v3_vcam.csv", use_shoes=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Rome_01_P_vcam_approachshort.csv", location_sequences=1)

configs["be_ai1102_1_250_shoes_vcam_standing"] = Config(balance_subjects="", balance_animations="usage_animations_b2v3_vcam.csv", use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol11_02_vcam.csv", location_sequences=1)

configs["be_ai1105_1_250_shoes_upperbody"] = Config(balance_subjects="", balance_animations="usage_animations_b2v3_0_60_80.csv", use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_AIUE_vol11_05_vcam.csv", location_sequences=1)

# BE_Yakohama (BE_CityMegapack2 project)
configs["be_yakohama_4-7_250_shoes"] = Config(use_shoes=True, use_hair=True, bodies_min=4, bodies_max=7, x_min=-450, x_max=450, y_min=-250, y_max=250, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Yakohama.csv", location_sequences=1)
configs["be_yakohama_1_250_shoes_upperbody"] = Config(balance_subjects="", balance_animations="usage_animations_b2v3_0_60_80.csv", use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Yakohama_a.csv", location_sequences=1)

# BE_MiddleEast (BE_CityMegapack2 project)
configs["be_middleeast_2-3_250_shoes"] = Config(balance_subjects="", balance_animations="usage_animations_b2v3_frames_300.csv", use_shoes=True, use_hair=True, bodies_min=2, bodies_max=3, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_MiddleEast.csv", location_sequences=1)

########
# b2v4 #
########
configs["be_rome_5-10_250_shoes"] = Config(use_shoes=True, use_hair=True, bodies_min=5, bodies_max=10, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Rome_01_P.csv", location_sequences=1)
configs["be_rome_1_250_shoes"] = Config(use_shoes=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Rome_01_P.csv", location_sequences=1)
configs["be_rome_1_250_shoes_vcam"] = Config(use_shoes=True, use_hair=True, bodies_min=1, bodies_max=1, x_min=-5, x_max=5, y_min=-5, y_max=5, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_Rome_01_P_vcam.csv", location_sequences=1)

configs["be_middleeast_3-4_250_shoes"] = Config(balance_subjects="", balance_animations="usage_animations_b2v4.csv", use_shoes=True, use_hair=True, bodies_min=3, bodies_max=4, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=250, unique_subjects=True, unique_sequences=True, camera_hfov_deg=65.470451, override_cameraroot_location=True, location_file="BE_MiddleEast.csv", location_sequences=1)

######################################
# Public release test configurations #
######################################

# BE_IBL
# 5 subjects, 10 sequences, stage center at 1000cm distance from origin, no hair, no shoes
configs["be_hdri_5_10_test"] = Config(use_hair=False, use_shoes=False, bodies_min=5, bodies_max=5, x_offset=1000, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=10, camera_hfov_deg=65.470451)
configs["be_hdri_5_10_test_moyo"] = Config(unique_subjects=False,use_hair=False, use_shoes=False, bodies_min=5, bodies_max=5, x_offset=1000, x_min=-400, x_max=400, y_min=-400, y_max=400, yaw_min=0, yaw_max=360, num_sequences=10, camera_hfov_deg=65.470451)

# 1 subject, 10 sequences, stage center at origin, no hair, no shoes, used in be_make_hdri_template.sh template sample
configs["be_hdri_1_10_test"] = Config(use_hair=False, use_shoes=True, safety_zone_width=1500.0, safety_zone_height=1500.0, bodies_min=1, bodies_max=1, x_offset=0, x_min=-10, x_max=10, y_min=-10, y_max=10, yaw_min=0, yaw_max=360, num_sequences=10, camera_hfov_deg=65.470451)

# Starterpack animations with hair and shoes, 1 subjects, 150 sequences, stage center at origin, use in be_make_hdri_template.sh template sample
configs["be_hdri_1_151_starterpack"] = Config(use_shoes=True, use_body_yaw_reference=True, safety_zone_width=1500.0, safety_zone_height=1500.0, use_all_animations=True, randomize_animations=False, use_hair=True, bodies_min=1, bodies_max=1, x_offset=0, x_min=-10, x_max=10, y_min=-10, y_max=10, yaw_min=-90, yaw_max=90, num_sequences=150, unique_subjects=False, unique_sequences=True, camera_hfov_deg=65.470451)
