# Imports
import subprocess
from pathlib import Path
from shutil import which as sh_which,  rmtree as sh_rmtree
from datetime import datetime
import logging
from logging import Logger
import os



# Definitions
configfile: "config.yaml"
ready_tags = config['ready_tags']
blocking_tags = config['blocking_tags']
rsync_path = sh_which('rsync')
staging_dir_path = Path(config["staging_dir"])
run_files_dir_path = Path(config['run_files_dir_path'])
run_files_dir_name = str(Path(run_files_dir_path).name)
run_staging_dir = staging_dir_path / run_files_dir_name
results_dir_path = config['results_dir_path']
samplesheet_path = run_staging_dir / 'SampleSheet.csv'
run_name = datetime.now().strftime('%y%m%d') + '_TSO'
analysis_dir_path = staging_dir_path / run_name
results_dir_path = results_dir_path / run_name
# TODO put that into scripts into separate file
# TODO add TSO_bot



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


def delete_directory(dead_dir_path: Path, logger_runtime: Logger):
    if dead_dir_path and dead_dir_path.is_dir():
        try:
            logger_runtime.info(f"deleting directory '{dead_dir_path}' ...")
            sh_rmtree(dead_dir_path)  # should also delete the directory itself along with its contents
            logger_runtime.info(f"successfully deleted directory '{dead_dir_path}'")
        except KeyboardInterrupt:
            logger_runtime.error("Keyboard Interrupt by user detected. Terminating pipeline execution ..")
            return 255  # propagate KeyboardInterrupt outward
        # TODO add whole stack
        if Path(dead_dir_path).is_dir():
            logger_runtime.warning(f"could not delete directory{dead_dir_path}")
    else:
        logger_runtime.warning(f"could not delete directory '{dead_dir_path}': path does not exist")


# Rules
rule all:
    input:
        "logs/check_mountpoint.done",
        "logs/check_structure.done",
        "logs/check_docker_image.done",
        # "logs/validate_samplesheet.done"
        'results/runs.txt',
        "logs/unified.log"



# Checkpoint to verify mountpoint
rule check_mountpoint:
    output:
        "logs/check_mountpoint.done"
    log:
        "logs/check_mountpoint.log"
    run:
        logger = setup_logger(rule_name='check_mountpoint') # TODO check if rule name could be replaced with wildcard
        mountpoint_dir = config["mountpoint_dir"]
        assert Path(mountpoint_dir).is_dir(), f"Directory {mountpoint_dir} does not exist"
        logger.info(f"Mountpoint found at '{mountpoint_dir}'")
        Path(output[0]).touch()

        # mountpoint_dir = config["mountpoint_dir"]
        # mountpoint_binary = config['mountpoint_binary']
        #
        # try:
        #     result = subprocess.run(
        #         [mountpoint_binary, mountpoint_dir],
        #         stdout=subprocess.PIPE,
        #         stderr=subprocess.PIPE,
        #         text=True
        #     )
        #
        #     if result.returncode != 0:
        #         logger.error(f"Directory '{mountpoint_dir}' is not a mountpoint")
        #         raise Exception("Mountpoint check failed")
        #
        #     logger.info(f"Mountpoint found at '{mountpoint_dir}'")
        #
        # except Exception as e:
        #     logger.error(f"Error checking mountpoint: {str(e)}")
        #     raise


# noinspection PyUnresolvedReferences
rule check_structure:
    output:
        "logs/check_structure.done"
    log:
        "logs/check_structure.log"
    run:
        logger = setup_logger(rule_name='check_structure')
        # TODO Change for 2 run dirs and 2 results dirs


        assert Path(run_dir).is_dir(), f"Directory {run_dir} does not exist"
        logger.info(f"Run directory found at '{run_dir}'")
        assert Path(results_dir).is_dir(), f"Directory {results_dir} does not exist"
        logger.info(f"Results directory found at '{results_dir}'")
        assert Path(staging_dir).is_dir(), f"Directory {staging_dir} does not exist"
        logger.info(f"Staging directory found at '{staging_dir}'")

        Path(output[0]).touch()


rule check_docker_image:
    output:
        "logs/check_docker_image.done"
    log:
        "logs/check_docker_image.log"
    run:
        logger = setup_logger(rule_name='check_structure')

        try:
            result = subprocess.run(['python3','scripts/docker_images.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True)
            # result = subprocess.run(['docker','images'],
            #     stdout=subprocess.PIPE,
            #     stderr=subprocess.PIPE,
            #     text=True)
        except Exception as e:
            logger.error(f"Error checking docker image: {str(e)}")
            raise
        assert 'dragen_tso500_ctdna' in result.stdout
        logger.info(f"The dragen_tso500_ctdna was found successfully")

        Path(output[0]).touch()


rule check_rsync:
    output:
        "logs/check_rsync.done"
    log:
        "logs/check_rsync.log"
    run:
        logger = setup_logger(rule_name='check_rsync')

        assert rsync_path, "Rsync path cannot be empty or None"
        logger.info(f"rsync has been found by this path: {rsync_path}")


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
    output:
        "logs/stage_run.done"
    log:
        "logs/stage_run.log"
    run:
        logger = setup_logger(rule_name='stage_run')

        rsync_call = [str(rsync_path), '-rl', '--checksum',
                      str(run_files_dir_path), str(run_staging_dir)]
        try:
            subprocess.run(rsync_call).check_returncode()
        except subprocess.CalledProcessError as e:
            logger.error(f"rsync failed with return code {e.returncode}")
            logger.error(f"Error output: {e.stderr}")
            # TODO cleanup if failed


rule process_run:
    output:
        "logs/process_run.done"
    log:
        "logs/process_run.log"
    run:
        logger = setup_logger(rule_name='process_run')

        dragen_call = ['DRAGEN_TruSight_Oncology_500_ctDNA.sh', '--runFolder', str(run_staging_dir),
                       '--analysisFolder', str(analysis_dir_path),
                       '--sampleSheet', str(samplesheet_path)]
        try:
            subprocess.run(rsync_call).check_returncode()
        except subprocess.CalledProcessError as e:
            # TODO cleanup if failed
            delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
            delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
            logger.error(f"DRAGEN failed with return code {e.returncode}. Cleaning up...")
            logger.error(f"Error output: {e.stderr}")


rule transfer_results:
    output:
        "logs/transfer_results.done"
    log:
        "logs/transfer_results.log"
    run:
        logger= setup_logger(rule_name='transfer_results')

        rsync_call = [str(rsync_path), '-rl','--checksum',
                      str(analysis_dir_path), str(run_staging_dir)]
        try:
            subprocess.run(rsync_call).check_returncode()
        except subprocess.CalledProcessError as e:
            delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
            delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
            delete_directory(dead_dir_path=results_dir_path,logger_runtime=logger)
            logger.error(f"rsync failed with return code {e.returncode}. Cleaning up...")
            logger.error(f"Error output: {e.stderr}")

        delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
        delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
        # delete_directory(dead_dir_path=run_files_dir_path,logger_runtime=logger)


rule summarize_logs:
    output:
        "logs/unified.log"
    run:
         rules_sequence = config['rules_sequence']
         for rule in rules_sequence:
             with open(f'logs/{rule}.log','r') as source:
                with open("logs/unified.log",'a') as dest:
                    dest.write(source.read())
