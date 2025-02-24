from pathlib import Path
from logging import Logger
from shutil import which as sh_which,  rmtree as sh_rmtree
from subprocess import run as subp_run, PIPE as subp_PIPE, CalledProcessError
from typing import Optional



def is_server_available(server_idle_tag: Path,
                        server_busy_tag: Path) -> bool:
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
