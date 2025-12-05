# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Render MovieRenderQueue batches sequentially via individual UnrealEditor instances.
# This prevents running of out memory when rendering many render jobs with large assets (HDRI, Alembic Clothing Simulations).
#
# Requirements:
#   + Enable Remote Execution in Project Settings>Plugins>Python
#   + remote_execution.py from Unreal Engine installation folder
#     + Copy UE_5.3\Engine\Plugins\Experimental\PythonScriptPlugin\Content\Python\remote_execution.py to same folder as this script
#
# Notes:
#   + Image output directory is already specified in MRQ assets
#
# Example: py -3 start_batch_render.py d:\UEProjects\5.3\BE_IBL
#

from pathlib import Path
import subprocess
import sys
import time

import remote_execution

# Globals
UNREAL_EDITOR_PATH = r"F:\UE\UE_5.3\Engine\Binaries\Win64\UnrealEditor.exe"

def render_batch(unreal_project_root, batch_index, num_batches):
    print("======================================================================")
    print(f"Rendering batch {(batch_index+1)} of {num_batches}")

    # Launch UnrealEditor
    print("Launching Unreal Editor")

    unreal_project_name = unreal_project_root.name
    unreal_path_uproject = unreal_project_root / f"{unreal_project_name}.uproject"

    # Check if project exists before starting Unreal Editor
    if not unreal_path_uproject.exists():
        print(f"[ERROR] Cannot find project file: {unreal_path_uproject}")
        sys.exit(1)

    command = [
        UNREAL_EDITOR_PATH,
        str(unreal_path_uproject),
#        UNREAL_LEVEL, # don't specify Level to load since it's already defined in MRQ render job
        "-windowed",
#        "-log",
#        "-StdOut",
#        "-allowStdOutLogVerbosity",
        "-Unattended",
        "-ResX=640",
        "-ResY=360",
        "-NoSplash",
        "-NoTextureStreaming"]

    unreal_process = subprocess.Popen(command)
    time.sleep(10)

    remote_execution.set_log_level(remote_execution._logging.DEBUG)

    print("Searching for Unreal Editor instance")
    remote_exec = remote_execution.RemoteExecution()
    remote_exec.start()

    # Connect to it
    remote_node_id = ""
    remote_exec.open_command_connection(remote_node_id)
    print("Connected to Unreal Editor")
    time.sleep(5)

    # Start movie render queue
    print(f"Starting MovieRenderQueue rendering via remote execution: batch_index={batch_index}")
    result = remote_exec.run_command(f"render_movie_render_queue_batch.py {batch_index}", exec_mode=remote_execution.MODE_EXEC_FILE)
    if not result["success"]:
        print("[ERROR] Cannot start MovieRenderQueue rendering")
        sys.exit(1)

    # Wait for movie rendering to be finished
    result = remote_exec.run_command("import render_status", exec_mode=remote_execution.MODE_EXEC_STATEMENT)

    rendering = True
    while rendering:
        result = remote_exec.run_command("render_status.rendering", exec_mode=remote_execution.MODE_EVAL_STATEMENT)
        if not result["success"]:
            print(f"[ERROR] {result}")
        else:
            rendering = ( (result["result"]) == "True" )
        time.sleep(10)

    # Rendering finished
    result = remote_exec.run_command("render_status.rendering_success", exec_mode=remote_execution.MODE_EVAL_STATEMENT)
    rendering_success = ( (result["result"]) == "True" )

    print(f"Movie rendering finished. Success: {rendering_success}")

    # Shutdown Unreal editor
    print("Closing Unreal Editor to free memory")
    result = remote_exec.run_command('unreal.SystemLibrary.execute_console_command(None, "QUIT_EDITOR")', exec_mode=remote_execution.MODE_EXEC_STATEMENT)
    remote_exec.stop()

    try:
        unreal_process.communicate(timeout=30)
    except subprocess.TimeoutExpired:
        print("[ERROR] Unreal Editor still open. Killing process.")
        unreal_process.kill()
        unreal_process.communicate()
    return

if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} UNREAL_PROJECT_ROOT")
        sys.exit(1)

    unreal_project_root = Path(sys.argv[1])

    # Determine number of available MovieRenderQueue assets
    mrq_root = Path(unreal_project_root) / "Content" / "Bedlam" / "MovieRenderQueue"
    mrq_files = mrq_root.glob("MRQ_Batch_*.uasset")
    num_batches = len(list(mrq_files))
    print(f"Unreal project directory: '{unreal_project_root}'")
    print(f"Number of MRQ assets: {num_batches}")

    for batch_index in range(num_batches):
        render_batch(unreal_project_root, batch_index, num_batches)

        print(f"Waiting 30s for memory release...")
        time.sleep(30) # wait for memory to be released

    sys.exit(0)
