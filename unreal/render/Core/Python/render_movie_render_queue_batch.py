# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Render jobs in specified MovieRenderQueue
#
# Requirements:
#   Python Editor Script Plugin
#
from pathlib import Path
import re
import sys
import unreal

import render_status

# Globals
#output_dir = r"C:\bedlam\images\test"
movie_render_queue_root = "/Game/Bedlam/MovieRenderQueue/"

pipeline_executor = None

"""
    Summary:
        This function is called after the executor has finished
    Params:
        success - True if all jobs completed successfully.
"""
def OnQueueFinishedCallback(executor, success):

    unreal.log("Render queue completed. Success: " + str(success))

    # Delete our reference too so we don"t keep it alive.
    global pipeline_executor
    del pipeline_executor

    # Change global rendering state (queried by remote execution)
    render_status.rendering = False
    render_status.rendering_success = success

"""
    Summary:
        This function is called after each individual job in the queue is finished.
        At this point, PIE has been stopped so edits you make will be applied to the
        editor world.
"""
def OnIndividualJobFinishedCallback(job, success):

    unreal.log("Individual job completed: success=" + str(success))

    # Note: We store camera gt via EXR output
    # Logging via BE_GroundTruthLogger is no longer used due to its inabilty to log camera shakes

    # Export camera ground truth to .csv
    # sequence_name = job.job_name
    # export_camera_data(sequence_name)

    return

###############################################################################
# Main
###############################################################################
if __name__ == "__main__":

    unreal.log("BEDLAM: Batch rendering")
    if len(sys.argv) != 2:
        unreal.log_error("BEDLAM: Invalid command-line arguments. Usage: render_movie_render_queue_batch.py BATCH_INDEX")
        sys.exit(1)

    batch_index = int(sys.argv[1])

    unreal.log(f"  Batch index: {batch_index} ")

	# Load queue
    # /Script/MovieRenderPipelineCore.MoviePipelineQueue'/Game/Bedlam/MovieRenderQueue/MRQ_Batch_00.MRQ_Batch_00'
    mrq_path = f"/Script/MovieRenderPipelineCore.MoviePipelineQueue'{movie_render_queue_root}MRQ_Batch_{batch_index:02d}'"
    mrq = unreal.EditorAssetLibrary.load_asset(mrq_path)
    if not mrq:
        unreal.log_error(f"Cannot load MovieRenderQueue: {mrq_path}")
        sys.exit(1)

    movie_pipeline_queue_subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    pipeline_queue = movie_pipeline_queue_subsystem.get_queue()

    movie_pipeline_queue_subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
    pipeline_queue = movie_pipeline_queue_subsystem.get_queue()
    pipeline_queue.copy_from(mrq)

	# Process queue
    render_status.rendering = False

    if len(pipeline_queue.get_jobs()) == 0:
        unreal.log_error("No render jobs in MovieRenderQueue")
        sys.exit(1)
    else:
        # Change global rendering state (queried by remote execution)
        render_status.rendering = True

        # This renders the queue that the subsystem belongs with the PIE executor, mimicking Render (Local)
        pipeline_executor = movie_pipeline_queue_subsystem.render_queue_with_executor(unreal.MoviePipelinePIEExecutor)
        pipeline_executor.on_executor_finished_delegate.add_callable_unique(OnQueueFinishedCallback)
        pipeline_executor.on_individual_job_finished_delegate.add_callable_unique(OnIndividualJobFinishedCallback) # Only available on PIE Executor

    sys.exit(0)
