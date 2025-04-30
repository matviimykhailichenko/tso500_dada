from pathlib import Path
from subprocess import CalledProcessError
import yaml
import subprocess
import argparse
from filelock import FileLock, Timeout
import pandas as pd
from scripts.helpers import is_server_available, get_server_ip, load_config, setup_paths, check_mountpoint, check_rsync, \
    check_structure, check_docker_image, check_tso500_script, stage_object, process_object, transfer_results, get_queue
from scripts.logging_ops import notify_bot, setup_logger



def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script process incoming runs')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser

#
# def run_automation(run_type: str = 'None', testing: bool = False):
#     with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
#         config = yaml.safe_load(file)
#         pipeline_dir: Path = Path(config['pipeline_dir'])
#         onco_dir: Path = Path(config['oncoservice_dir'])
#         server_availability_dir: Path = Path(config['server_availability_dir'])
#         server_idle_tag: Path = server_availability_dir / config['server_idle_tag']
#         server_busy_tag: Path = server_availability_dir / config['server_busy_tag']
#         cbmed_seqencing_dir: Path = Path(config['cbmed_seqencing_dir'])
#         pending_tag: str = config['pending_run_tag']
#
#     if run_type == 'oncoservice':
#         pending_tag: Path = onco_dir / pending_tag
#         run_files_dir: Path = Path(pending_tag.read_text())
#
#     elif run_type == 'cbmed':
#         pending_tag: Path = cbmed_seqencing_dir / pending_tag
#         run_files_dir: Path = Path(pending_tag.read_text())
#
#     elif run_type == 'patho':
#         pending_tag: Path = cbmed_seqencing_dir / pending_tag
#         run_files_dir: Path = Path(pending_tag.read_text())
#     else:
#         if testing:
#             notify_bot(f"TESTING TSO500: Unrecognised run type: {run_type}")
#         raise RuntimeError(f"Unrecognised run type: {run_type}")
#
#     failed_tag: Path = run_files_dir / config['failed_tag']
#     analysed_tag: Path = run_files_dir / config['analysed_tag']
#     server_idle_tag.unlink()
#     snakefile_path = pipeline_dir / 'snakefile'
#     config_file_path = pipeline_dir / 'config.yaml'
#     server_busy_tag.touch()
#
#     snakemake_call =[
#             "conda", "run", "-n", "tso500_dragen_pipeline",
#             "snakemake", "-s", str(snakefile_path),
#             "--configfile", str(config_file_path),
#             "--config", f"run_files_dir={str(run_files_dir)}", f'run_type={run_type}', f'testing={str(testing)}'
#     ]
#     try:
#         subprocess.run(snakemake_call).check_returncode()
#     except CalledProcessError as e:
#         message = f"Error processing run {run_files_dir}: {e}"
#         if testing:
#             notify_bot(f"TESTING TSO500: Error processing run {run_files_dir}: {e}")
#         failed_tag.touch()
#         server_busy_tag.unlink()
#         server_idle_tag.touch()
#         pending_tag.unlink()
#         raise RuntimeError(message)
#
#     analysed_tag.touch()
#     server_busy_tag.unlink()
#     server_idle_tag.touch()
#     pending_tag.unlink()



def main():
    args = create_parser().parse_args()
    testing: bool = args.testing

    with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])

    # if not is_server_available():
    #     return

    server = get_server_ip()
    queue_file = pipeline_dir.parent.parent / f'{server}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server}_PENDING.txt'

    queue = get_queue(pending_file=pending_file, queue_file=queue_file)

    if queue is None or queue.empty:
        return

    path, input_type, _, tag, flowcell = queue.iloc[0]

    config = load_config('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml')

    paths: dict = setup_paths(input_path=Path(path),input_type=input_type,tag=tag,flowcell=flowcell,config=config)

    logger = setup_logger(logger_name='Logger',log_file=paths['log_file'])

    check_mountpoint(paths=paths, logger=logger)

    check_structure(paths=paths, logger=logger)

    check_docker_image(logger=logger)

    check_rsync(paths=paths, logger=logger)

    check_tso500_script(paths=paths, logger=logger)

    stage_object(paths=paths,input_type=input_type,logger=logger)

    process_object(paths=paths,input_type=input_type,logger=logger)

    transfer_results(paths=paths,input_type=input_type,logger=logger)

if __name__ == "__main__":
    main()
