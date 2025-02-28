# Imports
from subprocess import run as subp_run, PIPE as subp_PIPE, CalledProcessError
from pathlib import Path
from shutil import which as sh_which
from datetime import datetime
from scripts.helpers import delete_directory, delete_file, is_nas_mounted
from scripts.logging_ops import notify_bot
from scripts.logging_ops import setup_logger



# Definitions
configfile: "config.yaml"
ready_tags = config['ready_tags']
blocking_tags = config['blocking_tags']
rsync_path = sh_which('rsync')
staging_dir_path = Path(config["staging_dir"])
run_files_dir_path = Path(config['run_files_dir_path'])
run_files_dir_name = str(Path(run_files_dir_path).name)
run_staging_dir = staging_dir_path / run_files_dir_name
samplesheet_path = run_staging_dir / 'SampleSheet.csv'
run_name = run_files_dir_path.parent.name
analysis_dir_path = staging_dir_path / run_name
results_dir_path = Path(config['results_dir_path']) / run_name
tmp_logging_dir_str = config['logging_dir'] + '/tmp'
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
log_file_str = config['logging_dir'] + f"/TSO_pipeline_{timestamp}.log"
error_messages = config["error_messages"]
# cbmed_dir_path = Path(config['cbmed_results_dir'])



# Rules
rule all:
    input:
        log_file_str


# Checkpoint to verify mountpoint
rule check_mountpoint:
    output:
        f"{tmp_logging_dir_str}/check_mountpoint.done",
        f"{tmp_logging_dir_str}/check_mountpoint.log"
    run:
        logger = setup_logger(logger_name='check_mountpoint', log_file_str=f"{tmp_logging_dir_str}/check_mountpoint.log") # TODO check if rule name could be replaced with wildcard
        mountpoint_dir = config["novaseq_mountpoint"]

        if not Path(mountpoint_dir).is_dir():
            message = f"Directory of mountpoint {mountpoint_dir} does not exist"
            notify_bot(message)
            logger.error(message)
        logger.info(f"Mountpoint found at '{mountpoint_dir}'")

        if not is_nas_mounted(mountpoint_dir, logger):
            message = f"Mountpoint check FAILED"
            notify_bot(message)
            logger.error(message)
        logger.info(f"Mountpoint is mounted")
        Path(output[0]).touch()


rule check_structure:
    input:
        f"{tmp_logging_dir_str}/check_mountpoint.done"
    output:
        f"{tmp_logging_dir_str}/check_structure.done",
        f"{tmp_logging_dir_str}/check_structure.log"
    run:
        logger = setup_logger(logger_name='check_structure', log_file_str=f"{tmp_logging_dir_str}/check_structure.log") # TODO check if rule name could be replaced with wildcard

        # TODO Change for oncoservice, CBmed and Patho dirs. Check for server availability dir and respective analysis results dirs
        if not Path(run_files_dir_path).is_dir():
            message = f"Directory {run_files_dir_path} does not exist"
            notify_bot(message)
            logger.error(message)
        logger.info(f"Run directory found at {run_files_dir_path}")

        if not staging_dir_path.is_dir():
            message = f"Directory {staging_dir_path} does not exist"
            notify_bot(message)
            logger.error(message)
        logger.info(f"Staging directory found at {staging_dir_path}")

        Path(output[0]).touch()


rule check_docker_image:
    input:
        f"{tmp_logging_dir_str}/check_structure.done"
    output:
        f"{tmp_logging_dir_str}/check_docker_image.done",
        f"{tmp_logging_dir_str}/check_docker_image.log"
    run:
        logger = setup_logger(logger_name='check_docker_image', log_file_str=f"{tmp_logging_dir_str}/check_docker_image.log") # TODO check if rule name could be replaced with wildcard

        try:
            result = subp_run(['docker','images'],
                stdout=subp_PIPE,
                stderr=subp_PIPE,
                text=True)
        except Exception as e:
            message = f"Error checking docker image: {str(e)}"
            notify_bot(message)
            logger.error(message)
            # TODO investigate what the hell does it do (in theory, each exception should stop the pipeline,
            #  but do they have to be raised specifically?)
            raise Exception

        if not 'dragen_tso500_ctdna' in result.stdout:
            message = "The dragen_tso500_ctdna Docker image wasn't found in the system"
            notify_bot(message)
            logger.error(message)

        logger.info(f"The dragen_tso500_ctdna was found successfully")
        Path(output[0]).touch()


rule check_rsync:
    input:
        f"{tmp_logging_dir_str}/check_docker_image.done"
    output:
        f"{tmp_logging_dir_str}/check_rsync.done",
        f"{tmp_logging_dir_str}/check_rsync.log"
    run:
        logger = setup_logger(logger_name='check_rsync',log_file_str=f"{tmp_logging_dir_str}/check_rsync.log")  # TODO check if rule name could be replaced with wildcard

        if not rsync_path:
            message = "Rsync path cannot be empty or None"
            notify_bot(message)
            logger.error(message)

        logger.info(f"Rsync has been found by this path: {rsync_path}")
        Path(output[0]).touch()


# TODO check how it fixes samplesheets
# checkpoint validate_samplesheet:
#     output:
#         f"{tmp_logging_dir_str}/validate_samplesheet.done"
#     run:
#         samplesheet = config['samplesheet']
#         try:
#             # Read and validate using default Illumina v2 validators
#             read_samplesheetv2(
#                 samplesheet,
#                 validation=[
#                     samshee.validation.illuminasamplesheetv2schema,
#                     samshee.validation.illuminasamplesheetv2logic
#                 ]
#             )
#             logger.info("Sample sheet is valid!")
#         except Exception as e:
#             logger.error(f"Validation failed: {str(e)}")
#             raise


rule stage_run:
    input:
        f"{tmp_logging_dir_str}/check_rsync.done"
    output:
        f"{tmp_logging_dir_str}/stage_run.done",
        f"{tmp_logging_dir_str}/stage_run.log"
    run:
        logger = setup_logger(logger_name='stage_run',log_file_str=f"{tmp_logging_dir_str}/stage_run.log")  # TODO check if rule name could be replaced with wildcard
        message = f'Staging run {run_name}'
        notify_bot(message)
        logger.info(message)

        # rsync_call = [str(rsync_path), '-rl', '--checksum',
        #               str(f"{str(run_files_dir_path)}/"), str(run_staging_dir)]
        # try:
        #     subp_run(rsync_call).check_returncode()
        # except CalledProcessError as e:
        #     message = f"Staging had failed with return a code {e.returncode}. Error output: {e.stderr.decode()}"
        #     notify_bot(message)
        #     logger.error(message)
        #     raise RuntimeError(message)
        #     # delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)

        message = f'Done staging the run {run_name}'
        logger.info(message)
        notify_bot(message)
        Path(output[0]).touch()


# TODO change when finished testing
rule process_run:
    input:
        f"{tmp_logging_dir_str}/stage_run.done"
    output:
        f"{tmp_logging_dir_str}/process_run.done",
        f"{tmp_logging_dir_str}/process_run.log"
    run:
         logger = setup_logger(logger_name='process_run',log_file_str=f"{tmp_logging_dir_str}/process_run.log")  # TODO check if rule name could be replaced with wildcard
         message = f'Started running the DRAGEN TSO500 script for run {run_name}'
         logger.info(message)
         notify_bot(message)

         dragen_call = ['/usr/local/bin/DRAGEN_TruSight_Oncology_500_ctDNA.sh','--version']
                        # '--runFolder', str(run_staging_dir),
                        # '--analysisFolder', str(analysis_dir_path)]
         try:
             subp_run(dragen_call).check_returncode()
         except CalledProcessError as e:
             message = f"DRAGEN failed with a return code, that corresponds to a message: {error_messages[e.returncode]}. Cleaning up..."
             logger.error(message)
             notify_bot(message)
             # delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
             # delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
             raise RuntimeError(message)

         logger.info(f'Done running the DRAGEN TSO500 script for run {run_name}')
         notify_bot(f'Done running the DRAGEN TSO500 script for run {run_name}')
         Path(output[0]).touch()


# TODO would differ for CBmed 1: rearrange stuff and then transfer it ig?
rule transfer_results:
    input:
        f"{tmp_logging_dir_str}/process_run.done"
    output:
        f"{tmp_logging_dir_str}/transfer_results.done",
        f"{tmp_logging_dir_str}/transfer_results.log"
    run:
        logger = setup_logger(logger_name='transfer_results',log_file_str=f"{tmp_logging_dir_str}/transfer_results.log")  # TODO check if rule name could be replaced with wildcard
        message = f'Started transferring results for run {run_name}'
        notify_bot(message)
        logger.info(message)

        # rsync_call = [str(rsync_path), '-rl', '--checksum',
        #               str(analysis_dir_path), str(results_dir_path)]
        # try:
        #     subp_run(rsync_call).check_returncode()
        # except CalledProcessError as e:
        #     message = f"Transfering results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        #     notify_bot(message)
        #     logger.error(message)
        #     # delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
        #     # delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
        #     # delete_directory(dead_dir_path=results_dir_path,logger_runtime=logger)
        #     raise RuntimeError(message)

        # TODO add assertions for safety
        # delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
        # delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
        # TODO add that if run is processed
        # delete_directory(dead_dir_path=run_files_dir_path,logger_runtime=logger)
        message = f'Done transferring results for run {run_name}'
        notify_bot(message)
        logger.info(message)

        Path(output[0]).touch()


rule summarize_logs:
    input:
        f"{tmp_logging_dir_str}/transfer_results.done",
        f"{tmp_logging_dir_str}/check_mountpoint.done",
        f"{tmp_logging_dir_str}/check_structure.done",
        f"{tmp_logging_dir_str}/check_docker_image.done",
        f"{tmp_logging_dir_str}/check_rsync.done",
        f"{tmp_logging_dir_str}/process_run.done",
        f"{tmp_logging_dir_str}/check_mountpoint.log",
        f"{tmp_logging_dir_str}/check_structure.log",
        f"{tmp_logging_dir_str}/check_docker_image.log",
        f"{tmp_logging_dir_str}/check_rsync.log",
        f"{tmp_logging_dir_str}/stage_run.log",
        f"{tmp_logging_dir_str}/process_run.log",
        f"{tmp_logging_dir_str}/transfer_results.log"
    output:
        log_file_str
    run:
        with open(output[0],'w') as dest:
            for log_file in input[6:]:
                with open(log_file,'r') as source:
                    dest.write(source.read())

        for tmp_file in input:
            Path(tmp_file).unlink()
