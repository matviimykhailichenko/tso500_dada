from pathlib import Path
from logging import Logger
from shutil import rmtree as sh_rmtree



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