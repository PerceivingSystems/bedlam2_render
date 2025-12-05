#!/usr/bin/env -S python -u
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Generate .csv file with desired body positions for multiple animated people per sequence
#
# Dependencies:
# + pip install opencv-python-headless
#
# Notes:
#   + Animation data must be in SMPL-X orientation notation (Y-up)
#   + Run in unbuffered mode (-u) to immediately see results when piping stdout to tee
#
#
import copy
import csv
import cv2
from dataclasses import dataclass
import json
from math import radians, tan
import numpy as np
import random
import sys

from be_generate_sequences_crowd_config import *

################################################################################

@dataclass
class SubjectLocationData:
    subject_name: str
    animation_name: str
    frames: int
    bounding_box_area: float
    trans: np.ndarray
    image: np.ndarray
    x: float
    y: float
    yaw: float
    start_frame: int
    used_frames: int


################################################################################
# Helper functions
################################################################################

def get_image_coordinates_from_smplx(imagesize, animation_x, animation_z):
    image_center_x = (imagesize - 1) / 2
    image_center_y = (imagesize - 1) / 2

    # Animation coordinates: X-RightOfBody-FacingAlongPositiveZ, Z-TowardsCamera, [m]
    # OpenCV coordinates: X-Right, Y-Down

    image_x = round(image_center_x + animation_z * CV_M_TO_PIXELS)
    image_y = round(image_center_y - animation_x * CV_M_TO_PIXELS)
    return (image_x, image_y)

def get_image_offset_from_unreal(unreal_x, unreal_y):
    # Unreal coordinates: X-Up, Y-Right, [cm]
    # OpenCV coordinates: X-Right, Y-Down

    image_x = round((unreal_y/100) * CV_M_TO_PIXELS)
    image_y = round((-unreal_x/100) * CV_M_TO_PIXELS)
    return (image_x, image_y)

def transform_image(source_image, unreal_x, unreal_y, unreal_yaw):
    (t_x, t_y) = get_image_offset_from_unreal(unreal_x, unreal_y)

    height, width = source_image.shape
    center = ( (width-1)/2, (height-1)/2 )

    # Rotate source image and then translate it
    # Unreal yaw is left-handed and OpenCV rotations are counter-clockwise
    R = cv2.getRotationMatrix2D(center=center, angle=-unreal_yaw, scale=1)
    source_image_r = cv2.warpAffine(source_image, R, (width, height))

    T = np.float32([[1, 0, t_x],
                    [0, 1, t_y]])

    source_image_r_t = cv2.warpAffine(source_image_r, T, (width, height))

    return source_image_r_t


def get_location_data(c, grouptype, sequence_index, used_subjects, used_animations, animation_folder, location_occupancy_mask, body_yaw_reference):
    location_data = []
    frame_rate_divisor = None
    for index, subject in enumerate(used_subjects):
        animation_name = used_animations[index]

        # Load animation data
        # Animation data must be in SMPL-X orientation notation (Y-up)
        filepath = animation_folder / subject / "moving_body_para" / animation_name / "motion_seq.npz" # BEDLAM CVPR
        if not filepath.exists():
            filepath = animation_folder / subject / animation_name / "motion_seq.npz"
            if not filepath.exists():
                filepath = animation_folder / f"{subject}_{animation_name}.npz"

        with np.load(filepath) as data:
            trans = data["trans"]
            mocap_frame_rate = data["mocap_frame_rate"]

            if frame_rate_divisor is None:
                frame_rate_divisor = 1
                if mocap_frame_rate > 30:
                    frame_rate_divisor = int(mocap_frame_rate / 30)

            # Downsample animation to 30fps via list slicing
            trans_30 = trans[::frame_rate_divisor]
            frames = len(trans_30)

        data = SubjectLocationData(subject, animation_name, frames, 0.0, trans_30, None, 0, 0, 0, 0, 0)
        location_data.append(data)

    # Find shortest animation sequence length
    maximum_sequence_length = sys.maxsize
    for data in location_data:
        if data.frames < maximum_sequence_length:
            maximum_sequence_length = data.frames

    # Randomize animation start frame
    for data in location_data:
        data.start_frame = random.randint(0, data.frames - maximum_sequence_length)
        data.used_frames = maximum_sequence_length

    # Sort location data by covered bounding box area.
    # Smaller areas are easier to place so we do those at the end.
    location_data_areasorted = []
    for data in location_data:
        trans = data.trans[data.start_frame : (data.start_frame + data.used_frames), :]

        x_min = trans[:,0].min()
        x_max = trans[:,0].max()
        z_min = trans[:,2].min()
        z_max = trans[:,2].max()
        data.bounding_box_area = (x_max - x_min) * (z_max - z_min)

        if len(location_data_areasorted) == 0:
            location_data_areasorted.append(data)
        else:
            for index, list_data in enumerate(location_data_areasorted):
                if data.bounding_box_area > list_data.bounding_box_area:
                    location_data_areasorted.insert(index, data)
                    break

                if index == (len(location_data_areasorted) - 1):
                    location_data_areasorted.append(data)
                    break

    # Generate ground occupancy masks for unmodified animations
    for data in location_data_areasorted:
        radius = CV_BODY_RADIUS
        current_location_image = np.zeros( (CV_IMAGESIZE, CV_IMAGESIZE), dtype=np.uint8)
        trans = data.trans[data.start_frame : (data.start_frame + data.used_frames), :]
        for position in trans:
            # Mark occupied area
            circle_center = get_image_coordinates_from_smplx(CV_IMAGESIZE, position[0], position[2])
            cv2.circle(current_location_image, circle_center, radius, 255, -1)

        # Debug image output
        #cv2.imwrite(f"{data.subject_name}_{data.animation_name}.png", current_location_image)

        # Store image
        data.image = current_location_image


    # Initialize stage occlusion mask
    occupancy_image = None
    if location_occupancy_mask is None:
        occupancy_image_mask = np.zeros((CV_IMAGESIZE, CV_IMAGESIZE), dtype=np.uint8)
        occupancy_image = cv2.cvtColor(occupancy_image_mask, cv2.COLOR_GRAY2BGR) * (0.0, 0.0, 0.0) # bgr
    else:
        occupancy_image_mask = location_occupancy_mask
        occupancy_image = cv2.cvtColor(occupancy_image_mask, cv2.COLOR_GRAY2BGR) * (0.0, 0.0, 1.0) # bgr

    # Find target locations
    for (index, data) in enumerate(location_data_areasorted):
        print(f"  Processing: {data.subject_name}_{data.animation_name}", file=sys.stderr)

        # Randomize position and yaw and check if leaving area boundary

        # Generate mask to check if animation is leaving the area boundary
        area_boundary_size = (CV_IMAGESIZE - 1) * 2 + 1
        area_boundary_mask = np.ones( (area_boundary_size, area_boundary_size), dtype=np.uint8) * 255

        center_x = round( (area_boundary_size-1) / 2 )
        safety_zone_width_pixels = round( (c.safety_zone_width / 100) * CV_M_TO_PIXELS)
        safety_start_x = center_x - round( safety_zone_width_pixels / 2 )
        safety_end_x = center_x + round( safety_zone_width_pixels / 2 )

        center_y = round( (area_boundary_size-1) / 2 )
        safety_zone_height_pixels = round( (c.safety_zone_height / 100) * CV_M_TO_PIXELS)
        safety_start_y = center_y - round( safety_zone_height_pixels / 2 )
        safety_end_y = center_y + round( safety_zone_height_pixels / 2 )

        cv2.rectangle(area_boundary_mask, (safety_start_x, safety_start_y), (safety_end_x, safety_end_y), 0, -1)
        #cv2.imwrite(f"area_boundary_mask.png", area_boundary_mask)

        target_image = None
        target_image_location_test_index = 1
        safety_zone_test_index = 1
        x_min = c.x_min
        x_max = c.x_max
        y_min = c.y_min
        y_max = c.y_max

        start_x = round((CV_IMAGESIZE-1)/2)
        start_y = start_x

        while target_image is None:
            if target_image_location_test_index % 5000 == 0:
                offset = 20
                x_min -= offset
                x_max += offset
                y_min -= offset
                y_max += offset
                print(f"  Increasing body area: Location trial={target_image_location_test_index}, x=[{x_min}, {x_max}], y=[{y_min}, {y_max}], safety_zone_test_index={safety_zone_test_index}", file=sys.stderr)
                if x_max > 500:
                    print(f"  WARNING: body area too large", file=sys.stderr)
                    return None

                target_image_location_test_index += 1 # prevent immediate retrigger if subsequent safety zone test fails

            # Give up if we cannot find safety zone location within reasonable time
            if safety_zone_test_index % 10000 == 0:
                print(f"  WARNING: Safety zone test failed: Zone trial={safety_zone_test_index}", file=sys.stderr)
                return None

            x = random.uniform(x_min, x_max)
            y = random.uniform(y_min, y_max)

            yaw = random.uniform(c.yaw_min, c.yaw_max)

            if body_yaw_reference is not None:
                body = f"{data.subject_name}_{data.animation_name}"
                body_yaw = body_yaw_reference[body]
                yaw = yaw + 90 + body_yaw # apply body yaw reference normalization, default Unreal body looks along Y-axis and needs yaw+=90 to face camera

            ground_trajectory_mask = np.zeros( (area_boundary_size, area_boundary_size), dtype=np.uint8)
            height, width = data.image.shape
            # Copy current template trajectory in larger mask at center
            ground_trajectory_mask[start_y:(start_y + height), start_x:(start_x + width)] = data.image


            ground_trajectory_mask_r_t = transform_image(ground_trajectory_mask, x, y, yaw)

            area_mask_test = cv2.bitwise_and(area_boundary_mask, ground_trajectory_mask_r_t)
            #cv2.imwrite(f"test_r_t_{index}_masked.png", area_mask_test)

            if not np.any(area_mask_test):
                target_image_location_test_index += 1
                # No overlap with outside boundary, we have valid area trajectory and can do occupancy overlap check next
                target_image = transform_image(data.image, x, y, yaw)

                occupancy_test = cv2.bitwise_and(occupancy_image_mask, target_image)
                if np.any(occupancy_test):
                    # Failed test, we are overlapping, need to try with new location
                    target_image = None
                    continue

                # Valid trajectory without occupancy overlap found
                data.x = x
                data.y = y
                data.yaw = yaw
                #cv2.imwrite(f"target_image.png", target_image)
                continue
            else:
                # Safety zone test failed
                safety_zone_test_index += 1

        # Color table (20 entries, generated with distinctipy)
        rgb_colors = [(0.9719224153972289, 0.0006387120046262851, 0.9572435498906621), (0.0, 1.0, 0.0), (0.0, 0.5, 1.0), (1.0, 0.5, 0.0), (0.5, 0.75, 0.5),
                      (0.30263956385061963, 0.02589151037218751, 0.6757257307743725), (0.8216012497248589, 0.0026428145851382645, 0.20847626796262153), (0.01267507572944171, 0.49697306807148534, 0.17396314179520123), (0.0, 1.0, 1.0), (0.9698728055826683, 0.5021762913810213, 0.7875501077376108),
                      (1.0, 1.0, 0.0), (0.0, 1.0, 0.5), (0.510314116241271, 0.3232218781514624, 0.09891582182150804), (0.520147512582225, 0.8462498714551937, 0.00708852231806234), (0.5022640147541273, 0.3238721132368306, 0.9748299235270517),
                      (0.5637646267468693, 0.7935494453374514, 0.9943913298776966), (0.9710018684130394, 0.8195424816067317, 0.46244870837979113), (0.26496132907909453, 0.38952992986967117, 0.5617810079535678), (0.0, 0.0, 1.0), (0.7026382639692401, 0.2676706088672629, 0.4941663340174245)]

        occupancy_image_mask = cv2.bitwise_or(occupancy_image_mask, target_image)

        (r, g, b) = rgb_colors[index % len(rgb_colors)]
        occupancy_image = occupancy_image + cv2.cvtColor(target_image, cv2.COLOR_GRAY2BGR) * (b, g, r) # bgr

        #cv2.imwrite(f"occupancy_image.png", occupancy_image)

    # Save accumulated ground trajectory image
    ground_trajectories = np.zeros( (area_boundary_size, area_boundary_size, 3), dtype=np.uint8)
    ground_trajectories[start_y:(start_y + height), start_x:(start_x + width)] = occupancy_image

    area_boundary_image = cv2.bitwise_not(cv2.cvtColor(area_boundary_mask, cv2.COLOR_GRAY2BGR))
    alpha = 0.25
    ground_trajectories = cv2.addWeighted(area_boundary_image, alpha, ground_trajectories, 1 - alpha, 0)

    output_root = OUTPUT_IMAGE_ROOT / grouptype / "ground_trajectories"
    output_root.mkdir(parents=True, exist_ok=True)
    output_image_path = output_root / f"ground_trajectories_{sequence_index:06d}.png"
#    cv2.imwrite(str(output_image_path), occupancy_image)
    cv2.imwrite(str(output_image_path), ground_trajectories)

    # Adjust sequence lengths for proper motion blur at beginning and end
    for data in location_data:
        # Due to Unreal (5.0.3) Alembic Python import bug the last frame is invalid and we need to skip it
        data.used_frames -= 1

        # For proper motion blur (temporal sampling) in Unreal we need to have valid data before and after each keyframe.
        # Increment start frame by one so that shortest sequence has a valid previous frame for image frame 0.
        data.start_frame += 1
        data.used_frames -= 1

        # Decrement end frame for proper temporal sampling on last image frame
        data.used_frames -= 1

    return location_data

def get_sequences(c, grouptype, subject_animations, animation_folder, body_yaw_reference, location_data, location_occupancy_masks, usage_subjects, usage_animations):
    num_sequences = c.num_sequences

    use_locations = False
    if (location_data is not None) and (len(location_data) > 0):
        use_locations = True

    sequences = []
    subjects = list(subject_animations.keys())

    if c.unique_sequences:
        input_subjects = list(subjects)
        input_subject_animations = copy.deepcopy(subject_animations)

    sequence_index = 0
    while sequence_index < num_sequences:
        print(f"Generating sequence: {sequence_index}", file=sys.stderr)
        num_subjects = random.randint(c.bodies_min, c.bodies_max)

        if c.unique_sequences:
            if len(subjects) < num_subjects:
                subjects = list(input_subjects)

        if not c.balance_subjects:
            current_subjects = list(subjects)
        else:
            current_subjects = [item for item in usage_subjects.keys() if item in subjects] # list is already sorted by count

        used_subjects = []
        used_animations = []

        location_occupancy_mask = None
        if use_locations:
            location_data_index = (sequence_index // c.location_sequences) % len(location_data)
            # Set safety zone size from location data
            size_x = float(location_data[location_data_index][5])
            size_y = float(location_data[location_data_index][6])
            # Stage size is specified in Unreal coordinates
            # Image represents top down stage view with image Y corresponding to Unreal X
            c = c._replace(safety_zone_width=size_y, safety_zone_height=size_x)

            stage_name = location_data[location_data_index][0]
            if stage_name in location_occupancy_masks:
                location_occupancy_mask = location_occupancy_masks[stage_name]

        for _ in range(num_subjects):
            # Select target subjects, avoid same subject in same sequence if requested
            # Note: We treat rp_aaron_posed_002 and rp_aaron_posed_009 as different subjects due to different clothing

            if not c.balance_subjects:
                current_subject_index = random.randint(0, len(current_subjects)-1)
            else:
                current_subject_index = 0 # list is sorted by usage count, first subject item has lowest usage count

            current_subject = current_subjects[current_subject_index]
            if c.unique_subjects:
                # Remove selected subject from current_subjects so that it will not be selected on following iterations
                current_subjects.remove(current_subject)

            used_subjects.append(current_subject)

            # Find animation for current subject
            if not c.balance_animations:
                if len(subject_animations[current_subject]) == 0:
                    subject_animations[current_subject] = list(input_subject_animations[current_subject])
            else:
                # Force the use of subject animation with lowest usage count
                selected_animation_index = None
                min_usage_count = None
                animations = input_subject_animations[current_subject]
                for animation_index in animations:

                    usage = int(usage_animations[f"{current_subject}_{animation_index}"])
                    if min_usage_count == None:
                        min_usage_count = usage
                        selected_animation_index = animation_index
                    elif usage < min_usage_count:
                        min_usage_count = usage
                        selected_animation_index = animation_index

                subject_animations[current_subject] = [selected_animation_index]
                usage_animations[f"{current_subject}_{selected_animation_index}"] = min_usage_count + 1 # update animation usage

            current_animations = subject_animations[current_subject]
            if c.unique_sequences:
                # No duplicated animations in current sequence
                if c.randomize_animations:
                    random.shuffle(current_animations)

                current_animation = current_animations.pop(0)

            else:
                # Animations can occur multiple times in current sequence
                if c.randomize_animations:
                    current_animation_index = random.randint(0, len(current_animations)-1)
                else:
                    current_animation_index = 0

                current_animation = current_animations[current_animation_index]

            used_animations.append(current_animation)

        # Get sequence bodies location data, sorted by ground area coverage, largest first
        subject_location_data = get_location_data(c, grouptype, sequence_index, used_subjects, used_animations, animation_folder, location_occupancy_mask, body_yaw_reference)
        if subject_location_data is not None:
            sequences.append( (f"seq_{sequence_index:06d}", subject_location_data) )
            sequence_index += 1

        if c.unique_sequences:
            # Remove used animations
            for index, used_subject in enumerate(used_subjects):
                used_animation = used_animations[index]
                if used_animation in subject_animations[used_subject]:
                    subject_animations[used_subject].remove(used_animation)

                if c.use_all_animations:
                    if len(subject_animations[used_subject]) == 0:
                        # Remove subject since it has no more available animations
                        subjects.remove(used_subject)
                elif c.unique_subjects:
                    subjects.remove(used_subject)

    return sequences


################################################################################
# Main
################################################################################
if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print(f"Usage: {sys.argv[0]} GROUPTYPE [HDRI_PATH]", file=sys.stderr)
        print(configs.keys())
        sys.exit(1)

    grouptype = sys.argv[1]
    if not grouptype in configs:
        print(f"ERROR: Undefined group type: {grouptype}", file=sys.stderr)
        sys.exit(1)
    c = configs[grouptype]

    whitelist_path = WHITELIST_PATH

    hdris_path = None
    if len(sys.argv) > 2:
        hdris_path = sys.argv[2]

    # Get list of whitelisted subject animations
    subject_animations = {}
    with open(whitelist_path) as f:
        subject_animations = json.load(f)

        # Remove subjects which do not have any animations
        subjects = list(subject_animations.keys())
        for subject in subjects:
            if len(subject_animations[subject]) == 0:
                print(f"WARNING: Removing subject without animations: {subject}", file=sys.stderr)
                del(subject_animations[subject])

    subjects = list(subject_animations.keys())

    hdris = None
    if hdris_path is not None:
        hdris = []
        # Get list of HDRI images
        with open(hdris_path) as f:
            hdris = f.read().splitlines()

    # Get subject gender information
    subject_gender = {}
    with open(SUBJECT_GENDER_PATH) as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            subject_gender[row["Name"]] = row["Gender"]

    # Get list of available body textures
    textures_body_female = []
    textures_body_male = []

    with open(TEXTURES_BODY_PATH) as f:
        lines = f.read().splitlines()
        for line in lines:
            if ("_f" in line) or ("Female_" in line):
                textures_body_female.append(line)
            else:
                textures_body_male.append(line)

    # Get list of available clothing textures
    outfit_textures = {}
    motion_outfit = {}
    with open(OUTFIT_INFO_PATH) as f:
        outfit_info = json.load(f)
        outfit_textures = outfit_info["textures"]
        motion_outfit = outfit_info["motions"]

    # Get gender hair whitelelist
    whitelist_hair = {}
    with open(WHITELIST_HAIR_PATH) as f:
        whitelist_hair = json.load(f)

    whitelist_hair_colors = []
    with open(WHITELIST_HAIRCOLORS_PATH) as f:
        lines = f.read().splitlines()
        for line in lines:
            whitelist_hair_colors.append(line)

    # Override world space offset if locations file is specified
    use_locations = False
    location_data = None
    location_occupancy_masks = None
    if c.location_file != "":
        use_locations = True
        location_data = []
        level_name = c.location_file.replace(".csv", "")
        location_file_path = LOCATIONS_ROOT / level_name / c.location_file
        with open(location_file_path, mode="r") as f:
            csv_reader = csv.reader(f)
            next(csv_reader) # skip header
            for row in csv_reader:
                location_data.append(row)

        # Initialize masks
        location_occupancy_masks = {}
        for data in location_data:
            stage_name = data[0]
            stage_index = stage_name.rsplit("_", maxsplit=1)[1]
            image_file_path = LOCATIONS_ROOT / level_name / f"{level_name}_stage_{stage_index}.png"
            if image_file_path.exists():
                img = cv2.imread(str(image_file_path), cv2.IMREAD_GRAYSCALE)
                if img is None:
                    print(f"ERROR: Could not load occupancy image: {image_file_path}", file=sys.stderr)
                    sys.exit(1)

                # Resize image and ensure binary mask (values either 0 or 255)
                img_resized = cv2.resize(img, (CV_IMAGESIZE, CV_IMAGESIZE), interpolation=cv2.INTER_NEAREST)

                # Exported PNG images are x-right, y-down, convert to internal representation (x-up, y-right)
                img_rotated = cv2.rotate(img_resized, cv2.ROTATE_90_COUNTERCLOCKWISE)
                _, img_binary = cv2.threshold(img_rotated, 127, 255, cv2.THRESH_BINARY)

                location_occupancy_masks[stage_name] = img_binary

    # Load usage statistics if subject or animation usage should be balanced
    usage_subjects = None
    if c.balance_subjects != "":
        usage_subjects_path = CONFIG_ROOT / c.balance_subjects
        with open(usage_subjects_path, mode="r") as f:
            usage_subjects = {}
            csv_reader = csv.DictReader(f)

            for row in csv_reader:
                usage_subjects[row["subject"]] = row["count"]

    usage_animations = None
    if c.balance_animations != "":
        usage_animations_path = CONFIG_ROOT / c.balance_animations
        with open(usage_animations_path, mode="r") as f:
            usage_animations = {}
            csv_reader = csv.DictReader(f)

            for row in csv_reader:
                usage_animations[row["animation"]] = row["count"]

    # Load body yaw reference if requested
    body_yaw_reference = None
    if c.use_body_yaw_reference:
        body_yaw_reference = {}
        with open(MOTION_STATS_PATH, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                body_id = row["body_id"]
                motion_id = row["motion_id"]
                body = f"{body_id}_{motion_id}"
                yaw =row["pelvis_world_yaw_deg"]
                body_yaw_reference[body] = float(yaw)

    whitelist_shoes = []
    shoe_height_offsets = {}
    if c.use_shoes:

        with open(WHITELIST_SHOES_PATH) as f:
            lines = f.read().splitlines()
            for line in lines:
                whitelist_shoes.append(line)

        with open(SHOE_OFFSETS_PATH, 'r') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                shoe_name = row["shoe_id"]
                height_offset = 100 * float(row["offset"]) # convert [m] to [cm]
                shoe_height_offsets[shoe_name] = height_offset

    # Get sequences
    sequences = get_sequences(c, grouptype, subject_animations, SMPLX_NPZ_ANIMATION_FOLDER, body_yaw_reference, location_data, location_occupancy_masks, usage_subjects, usage_animations)

    index = 0
    print("Index,Type,Body,X,Y,Z,Yaw,Pitch,Roll,Comment")
    comment = f"bodies_min={c.bodies_min};bodies_max={c.bodies_max};x_offset={c.x_offset};y_offset={c.y_offset};z_offset={c.z_offset};x_min={c.x_min};x_max={c.x_max};y_min={c.y_min};y_max={c.y_max};yaw_min={c.yaw_min};yaw_max={c.yaw_max}"
    print("%d,Comment,None,0,0,0,0,0,0,%s" % (index, comment))
    index = index + 1

    total_frames = 0

    # Ensure equal use of hair types over all sequences by not using hair from previous sequences if possible.
    current_hair = { 'f':[], 'm':[] }
    current_hair_colors = []

    current_shoes = []

    current_hdris = []

    for sequence_index, (sequence_name, subject_location_data) in enumerate(sequences):

        camera_radius_max = None
        camera_height_min = None
        camera_height_max = None
        theta_min = None
        theta_max = None

        if use_locations:
            location_data_index = (sequence_index // c.location_sequences) % len(location_data)
            # Set world offsets from location data
            x_offset = float(location_data[location_data_index][1])
            y_offset = float(location_data[location_data_index][2])
            z_offset = float(location_data[location_data_index][3])
            c = c._replace(x_offset=x_offset, y_offset=y_offset, z_offset=z_offset)

            if len(location_data[location_data_index])>=8:
                camera_radius_max = float(location_data[location_data_index][7])

            if len(location_data[location_data_index])>=9:
                camera_height_min = float(location_data[location_data_index][8])

            if len(location_data[location_data_index])>=10:
                camera_height_max = float(location_data[location_data_index][9])

            if len(location_data[location_data_index])>=11:
                theta_min = float(location_data[location_data_index][10])
                theta_max = float(location_data[location_data_index][11])


        sequence_frames = subject_location_data[0].used_frames
        total_frames += sequence_frames

        comment = f"sequence_name={sequence_name};frames={sequence_frames}"

        if hdris is not None:
            # Add random HDRI name to sequence information
            if len(current_hdris) == 0:
                current_hdris = list(hdris)
            hdri_name = current_hdris.pop(random.randrange(len(current_hdris)))
            comment += f";hdri={hdri_name}"

        if c.override_cameraroot_location:
            comment += f";cameraroot_x={c.x_offset};cameraroot_y={c.y_offset};cameraroot_z={c.z_offset}"

        if c.camera_hfov_deg > 0:
            comment += f";camera_hfov={c.camera_hfov_deg}"

        if camera_radius_max is not None:
            comment += f";camera_radius_max={camera_radius_max}"
        if camera_height_min is not None:
            comment += f";camera_height_min={camera_height_min}"
        if camera_height_max is not None:
            comment += f";camera_height_max={camera_height_max}"

        if theta_min is not None:
            comment += f";theta_min={theta_min};theta_max={theta_max}"

        comment += f";ground_height_world={c.z_offset}"

        if c.time_min > 0:
            time_of_day = random.uniform(c.time_min, c.time_max)
            comment += f";time={time_of_day}"

        print(f"{index},Group,None,0.0,0.0,{c.camera_height + c.z_offset},0.0,0.0,0.0,{comment}")
        index = index + 1

        current_textures_body_female = []
        current_textures_body_male = []

        for data in subject_location_data:
            comment = f"start_frame={data.start_frame}"

            # Randomize body texture, use each texture only once per sequence
            gender = subject_gender[data.subject_name]
            if gender == "f":
                if len(current_textures_body_female) == 0:
                    current_textures_body_female = list(textures_body_female)
                texture_body_name = current_textures_body_female.pop(random.randrange(len(current_textures_body_female)))
            elif gender == "m":
                if len(current_textures_body_male) == 0:
                    current_textures_body_male = list(textures_body_male)
                texture_body_name = current_textures_body_male.pop(random.randrange(len(current_textures_body_male)))
            else:
                print(f"ERROR: no gender definition for subject: {data.subject_name}", file=sys.stderr)
                sys.exit(1)

            comment += f";texture_body={texture_body_name}"

            # Randomize clothing texture
            if data.subject_name != "moyo": # MOYO does not use simulated clothing
                # Get outfit
                outfit = motion_outfit[data.subject_name][data.animation_name]
                textures = outfit_textures[outfit]
                texture_clothing_name = textures[random.randrange(len(textures))]
                comment += f";texture_clothing={outfit}_{texture_clothing_name}"

            if c.use_hair:
                # Randomize hair
                if len(current_hair[gender]) == 0:
                    current_hair[gender] = list(whitelist_hair[gender])

                hair_name = current_hair[gender].pop(random.randrange(len(current_hair[gender])))
                comment += f";hair={hair_name}"

                if len(current_hair_colors) == 0:
                    current_hair_colors = list(whitelist_hair_colors)
                hair_color = current_hair_colors.pop(random.randrange(len(current_hair_colors)))
                comment += f";haircolor={hair_color}"


            body = f"{data.subject_name}_{data.animation_name}"

            # Get shoe
            shoe_height_offset = 0.0
            if c.use_shoes:
                # Randomize shoe
                if len(current_shoes) == 0:
                    current_shoes = list(whitelist_shoes)

                shoe_name = current_shoes.pop(random.randrange(len(current_shoes)))
                comment += f";shoe={shoe_name}"
                shoe_height_offset = shoe_height_offsets[shoe_name]

            print(f"{index},Body,{body},{data.x + c.x_offset},{data.y + c.y_offset},{c.z_offset + shoe_height_offset},{data.yaw},0.0,0.0,{comment}")

            index = index + 1

    print(f"[INFO] Total frames in sequences: {total_frames}", file=sys.stderr)
