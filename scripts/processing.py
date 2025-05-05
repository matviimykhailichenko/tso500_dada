from pathlib import Path
from subprocess import CalledProcessError
import yaml
import subprocess
import argparse
from filelock import FileLock, Timeout
import pandas as pd
from scripts.helpers import is_server_available, get_server_ip, load_config, setup_paths, check_mountpoint, check_rsync, \
    check_structure, check_docker_image, check_tso500_script, stage_object, process_object, transfer_results, get_queue
from scripts.logging_ops import notify_bot, setup_logger, notify_pipeline_status



def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script process incoming runs')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser


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

    is_last_sample = False
    if input_type == 'sample' and len(queue['Tag'][queue['Tag'] == tag]) == 1:
        is_last_sample = True

    config = load_config('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml')

    paths: dict = setup_paths(input_path=Path(path),input_type=input_type,tag=tag,flowcell=flowcell,config=config)

    logger = setup_logger(logger_name='Logger',log_file=paths['log_file'])

    check_mountpoint(paths=paths, logger=logger)

    check_structure(paths=paths, logger=logger)

    check_docker_image(logger=logger)

    check_rsync(paths=paths, logger=logger)

    check_tso500_script(paths=paths, logger=logger)

    stage_object(paths=paths,input_type=input_type,is_last_sample=is_last_sample,logger=logger)

    process_object(paths=paths,input_type=input_type,is_last_sample=is_last_sample,logger=logger)

    transfer_results(paths=paths,input_type=input_type,is_last_sample=is_last_sample,logger=logger)

    notify_pipeline_status(step='finished',run_name=paths['run_name'],logger=logger,tag=paths['tag'],
                           input_type=input_type, is_last_sample=is_last_sample)

if __name__ == "__main__":
    main()
