#!/usr/bin/env python
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Batch generate LevelSequences via individual Editor instances to avoid out-of-memory situations
#
# Notes:
# + Python for Windows: py -3 level_sequence_batch.py PATH_TO_CSV PATH_TO_UPROJECT /Game/Bedlam/MAPNAME SEQUENCES_PER_BATCH
#                       py -3 level_sequence_batch.py C:\bedlam2\images\test\be_seq.csv C:\UE\UEProjects\5.3\BE_IBL\BE_IBL.uproject /Game/Bedlam/IBLMap 100
#

from pathlib import Path
import subprocess
import sys
import time

# Globals, adjust to match your Unreal Engine installation folder
IMPORT_SCRIPT_PATH = "C:/UE/UE_5.3/Engine/Content/PS/Bedlam/Core/Python/create_level_sequences_csv.py" # need forward slashes when calling via -ExecutePythonScript
UNREAL_APP_PATH = r"C:\UE\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
#IMPORT_SCRIPT_PATH = "F:/UE/UE_5.3/Engine/Content/PS/Bedlam/Core/Python/create_level_sequences_csv.py" # need forward slashes when calling via -ExecutePythonScript
#UNREAL_APP_PATH = r"F:\UE\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"

################################################################################
# Main
################################################################################
if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(f"Usage: py -3 {sys.argv[0]} PATH_TO_CSV PATH_TO_UPROJECT /Game/Bedlam/MAPNAME SEQUENCES_PER_BATCH", file=sys.stderr)
        sys.exit(1)

    csv_path = sys.argv[1].replace("\\", "/") # needs forward slashes when used as parameter for -ExecutePythonScript
    unreal_project_path = sys.argv[2]
    unreal_map_path = sys.argv[3]
    sequences_per_batch = int(sys.argv[4])

    # Get number of sequences
    num_sequences = 0
    with open(csv_path, "r") as f:
        for line in f:
            if "Group" in line:
                num_sequences += 1

    sequence_index_start = 0
    sequence_index_end = 0

    start_time = time.perf_counter()

    finished = False
    while not finished:
        sequence_index_end = sequence_index_start + sequences_per_batch - 1
        if sequence_index_end >= (num_sequences - 1):
            sequence_index_end = (num_sequences - 1)
            finished = True

        print(f"Processing: [{sequence_index_start}, {sequence_index_end}]")
        subprocess_args = [UNREAL_APP_PATH, unreal_project_path, unreal_map_path, f"-ExecutePythonScript={IMPORT_SCRIPT_PATH} {csv_path} Default {sequence_index_start} {sequence_index_end}"]
        print(f"  {subprocess_args}")
        subprocess.run(subprocess_args)

        sequence_index_start += sequences_per_batch

        if not finished:
            wait_time_s = 10
            print(f"  Waiting {wait_time_s}s for memory release...")
            time.sleep(wait_time_s) # wait for memory to be released

    print(f"Finished. Total batch conversion time: {(time.perf_counter() - start_time):.1f}s")
