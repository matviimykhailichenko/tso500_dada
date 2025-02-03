import subprocess
from snakemake.logging import logger
from pathlib import Path

configfile: "config.yaml"


rule all:
    input:
        "logs/check_mountpoint.done",
        "logs/check_structure.done",
        "logs/check_docker_image.done"


# Checkpoint to verify mountpoint
checkpoint check_mountpoint:
    output:
        "logs/check_mountpoint.done"
    run:
        mountpoint_dir = config["mountpoint_dir"]
        assert Path(mountpoint_dir).is_dir(), f"Directory {mountpoint_dir} does not exist"
        logger.info(f"Mountpoint found at '{mountpoint_dir}'")
        Path(output[0]).touch()

        # mountpoint_dir = config["mountpoint_dir"]
        # mountpoint_binary = '/usr/bin/mountpoint'
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
    run:
        run_dir = config["run_dir"]
        staging_dir = config["staging_dir"]
        results_dir = config["results_dir"]

        assert Path(run_dir).is_dir(), f"Directory {run_dir} does not exist"
        assert Path(results_dir).is_dir(), f"Directory {results_dir} does not exist"
        assert Path(staging_dir).is_dir(), f"Directory {staging_dir} does not exist"

        Path(output[0]).touch()

checkpoint check_docker_image:
    output:
        "logs/check_docker_image.done"
    run:
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
        Path(output[0]).touch()