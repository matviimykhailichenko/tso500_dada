# Imports
import subprocess
from pathlib import Path
from samshee.samplesheetv2 import read_samplesheetv2
import samshee.validation



# Definitions
configfile: "config.yaml"
ready_tags = config['ready_tags']
blocking_tags = config['blocking_tags']

# TODO put that into scripts into separate file
# Helper functions
def setup_logger(rule_name):
    import logging
    import os

    os.makedirs("logs",exist_ok=True)
    logger = logging.getLogger(rule_name)
    handler = logging.FileHandler(f"logs/{rule_name}.log")
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger



rule all:
    input:
        "logs/check_mountpoint.done",
        "logs/check_structure.done",
        "logs/check_docker_image.done",
        # "logs/validate_samplesheet.done"
        'results/runs.txt',
        "logs/unified.log"



# Checkpoint to verify mountpoint
checkpoint check_mountpoint:
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

checkpoint check_structure:
    output:
        "logs/check_structure.done"
    log:
        "logs/check_structure.log"
    run:
        logger = setup_logger(rule_name='check_structure')
        # TODO Change for 2 run dirs and 2 results dirs
        run_dir = config["run_dir"]
        staging_dir = config["staging_dir"]
        results_dir = config["results_dir"]

        assert Path(run_dir).is_dir(), f"Directory {run_dir} does not exist"
        logger.info(f"Run directory found at '{run_dir}'")
        assert Path(results_dir).is_dir(), f"Directory {results_dir} does not exist"
        logger.info(f"Results directory found at '{results_dir}'")
        assert Path(staging_dir).is_dir(), f"Directory {staging_dir} does not exist"
        logger.info(f"Staging directory found at '{staging_dir}'")

        Path(output[0]).touch()

checkpoint check_docker_image:
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

# Checkpoint to identify runs
checkpoint scan_runs:
    output:
        runs="results/runs.txt"
    run:
        valid_runs = []
        for runs_dir in config["sequencing_dirs"]:
            runs_dir = Path(runs_dir)
            for run_dir in runs_dir.iterdir():
                # Skip if any blocking files exist
                txt_files = list(Path(run_dir).glob('*.txt'))
                file_names = [path.name for path in txt_files]
                if (not any(f in blocking_tags for f in file_names) and
                        (all(f in ready_tags for f in file_names))):
                    valid_runs.append(run_dir.name)

        # Write valid runs to output file
        with open(output.runs,'w') as f:
            for run in valid_runs:
                f.write(f"{run}\n")

# # Helper function to get run names
# def get_runs(wildcards):
#     checkpoint_output = checkpoints.scan_runs.get(**wildcards).runs
#     with open(checkpoint_output) as f:
#         return [line.strip() for line in f]

rule summarize_logs:
    output:
        "logs/unified.log"
    run:
         rules_sequence = config['rules_sequence']
         for rule in rules_sequence:
             with open(f'logs/{rule}.log','r') as source:
                with open("logs/unified.log",'a') as dest:
                    dest.write(source.read())
