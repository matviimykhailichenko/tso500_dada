from pathlib import Path
from logging import Logger
from shutil import which as sh_which, rmtree as sh_rmtree, copy as sh_copy
from subprocess import run as subp_run, PIPE as subp_PIPE, CalledProcessError
from typing import Optional
import yaml
from scripts.logging_ops import notify_bot



def is_server_available() -> bool:
    with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        server_availability_dir = Path(config['server_availability_dir'])
        server_idle_tag = server_availability_dir / config['server_idle_tag']
        server_busy_tag = server_availability_dir / config['server_busy_tag']

    try:
        if Path(server_busy_tag).exists() and not Path(server_idle_tag).exists():
            return True
        return False
    except Exception as e:
        # TODO discord bot?
        raise RuntimeError(f"Failed to check server status: {e}")


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


def delete_file(dead_file_path: Path):
    if dead_file_path and dead_file_path.is_file():
        try:
            dead_file_path.unlink()
        except KeyboardInterrupt:
            return 255  # propagate KeyboardInterrupt outward
# TODO not sure if returning 255 is most logical


def is_nas_mounted(mountpoint_dir: str,
                   logger_runtime: Logger) -> bool:
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


def transfer_results_cbmed(flowcell: str,
                           run_name: str,
                           rsync_path_str: str,
                           logger: Logger,
                           testing: bool = False):
    with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        cbmed_results_dir = Path(config['cbmed_results_dir'])
        staging_dir_path = Path(config['staging_dir'])
    data_staging_dir_path = staging_dir_path / flowcell
    data_cbmed_dir_path = cbmed_results_dir / 'flowcells' / flowcell
    results_staging_dir_path = staging_dir_path / run_name
    results_cbmed_dir_path = cbmed_results_dir / 'dragen' / flowcell / 'Results'

    checksums_file_path = data_cbmed_dir_path / 'checksums.md5'
    log_file_path = data_cbmed_dir_path / 'CBmed_copylog.log'
    rsync_call = (f"{rsync_path_str} -rl " # TODO delete if pipeline without -l flag succeeds 
                  f"--checksum --checksum-choice=md5 "
                  f"--out-format=\"%C %n\" "
                  f"--log-file {str(log_file_path)}"
                  f"{str(data_staging_dir_path)}/ "
                  f"{str(data_cbmed_dir_path)} "
                  f"> {str(checksums_file_path)}")
    try:
        subp_run(rsync_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = f"Transfering results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        notify_bot(message)
        logger.error(message)
        raise RuntimeError()

    checksums_file_path = results_cbmed_dir_path / 'checksums.md5'
    log_file_path = results_cbmed_dir_path / 'CBmed_copylog.log'
    rsync_call = (f"{rsync_path_str} -rl "
                  f"--checksum --checksum-choice=md5 "
                  f"--out-format=\"%C %n\" "
                  f"--log-file {str(log_file_path)}"
                  f"{str(results_staging_dir_path)}/ "
                  f"{str(results_cbmed_dir_path)} "
                  f"> {str(checksums_file_path)}")
    try:
        subp_run(rsync_call, shell=True).check_returncode()
    except CalledProcessError as e:
        message = f"Transfering results had failed with return a code {e.returncode}. Error output: {e.stderr}"
        notify_bot(message)
        logger.error(message)
        raise RuntimeError()

    return 0


def transfer_results_oncoservice(run_name: str,
                           rsync_path_str: str,
                           logger: Logger,
                           testing: bool = False):
    with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        staging_dir_path = Path(config['staging_dir'])
        results_dir_path = Path(config['oncoservice_dir']) / f'Analyseergebnisse{'_TEST' if testing else ''}'
    analysis_dir_path = staging_dir_path / run_name
    rsync_call = [rsync_path_str, '-r', '--checksum',
                  str(f'{analysis_dir_path}/'), str(results_dir_path)]
    try:
        subp_run(rsync_call).check_returncode()
    except CalledProcessError as e:
        message = f"Transfering results had failed with a return code {e.returncode}. Error output: {e.stderr}"
        notify_bot(message)
        logger.error(message)
        # delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
        # delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
        # delete_directory(dead_dir_path=results_dir_path,logger_runtime=logger)
        raise RuntimeError(message)

    # delete_directory(dead_dir_path=analysis_dir_path,logger_runtime=logger)
    # delete_directory(dead_dir_path=run_staging_dir,logger_runtime=logger)
    # TODO add that if run is processed
    # delete_directory(dead_dir_path=run_files_dir_path,logger_runtime=logger)

    return 0