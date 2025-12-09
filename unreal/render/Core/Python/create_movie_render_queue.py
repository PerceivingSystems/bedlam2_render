# Copyright (c) 2025 Max Planck Society
# License: https://bedlam2.is.tuebingen.mpg.de/license.html
#
# Generates MovieRenderQueue render jobs for selected Content Browser LevelSequences
#
# Requirements:
#   Plugins:
#     + Python Editor Script Plugin
#     + Movie Render Queue
#     + Movie Render Queue Additional Render Passes (for segmentation masks)
#
import sys
import time
import unreal

# Globals
output_dir = r"C:\bedlam2\images\test"
data_root_unreal = "/Engine/PS/Bedlam/Core/Materials/MovieRenderQueue/"
movie_render_queue_root = "/Game/Bedlam/MovieRenderQueue/"
movie_render_queue_template = "/Engine/PS/Bedlam/Core/MovieRenderQueue/MRQ_Template"
material_cameranormal = data_root_unreal + "MovieRenderQueue_CameraNormal"
material_worldnormal = data_root_unreal + "MovieRenderQueue_WorldNormal"

def add_render_job(pipeline_queue, level_sequence_data, output_frame_step, image_size, spatial_samples, temporal_samples):
	global output_dir

	level_sequence_name = str(level_sequence_data.asset_name)
	# Create new movie pipeline job and set job parameters
	job = pipeline_queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
	job.set_editor_property('job_name', level_sequence_name)

	# Note: Setting sequence will immediately load LevelSequence into memory in order to to retrieve shot list from sequence.
	#       See UMoviePipelineExecutorJob::SetSequence() implementation for details.
	job.set_editor_property('sequence', level_sequence_data.to_soft_object_path())

	current_level = unreal.EditorLevelUtils.get_levels(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world())[0]
	map_path = unreal.SystemLibrary.get_path_name(unreal.SystemLibrary.get_outer_object(current_level))
	job.set_editor_property('map', unreal.SoftObjectPath(map_path))

	job.set_editor_property('author', "BEDLAM")

	# Set output type PNG
	jpg_setting = job.get_configuration().find_setting_by_class(unreal.MoviePipelineImageSequenceOutput_JPG)
	if jpg_setting is not None:
		job.get_configuration().remove_setting(jpg_setting)
	job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)

	output_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)

	output_directory = output_dir + "\\png\\{sequence_name}"
	file_name_format = "{sequence_name}_{frame_number}"

	output_setting.output_directory = unreal.DirectoryPath(output_directory)
	output_setting.file_name_format = file_name_format

	output_setting.output_resolution = unreal.IntPoint(image_size[0], image_size[1])

	output_setting.zero_pad_frame_numbers = 4
	output_setting.output_frame_step = output_frame_step

	# Anti-aliasing
	antialiasing_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)

	antialiasing_setting.spatial_sample_count = spatial_samples

	# Use 7 when using temporal samples instead of 8 to get sample on keyframe for default frame center shutter mode
	# https://dev.epicgames.com/community/learning/tutorials/GxdV/unreal-engine-demystifying-sampling-in-movie-render-queue
	antialiasing_setting.temporal_sample_count = temporal_samples

	antialiasing_setting.override_anti_aliasing = True
	antialiasing_setting.anti_aliasing_method = unreal.AntiAliasingMethod.AAM_NONE

	# Ensure proper Lumen warmup at frame 0, especially when rendering with frame skipping (6 fps)
	antialiasing_setting.render_warm_up_frames = True
	antialiasing_setting.engine_warm_up_count = 32

	# Deferred renderer
	deferred_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)

# Setup EXR render job for image pass with embedded ground truth camera information, 16-bit EXR with ZIP compression and additional PNG pass
def add_render_job_exr_image(pipeline_queue, level_sequence_data, output_frame_step, image_size, spatial_samples, temporal_samples):
	global output_dir

	level_sequence_name = str(level_sequence_data.asset_name)
	# Create new movie pipeline job and set job parameters
	job = pipeline_queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
	job.set_editor_property('job_name', level_sequence_name + "_exr")

	# Note: Setting sequence will immediately load LevelSequence into memory in order to to retrieve shot list from sequence.
	#       See UMoviePipelineExecutorJob::SetSequence() implementation for details.
	job.set_editor_property('sequence', level_sequence_data.to_soft_object_path())

	current_level = unreal.EditorLevelUtils.get_levels(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world())[0]
	map_path = unreal.SystemLibrary.get_path_name(unreal.SystemLibrary.get_outer_object(current_level))
	job.set_editor_property('map', unreal.SoftObjectPath(map_path))

	job.set_editor_property('author', "BEDLAM")

	# Set output types
	jpg_setting = job.get_configuration().find_setting_by_class(unreal.MoviePipelineImageSequenceOutput_JPG)
	if jpg_setting is not None:
		job.get_configuration().remove_setting(jpg_setting)

	# Add PNG output. It is faster to output EXR+PNG at the same time since EXR=>PNG in post can take as long as render time.
	job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_PNG)

	# Add EXR output
	exr_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_EXR)
	exr_setting.compression = unreal.EXRCompressionFormat.ZIP # better compression than PIZ for sample test render, also faster decompression than PIZ
	exr_setting.multilayer = True # needed for camera ground truth data

	output_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)

	output_directory = output_dir + "\\exr_image\\{sequence_name}"
	file_name_format = "{sequence_name}_{frame_number}"

	output_setting.output_directory = unreal.DirectoryPath(output_directory)
	output_setting.file_name_format = file_name_format

	output_setting.output_resolution = unreal.IntPoint(image_size[0], image_size[1])

	output_setting.zero_pad_frame_numbers = 4
	output_setting.output_frame_step = output_frame_step

	# Anti-aliasing: Disable for depth/mask rendering
	antialiasing_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)

	antialiasing_setting.spatial_sample_count = spatial_samples
	antialiasing_setting.temporal_sample_count = temporal_samples
	antialiasing_setting.override_anti_aliasing = True
	antialiasing_setting.anti_aliasing_method = unreal.AntiAliasingMethod.AAM_NONE

	# Ensure proper Lumen warmup at frame 0, especially when rendering with frame skipping (6 fps)
	antialiasing_setting.render_warm_up_frames = True
	antialiasing_setting.engine_warm_up_count = 32

	# Deferred renderer
	deferred_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)

# Setup EXR render job for generating depth map, segmentation masks, normals (optional)
def add_render_job_exr_depthmask(pipeline_queue, level_sequence_data, output_frame_step, image_size, normals_type):
	global output_dir

	level_sequence_name = str(level_sequence_data.asset_name)
	# Create new movie pipeline job and set job parameters
	job = pipeline_queue.allocate_new_job(unreal.MoviePipelineExecutorJob)
	job.set_editor_property('job_name', level_sequence_name + "_exr_depth")

	# Note: Setting sequence will immediately load LevelSequence into memory in order to to retrieve shot list from sequence.
	#       See UMoviePipelineExecutorJob::SetSequence() implementation for details.
	job.set_editor_property('sequence', level_sequence_data.to_soft_object_path())

	current_level = unreal.EditorLevelUtils.get_levels(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world())[0]
	map_path = unreal.SystemLibrary.get_path_name(unreal.SystemLibrary.get_outer_object(current_level))
	job.set_editor_property('map', unreal.SoftObjectPath(map_path))

	job.set_editor_property('author', "BEDLAM")

	# Set output type EXR
	jpg_setting = job.get_configuration().find_setting_by_class(unreal.MoviePipelineImageSequenceOutput_JPG)
	if jpg_setting is not None:
		job.get_configuration().remove_setting(jpg_setting)

	exr_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineImageSequenceOutput_EXR)
	exr_setting.compression = unreal.EXRCompressionFormat.ZIP # ZIP results in better compression than PIZ when including segmentation masks (ObjectIds)
	exr_setting.multilayer = True

	output_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineOutputSetting)

	output_directory = output_dir + "\\exr_depth\\{sequence_name}"
	file_name_format = "{sequence_name}_{frame_number}"

	output_setting.output_directory = unreal.DirectoryPath(output_directory)
	output_setting.file_name_format = file_name_format

	output_setting.output_resolution = unreal.IntPoint(image_size[0], image_size[1])

	output_setting.zero_pad_frame_numbers = 4
	output_setting.output_frame_step = output_frame_step

	# Anti-aliasing: Disable for depth/mask rendering
	antialiasing_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineAntiAliasingSetting)

	antialiasing_setting.spatial_sample_count = 1
	antialiasing_setting.temporal_sample_count = 1
	antialiasing_setting.override_anti_aliasing = True
	antialiasing_setting.anti_aliasing_method = unreal.AntiAliasingMethod.AAM_NONE

	# Ensure proper Lumen warmup at frame 0, especially when rendering with frame skipping (6 fps)
	antialiasing_setting.render_warm_up_frames = True
	antialiasing_setting.engine_warm_up_count = 32

	# Deferred renderer
	deferred_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineDeferredPassBase)

	# Depth and motion vectors
	deferred_setting.use32_bit_post_process_materials = False # export 16-bit float depth
	world_depth = deferred_setting.additional_post_process_materials[0]
	world_depth.enabled = True
	deferred_setting.additional_post_process_materials[0] = world_depth
	motion_vectors = deferred_setting.additional_post_process_materials[1]
	motion_vectors.enabled = False # disable motion vectors
	deferred_setting.additional_post_process_materials[1] = motion_vectors

	# Normals (optional)
	if normals_type is not None:
		material = None
		if normals_type == "CameraSpace":
			material_name = material_cameranormal
			material = unreal.EditorAssetLibrary.load_asset(f"Material'{material_name}'")
			if not material:
				unreal.log_error("Cannot load material: " + material_name)
		elif normals_type == "WorldSpace":
			material_name = material_worldnormal
			material = unreal.EditorAssetLibrary.load_asset(f"Material'{material_name}'")
			if not material:
				unreal.log_error("Cannot load material: " + material_name)
		else:
			unreal.log_error("Unsupported normals type: " + normals_type)

		if material is not None:
			post_process_normal = unreal.MoviePipelinePostProcessPass(True, material)
			deferred_setting.additional_post_process_materials.append(post_process_normal)

		# Camera normals
		# material_name = material_cameranormal
		# material = unreal.EditorAssetLibrary.load_asset(f"Material'{material_name}'")
		# if not material:
		# 	unreal.log_error('Cannot load material: ' + material_name)
		# post_process_cameranormal = unreal.MoviePipelinePostProcessPass(True, material)
		# deferred_setting.additional_post_process_materials.append(post_process_cameranormal)


	# Segmentation mask (Object ID) render setup
	deferred_setting.disable_multisample_effects = True
	objectid_setting = job.get_configuration().find_or_add_setting_by_class(unreal.MoviePipelineObjectIdRenderPass)
	world_settings = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world().get_world_settings()
	world_partition = world_settings.get_editor_property("world_partition")
	if world_partition is not None:
		# World Partition system active, use folder type to identify masks
		objectid_setting.id_type = unreal.MoviePipelineObjectIdPassIdType.FOLDER
	else:
		# Use layer system to identify masks
		objectid_setting.id_type = unreal.MoviePipelineObjectIdPassIdType.LAYER

def save_movie_render_queue(pipeline_queue, current_batch_index, movie_render_queue_root, movie_render_queue_template):
	mrq_path = movie_render_queue_root + f"MRQ_Batch_{current_batch_index:02d}"
	# Remove existing MovieRenderQueue assets
	if unreal.EditorAssetLibrary.does_asset_exist(mrq_path):
		unreal.log("  Deleting existing old MovieRenderQueue asset: " + mrq_path)
		unreal.EditorAssetLibrary.delete_asset(mrq_path)

	mrq = unreal.EditorAssetLibrary.duplicate_asset(movie_render_queue_template, mrq_path)
	mrq.copy_from(pipeline_queue)
	unreal.log("  Saving MovieRenderQueue asset: " + mrq_path)
	unreal.EditorAssetLibrary.save_asset(mrq.get_path_name())

###############################################################################
# Main
###############################################################################
if __name__ == '__main__':

	unreal.log('BEDLAM: Setup Movie Render Queue render jobs for selected level sequences')

	if len(sys.argv) >= 2:
		output_dir = sys.argv[1]

	output_frame_step = 1
	generate_png_image = False
	generate_exr_image = False
	generate_exr_depthmask = False
	generate_exr_depthmasknormals = False

	spatial_samples = 1
	temporal_samples = 1

	if len(sys.argv) >= 3:
		values = sys.argv[2].split("_") # Example: 10-8-1_DepthMaskNormals
		output_frame_step = int(values[0].split("-")[0])
		spatial_samples = int(values[0].split("-")[1])
		temporal_samples = int(values[0].split("-")[2])

		if "PNG" in values:
			generate_png_image = True

		if "EXR" in values:
			generate_exr_image = True

		if "DepthMask" in values:
			generate_exr_depthmask = True # generate depth map and segmentation masks in .exr file (separate render pass)
		elif "DepthMaskNormals" in values:
			generate_exr_depthmasknormals = True # generate depth map, segmentation masks and normals in .exr file (separate render pass)

	image_size=(1280,720)
	if len(sys.argv) >= 4:
		values = sys.argv[3].split("x")
		image_width=int(values[0])
		image_height=int(values[1])
		image_size=(image_width, image_height)

	movie_render_queue_batches=0
	if len(sys.argv) >= 5:
		movie_render_queue_batches = int(sys.argv[4])

	normals_type = None
	if len(sys.argv) >= 6:
		normals_type = sys.argv[5]

	unreal.log(f"  Number of MovieRenderQueue batches: {movie_render_queue_batches}")

	start_time = time.perf_counter()

	# Setup movie render queue
	subsystem = unreal.get_editor_subsystem(unreal.MoviePipelineQueueSubsystem)
	pipeline_queue = subsystem.get_queue()

	# Make sure that target Level is open in Editor
	current_level = unreal.EditorLevelUtils.get_levels(unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world())[0]
	if not current_level.get_path_name().startswith("/Game"):
		unreal.log_error(f"No loaded Level. Load target level before creating MovieRenderQueue")
		sys.exit(1)

	if len(pipeline_queue.get_jobs()) > 0:
		# Remove all existing pipeline jobs
		for job in pipeline_queue.get_jobs():
			pipeline_queue.delete_job(job)

	# Get information about the selected Content Browser assets without loading all the assets into memory.
	# Note: unreal.EditorUtilityLibrary.get_selected_assets() will load all assets into memory.
	selection = unreal.EditorUtilityLibrary.get_selected_asset_data()
	level_sequence_selection = []
	for asset_data in selection:
		if asset_data.get_class() == unreal.LevelSequence.static_class():
			level_sequence_selection.append(asset_data)

	if len(level_sequence_selection) == 0:
		unreal.log_error(f"No selected LevelSequences")
		sys.exit(1)

	num_level_sequences = len(level_sequence_selection)
	current_batch_index = 0
	current_render_job_index = 0

	for level_sequence_data in level_sequence_selection:

		unreal.log(f"  Adding: {level_sequence_data.package_name}")

		# High-quality image pass with motion blur
		if generate_exr_image:
			add_render_job_exr_image(pipeline_queue, level_sequence_data, output_frame_step, image_size, spatial_samples=spatial_samples, temporal_samples=temporal_samples)
		elif generate_png_image:
			add_render_job(pipeline_queue, level_sequence_data, output_frame_step, image_size, spatial_samples=spatial_samples, temporal_samples=temporal_samples)

		# Depth pass, 1 temporal sample, no motion blur
		if generate_exr_depthmasknormals:
			# Render depth, segmentation masks and normals into multilayer EXR file
			add_render_job_exr_depthmask(pipeline_queue, level_sequence_data, output_frame_step, image_size, normals_type=normals_type)
		elif generate_exr_depthmask:
			# Render depth and segmentation masks into multilayer EXR file
			add_render_job_exr_depthmask(pipeline_queue, level_sequence_data, output_frame_step, image_size, normals_type=None)

		if movie_render_queue_batches > 0:
			# Batch render mode: Save current render job subset as MovieRenderQueue asset for later rendering via command-line
			current_render_job_index += 1
			avg_sequences_per_batch = num_level_sequences // movie_render_queue_batches
			save_batch = False
			if current_batch_index < (movie_render_queue_batches - 1):
				if current_render_job_index % avg_sequences_per_batch == 0:
					save_batch = True
			elif current_render_job_index == num_level_sequences:
					save_batch = True

			if save_batch:
				save_movie_render_queue(pipeline_queue, current_batch_index, movie_render_queue_root, movie_render_queue_template)
				current_batch_index += 1

				# Remove all existing pipeline jobs
				for job in pipeline_queue.get_jobs():
					pipeline_queue.delete_job(job)

	unreal.log(f"Movie Render Queue generation finished. Total time: {(time.perf_counter() - start_time):.1f}s")
	sys.exit(0)
