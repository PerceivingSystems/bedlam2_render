#!/usr/bin/env python
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Plot camera ground truth data overviews for each sequence
#
# Requirements:
#   + seaborn
#
import json
from pathlib import Path
import sys

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def load_data(renderjob_path):
    data = {} # sequence name => data frame

    gt_path = renderjob_path / "ground_truth" / "meta_exr"

    sequence_paths = sorted(Path(gt_path).iterdir())

    for sequence_path in sequence_paths:
        data_x = []
        data_y = []
        data_z = []
        data_yaw = []
        data_pitch = []
        data_roll = []
        data_focallength = []
        data_hfov = []

        sequence_name = sequence_path.name

        json_paths = sorted(sequence_path.rglob("*.json"))
        for json_path in json_paths:

            with open(json_path, "r") as f:
                data_json = json.load(f)

                x = float(data_json["unreal/camera/curPos/x"])
                y = float(data_json["unreal/camera/curPos/y"])
                z = float(data_json["unreal/camera/curPos/z"])
                yaw = float(data_json["unreal/camera/curRot/yaw"])
                pitch = float(data_json["unreal/camera/curRot/pitch"])
                roll = float(data_json["unreal/camera/curRot/roll"])
                focallength = float(data_json["unreal/camera/FinalImage/focalLength"])
                hfov = float(data_json["unreal/camera/FinalImage/fov"])

                data_x.append(x)
                data_y.append(y)
                data_z.append(z)
                data_yaw.append(yaw)
                data_pitch.append(pitch)
                data_roll.append(roll)
                data_focallength.append(focallength)
                data_hfov.append(hfov)

        data_sequence = {
            "x": data_x,
            "y": data_y,
            "z": data_z,
            "yaw": data_yaw,
            "pitch": data_pitch,
            "roll": data_roll,
            "focallength" : data_focallength,
            "hfov" : data_hfov
        }

        df_sequence = pd.DataFrame(data_sequence)

        data[sequence_name] = df_sequence

    return data

def load_data_csv(renderjob_path):
    data = {} # sequence name => data frame

    gt_path = renderjob_path / "ground_truth" / "meta_exr_csv"

    csv_paths = sorted(Path(gt_path).rglob("*.csv"))

    for csv_path in csv_paths:
        sequence_name = csv_path.name.replace("_camera.csv", "")

        df = pd.read_csv(csv_path)
        data_sequence = {
                    "x": df["x"],
                    "y": df["y"],
                    "z": df["z"],
                    "yaw": df["yaw"],
                    "pitch": df["pitch"],
                    "roll": df["roll"],
                    "focallength": df["focal_length"],
                    "hfov": df["hfov"]
                }

        df_sequence = pd.DataFrame(data_sequence)

        data[sequence_name] = df_sequence

    return data

def plot_scatter_1(sequence_name, df, datatype, title, xlabel, ylabel, filename_prefix):
    sns.scatterplot(x=df.index, y=datatype, data=df)
    plt.title(f"{sequence_name} - {title}")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    output_path = renderjob_path / "overview" / "plots" / f"{filename_prefix}_{datatype}_{sequence_name}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.clf()

def plot_scatter_1_overview(data, datatype, title, xlabel, ylabel, filename_prefix):

    for sequence_name in data:
        df = data[sequence_name]
        sns.scatterplot(x=df.index, y=datatype, data=df)

    plt.title(f"{title}")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    output_path = renderjob_path / "overview" / "plots" / f"{filename_prefix}_{datatype}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.clf()

def plot_scatter_2(sequence_name, df, datatype_x, datatype_y, title, xlabel, ylabel, filename_prefix):
    sns.scatterplot(x=datatype_x, y=datatype_y, data=df)
    plt.title(f"{sequence_name} - {title}")
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.axis("square") # ensure square data plot with same x/y axis range differences
    plt.tight_layout()

    output_path = renderjob_path / "overview" / "plots" / f"{filename_prefix}_{datatype_x}_{datatype_y}_{sequence_name}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    plt.clf()

if __name__ == "__main__":
    if (len(sys.argv) < 2) or (len(sys.argv) > 3):
        print("Usage: %s RENDERJOB_FOLDER [json]" % (sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    renderjob_path = Path(sys.argv[1])
    use_csv_ground_truth = True # use CSV camera ground truth by default
    if len(sys.argv) > 2:
        use_csv_ground_truth = False

    if use_csv_ground_truth:
        data = load_data_csv(renderjob_path)
    else:
        data = load_data(renderjob_path)

    sns.set(style="whitegrid")

    for sequence_name in data:
        print(f"Plotting sequence data: {sequence_name}")

        df = data[sequence_name]
        plot_scatter_2(sequence_name, df, "y", "x", f"World YX (UE)", "Y [cm]", "X [cm]", "camera_loc")
        plot_scatter_1(sequence_name, df, "z", f"World Height (UE)", "Frame", "Height [cm]", "camera_loc")
#        plot_scatter_1(sequence_name, df, "yaw", f"World Yaw (UE)", "Frame", "Angle [deg]", "camera_rot")
#        plot_scatter_1(sequence_name, df, "pitch", f"World Pitch (UE)", "Frame", "Angle [deg]", "camera_rot")
#        plot_scatter_1(sequence_name, df, "roll", f"World Roll (UE)", "Frame", "Angle [deg]", "camera_rot")

    plot_scatter_1_overview(data, "yaw", f"World Yaw (UE)", "Frame", "Angle [deg]", "camera_rot")
    plot_scatter_1_overview(data, "pitch", f"World Pitch (UE)", "Frame", "Angle [deg]","camera_rot")
    plot_scatter_1_overview(data, "roll", f"World Roll (UE)", "Frame", "Angle [deg]", "camera_rot")
    plot_scatter_1_overview(data, "focallength", f"Focal Length", "Frame", "Focal Length [mm]", "camera_intrinsics")
    plot_scatter_1_overview(data, "hfov", f"HFOV", "Frame", "HFOV [deg]", "camera_intrinsics")
