#!/usr/bin/env python
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Generate new body whitelist based on filter criteria
#
import json
import pandas as pd
from pathlib import Path
import sys

def process_csv(csv_path, range_min_cm, range_max_cm, batch_id, pelvis_height_min_cm):

    range_min = float(range_min_cm) / 100
    range_max = float(range_max_cm) / 100
    height_min = float(pelvis_height_min_cm) / 100

    df = pd.read_csv(csv_path)
    df_filtered = df[ (df['pelvis_height_min'] >= height_min) & (df['ground_coverage_x'] >= range_min) & (df['ground_coverage_z'] >= range_min) & (df['ground_coverage_x'] <= range_max) & (df['ground_coverage_z'] <= range_max)]
    df_filtered = df_filtered.sort_values(by="body_id")

    whitelist_subjects = {}
    for _, row in df_filtered.iterrows():
        body_id = row["body_id"]
        motion_id = str(row["motion_id"])
        if body_id not in whitelist_subjects:
            whitelist_subjects[body_id] = [ motion_id ]
        else:
            motions = whitelist_subjects[body_id]
            motions.append(motion_id)
            whitelist_subjects[body_id] = sorted(motions)

    height_suffix = ""
    if pelvis_height_min_cm > 0:
        height_suffix = f"_{pelvis_height_min_cm}"
    target_path = Path(".") / f"whitelist_animations_{batch_id}_{range_min_cm}_{range_max_cm}{height_suffix}.json"
    print(f"Saving: {target_path}")
    with open(target_path, "w") as json_file:
        json.dump(whitelist_subjects, json_file, indent=4)

    unique_bodies = df_filtered["body_id"].nunique()
    print(f"Number of bodies: {unique_bodies}")
    print(f"Number of motions: {len(df_filtered)}")

    return True

################################################################################
# Main
################################################################################

if (len(sys.argv) < 5) or (len(sys.argv) > 6):
    print(f"Usage: {sys.argv[0]} GROUND_COVERAGE_CSV_PATH MINRANGE_CM MAXRANGE_CM BATCH_ID [PELVIS_HEIGHT_MIN_CM]")
    print(f"       {sys.argv[0]} ../../../stats/motion_stats_b2v4.csv 1 20 b2v4 80")
    sys.exit(1)

csv_path = Path(sys.argv[1])
range_min_cm = int(sys.argv[2])
range_max_cm = int(sys.argv[3])
batch_id = sys.argv[4]
pelvis_height_min = 0.0
if len(sys.argv) >= 6:
    pelvis_height_min = int(sys.argv[5])

process_csv(csv_path, range_min_cm, range_max_cm, batch_id, pelvis_height_min)

sys.exit(0)
