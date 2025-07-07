from pathlib import Path
import yaml
import argparse
from shutil import copy as sh_copy
import pandas as pd
from helpers import is_server_available, get_server_ip, load_config, setup_paths, check_mountpoint, check_rsync, \
    check_structure, check_docker_image, check_tso500_script, stage_object, process_object, transfer_results, get_queue
from logging_ops import setup_logger, notify_bot



def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script process incoming runs')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser


def main():
    args = create_parser().parse_args()
    testing: bool = args.testing

    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        servers: list = config['available_servers']

    # TODO change in prod
    # if not is_server_available():
    #     return

    server = get_server_ip()
    queue_file = pipeline_dir.parent.parent / f'{server}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server}_PENDING.txt'

    if not queue_file.exists() or queue_file.stat().st_size < 38:
        queue_blank = Path('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt')
        sh_copy(queue_blank, queue_file)

    if not pending_file.exists() or pending_file.stat().st_size < 38:
        queue_blank = Path('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt')
        sh_copy(queue_blank, pending_file)

    queue = get_queue(pending_file=pending_file, queue_file=queue_file)

    if queue is None:
        return

    path, input_type, _, tag, flowcell = queue.iloc[0]

    last_sample_queue = False
    if input_type == 'sample' and len(queue['Tag'][queue['Tag'] == tag]) == 1:
        last_sample_queue = True

    last_sample_run = False
    queues = []
    for server in servers:
        queue_file = pipeline_dir.parent.parent / f'{server}_QUEUE.txt'
        queues.append(pd.read_csv(queue_file, sep='\t'))
    queue_merged = pd.concat(queues, ignore_index=True)
    if len(queue_merged['Tag'][queue_merged['Tag'] == tag]) == 0:
        last_sample_run = True

    config = load_config('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml')

    paths: dict = setup_paths(input_path=Path(path), input_type=input_type, tag=tag, flowcell=flowcell, config=config, testing=testing)

    logger = setup_logger(logger_name='Logger',log_file=paths['log_file'])

    check_mountpoint(paths=paths, logger=logger)
    check_structure(paths=paths, logger=logger)
    check_docker_image(logger=logger)
    check_rsync(paths=paths, logger=logger)
    check_tso500_script(paths=paths, logger=logger)


    if not paths['analyzing_tag'].exists():
        # TODO uncomment in prod
        # paths['analyzing_tag'].touch()
        # paths['queued_tag'].unlink()
    stage_object(paths=paths, input_type=input_type, last_sample_queue=last_sample_queue, logger=logger)

    process_object(paths=paths, input_type=input_type, last_sample_queue=last_sample_queue, logger=logger)

    transfer_results(paths=paths, input_type=input_type, last_sample_queue=last_sample_queue, logger=logger, testing=testing)

    if last_sample_run or input_type == 'run':
        # TODO uncomment in prod
        # paths['analyzed_tag'].touch()
        # paths['analyzing_tag'].unlink()


if __name__ == "__main__":
    main()
