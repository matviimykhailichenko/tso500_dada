# Imports
from subprocess import run as subp_run, PIPE as subp_PIPE, CalledProcessError
from pathlib import Path
from shutil import which as sh_which,  rmtree as sh_rmtree
from datetime import datetime
import logging
from logging import Logger
import os
from scripts.helpers import delete_directory



# Definitions
configfile: "config.yaml"
ready_tags = config['ready_tags']
blocking_tags = config['blocking_tags']
rsync_path = sh_which('rsync')
staging_dir_path = Path(config["staging_dir"])
run_files_dir_path = Path(config['run_files_dir_path'])
run_files_dir_name = str(Path(run_files_dir_path).name)
run_staging_dir = staging_dir_path / run_files_dir_name
results_dir_path = Path(config['results_dir_path'])
samplesheet_path = run_staging_dir / 'SampleSheet.csv'
run_name = datetime.now().strftime('%y%m%d') + '_TSO'
analysis_dir_path = staging_dir_path / run_name
results_dir_path = results_dir_path / run_name
# TODO put that into scripts into separate file
# TODO add TSO_bot
# TODO add check for available storage


# Helper functions
def setup_logger(rule_name):
    os.makedirs("logs",exist_ok=True)
    logger = logging.getLogger(rule_name)
    handler = logging.FileHandler(f"logs/{rule_name}.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger





def is_nas_mounted(mountpoint_dir: str,
                   logger_runtime: Logger) -> bool:  # tested
    mountpoint_binary = sh_which('mountpoint')
    if not mountpoint_binary:
        mountpoint_binary = '/usr/bin/mountpoint'
        logger_runtime.warning(f"looked for the mountpoint executable at '{mountpoint_binary}' but didn't "
                               f"find the file (path was None) or could not access it (permission problem). "
                               f"Using the default one anyways at '{mountpoint_binary}'. This might cause "
                               f"subprocess failure!")
    ran_mount_check = subp_run([mountpoint_binary, mountpoint_dir], stdout=subp_PIPE, encoding='utf-8')
    try:
        ran_mount_check.check_returncode()
    except CalledProcessError:
        # TODO BOT!
        logger_runtime.error(f"the expected NAS mountpoint was not found at {mountpoint_dir}. Terminating..")
        return False
    # check if the command returned as expected:
    if ran_mount_check.stdout.strip() != f'{mountpoint_dir} is a mountpoint':
        logger_runtime.error(f"the expected NAS mountpoint was not found at '{mountpoint_dir}'. "
                             f"Terminating..")
        return False
    logger_runtime.info(f"the expected NAS mountpoint was found at '{mountpoint_dir}'.")
    return True


# Rules
rule all:
    input:
        "logs/unified.log"



# Checkpoint to verify mountpoint
rule check_mountpoint:
    output:
        "logs/check_mountpoint.done"
    log:
        "logs/check_mountpoint.log"
    run:
        logger = setup_logger(rule_name='check_mountpoint') # TODO check if rule name could be replaced with wildcard
        mountpoint_dir = config["novaseq_mountpoint"]
        assert Path(mountpoint_dir).is_dir(), f"Directory {mountpoint_dir} does not exist"
        logger.info(f"Mountpoint found at '{mountpoint_dir}'")

        assert is_nas_mounted(mountpoint_dir, logger), f"Mountpoint check FAILED"
        Path(output[0]).touch()


# noinspection PyUnresolvedReferences
rule check_structure:
    input:
        "logs/check_mountpoint.done"
    output:
        "logs/check_structure.done"
    log:
        "logs/check_structure.log"
    run:
        logger = setup_logger(rule_name='check_structure')
        # TODO Change for 2 run dirs and 2 results dirs
        assert Path(run_files_dir_path).is_dir(), f"Directory {run_files_dir_path} does not exist"
        logger.info(f"Run directory found at '{run_files_dir_path}'")
        # assert Path(results_dir_path).is_dir(), f"Directory {results_dir_path} does not exist"
        # logger.info(f"Results directory found at '{results_dir}'")
        assert Path(staging_dir_path).is_dir(), f"Directory {staging_dir_path} does not exist"
        logger.info(f"Staging directory found at '{staging_dir_path}'")

        Path(output[0]).touch()


rule check_docker_image:
    input:
        "logs/check_structure.done"
    output:
        "logs/check_docker_image.done"
    log:
        "logs/check_docker_image.log"
    run:
        logger = setup_logger(rule_name='check_docker_image')

        try:
            result = subp_run(['docker','images'],
                stdout=subp_PIPE,
                stderr=subp_PIPE,
                text=True)
        except Exception as e:
            logger.error(f"Error checking docker image: {str(e)}")
            raise
        assert 'dragen_tso500_ctdna' in result.stdout
        logger.info(f"The dragen_tso500_ctdna was found successfully")

        Path(output[0]).touch()


rule check_rsync:
    input:
        "logs/check_docker_image.done"
    output:
        "logs/check_rsync.done"
    log:
        "logs/check_rsync.log"
    run:
        logger = setup_logger(rule_name='check_rsync')

        assert rsync_path, "Rsync path cannot be empty or None"
        logger.info(f"rsync has been found by this path: {rsync_path}")

        Path(output[0]).touch()


# TODO check how it fixes samplesheets
# checkpoint validate_samplesheet:
#     output:
#         "logs/validate_samplesheet.done"
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
        "logs/check_rsync.done"
    output:
        "logs/stage_run.done"
    log:
        "logs/stage_run.log"
    run:
        logger = setup_logger(rule_name='stage_run')

        rsync_call = [str(rsync_path), '-rl', '--checksum',
                      str(f"{str(run_files_dir_path)}/"), str(run_staging_dir)]
        try:
            subp_run(rsync_call).check_returncode()
        except CalledProcessError as e:
            logger.error(f"rsync failed with return code {e.returncode}")
            logger.error(f"Error output: {e.stderr}")
            delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)

        Path(output[0]).touch()

# TODO add error handling, assuming that dragen_call won't raise errors
rule process_run:
    input:
        "logs/stage_run.done"
    output:
        "logs/process_run.done"
    log:
        "logs/process_run.log"
    run:
         logger = setup_logger(rule_name='process_run')
         logger.info(f'Here I would process run {run_staging_dir} with {analysis_dir_path} and {samplesheet_path}')

         dragen_call = ['DRAGEN_TruSight_Oncology_500_ctDNA.sh', '--runFolder', str(run_staging_dir),
                        '--analysisFolder', str(analysis_dir_path),
                        '--sampleSheet', str(samplesheet_path)]
         try:
             subp_run(dragen_call).check_returncode()
         except CalledProcessError as e:
             logger.error(f"DRAGEN failed with return code {e.returncode}. Cleaning up...")
             logger.error(f"Error output: {e.stderr}")
             delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
             delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)

         Path(output[0]).touch()


rule transfer_results:
    input:
        "logs/process_run.done"
    output:
        "logs/transfer_results.done"
    log:
        "logs/transfer_results.log"
    run:
        logger= setup_logger(rule_name='transfer_results')

        rsync_call = [str(rsync_path), '-rl', '--checksum',
                      str(analysis_dir_path), str(run_staging_dir)]
        try:
            subp_run(rsync_call).check_returncode()
        except CalledProcessError as e:
            logger.error(f"rsync failed with return code {e.returncode}. Cleaning up...")
            logger.error(f"Error output: {e.stderr}")
            delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
            delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
            delete_directory(dead_dir_path=results_dir_path,logger_runtime=logger)

        # TODO add assertions for safety
        delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
        delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
        # TODO add that if run is processed
        # delete_directory(dead_dir_path=run_files_dir_path,logger_runtime=logger)

        Path(output[0]).touch()


rule summarize_logs:
    input:
        "logs/transfer_results.done",
        "logs/check_mountpoint.log",
        "logs/check_structure.log",
        "logs/check_docker_image.log",
        "logs/check_rsync.log",
        "logs/stage_run.log",
        "logs/process_run.log",
        "logs/transfer_results.log"
    output:
        "logs/unified.log"
    run:
        with open(output[0],'w') as dest:
            for log_file in input[1:]:
                with open(log_file,'r') as source:
                    dest.write(source.read())
