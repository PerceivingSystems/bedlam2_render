#!/usr/bin/env python
# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Batch import SMPL-X .fbx animations into Unreal using multiprocessing
#
# Notes:
# + Python for Windows: py -3 import_fbx_smplx_batch.py 20 10
#

from multiprocessing import Pool
import subprocess
import sys
import time

# Globals
IMPORT_SCRIPT_PATH = "C:/bedlam2/render/unreal/import/import_fbx_smplx.py" # need forward slashes when calling via -ExecutePythonScript

UNREAL_APP_PATH = r"C:\UE\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
UNREAL_PROJECT_PATH = r"C:\UE\Projects\5.3\BE_Import\BE_Import.uproject"
#UNREAL_APP_PATH = r"F:\UE\UE_5.3\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"
#UNREAL_PROJECT_PATH = r"F:\UE\Projects\5.3\BE_Import\BE_Import.uproject"

def worker(unreal_app_path, unreal_project_path, import_script_path, batch_index, num_batches):
    subprocess_args = [unreal_app_path, unreal_project_path, f"-ExecutePythonScript={import_script_path} {batch_index} {num_batches}"]
    print(subprocess_args)
    subprocess.run(subprocess_args)
    return True

def worker_args(args):
    return worker(*args)

################################################################################
# Main
################################################################################
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('Usage: %s NUM_BATCHES PROCESSES' % (sys.argv[0]), file=sys.stderr)
        sys.exit(1)

    num_batches = int(sys.argv[1])
    processes = int(sys.argv[2])

    print(f"Starting pool with {processes} processes, batches: {num_batches}\n", file=sys.stderr)
    pool = Pool(processes)

    start_time = time.perf_counter()
    tasklist = []
    for batch_index in range(num_batches):
        tasklist.append( (UNREAL_APP_PATH, UNREAL_PROJECT_PATH, IMPORT_SCRIPT_PATH, batch_index, num_batches) )

    result = pool.map(worker_args, tasklist)

    print(f"Finished. Total batch conversion time: {(time.perf_counter() - start_time):.1f}s")
