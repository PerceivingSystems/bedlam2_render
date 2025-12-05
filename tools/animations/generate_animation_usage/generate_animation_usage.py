#!/usr/bin/env python
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Generate animation usage of specified renderjobs
#
import json
from pathlib import Path
import sys
import tarfile

# Globals
USAGE_ANIMATIONS_PATH = Path("usage_animations.csv")
USAGE_SUBJECTS_PATH = Path("usage_subjects.csv")

def process_tgz_gt(animation_usage, source_root):

    tgz_filepaths = sorted(source_root.rglob("*_meta_csv.tar.gz"))

    for tgz_filepath in tgz_filepaths:
        print(f"Processing: {tgz_filepath}", file=sys.stderr)

        csv_data = []
        with tarfile.open(tgz_filepath, "r:gz") as tar:
            try:
                centersubframe = ""
                if "centersubframe" in tgz_filepath.name:
                    centersubframe = "centersubframe_"

                renderjob = tgz_filepath.name.replace(f"_gt_{centersubframe}exr_meta_csv.tar.gz", "")
                member = tar.getmember(f"{renderjob}/be_seq.csv")
                file = tar.extractfile(member)

                if file:
                    file_contents = file.read().decode("utf-8")
                    csv_data = file_contents.split("\n")

            except KeyError:
                print(f"ERROR: {renderjob}/be_seq.csv not found in the archive")
                sys.exit(1)

        process_csv_data(animation_usage, renderjob, csv_data)

    return True

def process_csv_data(animation_usage, renderjob, csv_data):
    for line in csv_data:
        if len(line) == 0:
            continue

        data = line.split(",")
        if data[1] != "Body":
            continue

        animation = data[2]

        if animation not in animation_usage:
            animation_usage[animation] = { "count": 1, "renderjobs": [renderjob] }
        else:
            usage_count = animation_usage[animation]["count"]
            animation_usage[animation]["count"] = usage_count + 1
            if renderjob not in animation_usage[animation]["renderjobs"]:
                animation_usage[animation]["renderjobs"].append(renderjob)
    return True

################################################################################
# Main
################################################################################

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} /path/to/source_csv_tgz /path/to/whitelist_animations_json")
    print(f"       {sys.argv[0]} ./gt/ ../../../config/whitelist_animations_b2v1.json")
    sys.exit(1)

source_root = Path(sys.argv[1])
whitelist_animations = Path(sys.argv[2])

# Initialize animation usage to zero based on selected animation whitelist
animation_usage = {}

with open(whitelist_animations) as f:
    subject_animations = json.load(f)
    for subject in subject_animations:
        for animation_index in subject_animations[subject]:
            animation = f"{subject}_{animation_index}"
            animation_usage[animation] = { "count": 0, "renderjobs": [] }

process_tgz_gt(animation_usage, source_root)

# Output animation usage CSV sorted by increasing count
with open(USAGE_ANIMATIONS_PATH, "w") as f:

    animation_usage_sorted = dict(sorted(animation_usage.items(), key=lambda item: item[1]["count"]))

    line = "animation,count,renderjobs"
 #   print(line)
    f.write(line + "\n")
    for animation in animation_usage_sorted:
        count = animation_usage_sorted[animation]["count"]
        renderjobs = sorted(animation_usage_sorted[animation]["renderjobs"])
        renderjobs_text = ""
        for index, renderjob in enumerate(renderjobs):
            if index == 0:
                renderjobs_text = renderjob
            else:
                renderjobs_text += f"|{renderjob}"

        line = f"{animation},{count},{renderjobs_text}"
#        print(line)
        f.write(line + "\n")
    print(f"Saving: {USAGE_ANIMATIONS_PATH}", file=sys.stderr)

# Output subject usage CSV sorted by increasing count
with open(USAGE_SUBJECTS_PATH, "w") as f:

    subject_usage = {}
    for animation in animation_usage:
        if animation.startswith("moyo"):
            subject = "moyo"
        else:
            subject = animation.rsplit("_", maxsplit=1)[0]

        if subject not in subject_usage:
            subject_usage[subject] = { "count": 0, "renderjobs": [] }

        subject_count = subject_usage[subject]["count"]
        subject_usage[subject]["count"] = subject_count + animation_usage[animation]["count"]

        renderjobs = animation_usage[animation]["renderjobs"]
        for renderjob in renderjobs:
            if renderjob not in subject_usage[subject]["renderjobs"]:
                subject_usage[subject]["renderjobs"].append(renderjob)


    subject_usage_sorted = dict(sorted(subject_usage.items(), key=lambda item: item[1]["count"]))

    line = "subject,count,renderjobs"
 #   print(line)
    f.write(line + "\n")
    for subject in subject_usage_sorted:
        count = subject_usage_sorted[subject]["count"]
        renderjobs = sorted(subject_usage_sorted[subject]["renderjobs"])
        renderjobs_text = ""
        for index, renderjob in enumerate(renderjobs):
            if index == 0:
                renderjobs_text = renderjob
            else:
                renderjobs_text += f"|{renderjob}"

        line = f"{subject},{count},{renderjobs_text}"
#        print(line)
        f.write(line + "\n")
    print(f"Saving: {USAGE_SUBJECTS_PATH}", file=sys.stderr)

sys.exit(0)