#!/usr/bin/env python3
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Body part segmentation masks (greyscale PNG) and camera ground truth (JSON) from Unreal Movie Render Queue raw 32-bit exr output file
#
# Generated EXR needs to be rendered without motion blur and antialiasing so that we have no partial coverage for the body parts and can use binary masks.
#
# Requirements:
# + OpenEXR (1.3.9)
#   + Installation
#     + sudo apt install build-essential
#     + sudo apt install python3-dev
#     + sudo apt install libopenexr-dev
#     + pip install OpenEXR
#
# + OpenCV (4.7.0.72)
#   + PNG export
#   + Installation: pip install opencv-python-headless
#
# References:
#   + https://github.com/Psyop/Cryptomatte
#   + https://github.com/Synthesis-AI-Dev/exr-info
#

import OpenEXR
import Imath

import cv2
import json
from multiprocessing import Pool
import numpy as np
from pathlib import Path
import struct
import sys
import time

# Globals
DEFAULT_PROCESSES = 16
FOLDER_MASK_PREFIX = "BEDLAM/masks/"

def process(input_exr, mask_type):
    output_dir = input_exr.parent.parent.parent
    exr = OpenEXR.InputFile(str(input_exr))

    if mask_type == "masks":
        meta_output_path = output_dir / "ground_truth" / "meta_exr" / input_exr.parent.name / input_exr.name.replace(".exr", "_meta.json")
        status = process_meta(exr, meta_output_path)
        if not status:
            exr.close()
            return False

    masks_output_path = output_dir / "exr_layers" / mask_type / input_exr.parent.name / input_exr.name
    status = process_masks(exr, masks_output_path)
    if not status:
        exr.close()
        return False

    exr.close()
    return True

def process_args(args):
    return process(*args)

def process_meta(exr, output_path):

    print("Extracting meta information")
    if (output_path.exists()):
        print(f"  Skipping. File exists: {output_path}")
        return True

    header = exr.header()

    meta = {}
    for key in header.keys():
        if key.startswith("unreal/"):
            if "ActorHitProxyMask" in key:
                continue

            meta[key] = header[key].decode()

    if len(meta) == 0:
        print(f"ERROR: No Unreal meta information found in EXR file")
        return False

    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"  Exporting: {output_path}")
    with open(output_path, "w") as f:
        json.dump(meta, f, indent=4)

    return True

def process_masks(exr, output_path):

    print("Extracting segmentation masks")
    export_path = str(output_path).replace(".exr", "_env.png")
    if (Path(export_path).exists()):
        print(f"  Skipping. File exists: {export_path}")
        return True

    # Find cryptomatte information
    header = exr.header()
    pixel_type = header["channels"]["ActorHitProxyMask00.R"].type
    if pixel_type != Imath.PixelType(Imath.PixelType.FLOAT):
        print(f"ERROR: Invalid pixel type: {pixel_type}")
        return False

    image_size = (header["dataWindow"].max.x - header["dataWindow"].min.x + 1, header["dataWindow"].max.y - header["dataWindow"].min.y + 1)

    cryptomatte_key = None
    cryptomatte_name = None

    for key in header.keys():
        # cryptomatte/3fd1687/name
        if "cryptomatte" in key:
            if key.endswith("name"):
                cryptomatte_key = key.split("/")[1]
                cryptomatte_name = header[key].decode()
                break

    if cryptomatte_key is None:
        print("ERRROR: Cannot find cryptomatte name in file", file=sys.stderr)
        return False
    else:
        print(f"  Cryptomatte information found: key={cryptomatte_key}, name={cryptomatte_name}")

    manifest = json.loads(header[f"cryptomatte/{cryptomatte_key}/manifest"])
    actor_names = []
    for key in manifest.keys():
        key = key.replace(FOLDER_MASK_PREFIX, "") # Remove folder name prefix for generated masks from World Partition maps
        if key.startswith("be_actor_"):
            actor_name = key.rsplit("_", maxsplit=1)[0]
            if actor_name not in actor_names:
                actor_names.append(actor_name)

    actor_names.sort()

    # Get cryptomatte channel data
    # ID levels: R and B
    # Since we render without motion blur/antialiasing we ignore the coverage values and use simple binary mask
    data_id = []
    for layer_index in range(0,3):
        for channel_id in ["R", "B"]:
            channel_name = f"ActorHitProxyMask{layer_index:02}.{channel_id}"
            #print(f"  Loading channel data: {channel_name}")
            data_exr = exr.channel(channel_name)
            data_np = np.frombuffer(data_exr, dtype=np.float32)
            data_id.append(data_np)

    """
    # Coverage levels: G and A
    data_coverage = []
    for layer_index in range(0,3):
        for channel_id in ["G", "A"]:
            channel_name = f"ActorHitProxyMask{layer_index:02}.{channel_id}"
            print(f"  Loading: {channel_name}")
            data_exr = exr.channel(channel_name)
            data_np = np.frombuffer(data_exr, dtype=np.float32)
            data_coverage.append(data_np)
    """

    if not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # Export environment mask
    mask_names = []
    for key in manifest.keys():
        # Append all keys which are not body/clothing/hair
        if "be_actor_" not in key:
            mask_names.append(key)

    print(mask_names, export_path)
    status = export_mask(exr, mask_names, manifest, data_id, image_size, export_path)
    if not status:
        # Default mask should always be generated even if body/clothing fully covers camera which leads to fully black mask.
        print(f"ERROR: Cannot find data for desired mask names: {mask_names}, {output_path}", file=sys.stderr)
        return False

    # Export actor masks for body, clothing (optional), hair (optional)
    for index, actor_name in enumerate(actor_names):
        for item in ["body", "clothing", "hair"]:
            mask_name = f"{actor_name}_{item}"
            folder_mask_name = f"{FOLDER_MASK_PREFIX}{mask_name}"
            if mask_name in manifest.keys() or folder_mask_name in manifest.keys():
                if mask_name in manifest.keys():
                    target_mask_name = mask_name
                else:
                    target_mask_name = folder_mask_name

                export_path = str(output_path).replace(".exr", f"_{index:02}_{item}.png")
                status = export_mask(exr, [target_mask_name], manifest, data_id, image_size, export_path)
                if not status:
                    # Actor mask will not exist if actor is out of camera frame. We just issue a warning instead of aborting.
                    print(f"WARNING: Cannot find body/clothing data for desired mask name (out of camera frame): {target_mask_name}, {output_path}")

    return True

def export_mask(exr, mask_names, manifest, data_id, image_size, output_path):

    rank_objectid_binary_mask = None
    for mask_name in mask_names:
        print(f"  Exporting: {mask_name}: {output_path}")

        # Get object ID in float32 format
        # Note: Object ID needs to be interpreted as big-endian so that resulting float matches the data in the ID ranks.
        #       This differs from official spec which uses platform byte-order which would be little-endian.
        #       A similar approach is taken here: https://github.com/Synthesis-AI-Dev/exr-info/blob/04a51b3b943c05db6a94774c710258070d19e69a/exr_info/cryptomatte.py#L51
        object_id_hex = manifest[mask_name]
        object_id_float = struct.unpack(">f", bytes.fromhex(object_id_hex))[0]

        num_ranks = len(data_id)
        for rank_index in range(num_ranks):
            rank_data_id = data_id[rank_index]

            # Skip checks if current rank has no data
            if not np.any(rank_data_id):
                continue

            rank_objectid_found = rank_data_id[:] == object_id_float # Generate binary mask, True if pixel float value matches object id float

            if np.any(rank_objectid_found):
                if rank_objectid_binary_mask is None:
                    rank_objectid_binary_mask = rank_objectid_found
                else:
                    # OR with current data
                    rank_objectid_binary_mask = np.logical_or(rank_objectid_binary_mask, rank_objectid_found)

                break # we don't process other ranks if we found one since we only handle binary masks

    if rank_objectid_binary_mask is not None:
        image_data = rank_objectid_binary_mask.reshape( (image_size[1], image_size[0]) )
        image_data = image_data.astype(np.uint8)
        image_data *= 255
        cv2.imwrite(output_path, image_data, [cv2.IMWRITE_PNG_COMPRESSION, 9]) # write as greyscale PNG with max compression
        return True

    # Environment mask might be zero if body/clothing fully covers it. Write black image in this case to ensure that we always have an environment mask.
    if "default" in mask_names:
        image_data = np.zeros((image_size[1], image_size[0]), dtype=np.uint8)
        cv2.imwrite(output_path, image_data, [cv2.IMWRITE_PNG_COMPRESSION, 9]) # write as greyscale PNG with max compression
        return True

    return False

def print_usage():
    print("Usage: %s MASK_TYPE INPUT_EXR" % (sys.argv[0]), file=sys.stderr) # single file mode, input ends with .exr
    print("Usage: %s MASK_TYPE INPUT_EXR_DIR [NUM_PROCESSES]" % (sys.argv[0]), file=sys.stderr) # batch mode
    print("Supported MASK TYPE values:", file=sys.stderr)
    print("  masks (will also export camera ground truth metadata)", file=sys.stderr)
    print("  body_correspondence_masks", file=sys.stderr)

################################################################################
# Main
################################################################################
if __name__ == "__main__":
    if (len(sys.argv) < 3) or (len(sys.argv) > 4):
        print_usage()
        sys.exit(1)

    mask_type = sys.argv[1]
    if (mask_type != "masks") and (mask_type != "body_correspondence_masks"):
        print(f"ERROR: invalid TYPE: {mask_type}", file=sys.stderr)
        print_usage()
        sys.exit(1)

    input_exr = Path(sys.argv[2])

    processes = DEFAULT_PROCESSES
    if len(sys.argv) >= 3:
        processes = int(sys.argv[3])

    batch_mode = False
    if input_exr.is_dir():
        batch_mode = True

    start_time = time.perf_counter()

    if not batch_mode:
        # Process single EXR file
        results = [process(input_exr, mask_type)]
    else:
        # Batch mode
        input_exr_files = sorted(input_exr.rglob("*.exr"))
        tasklist = []
        for input_exr_file in input_exr_files:
            tasklist.append( (input_exr_file, mask_type) )

        print(f"Starting pool with {processes} processes\n")
        pool = Pool(processes)
        results = pool.map(process_args, tasklist)

    if False not in results:
        print("EXR processing finished successfully.", file=sys.stderr)
        print(f"  Total conversion time: {(time.perf_counter() - start_time):.1f}s", file=sys.stderr)
    else:
        print("ERROR: EXR processing errors.", file=sys.stderr)
        sys.exit(1)
