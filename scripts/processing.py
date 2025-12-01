from pathlib import Path
import yaml
import argparse
import pandas as pd
from helpers import is_server_available, get_server_ip, setup_paths, check_mountpoint, check_rsync, \
    check_structure, check_docker_image, check_tso500_script, stage_object, process_object, transfer_results, \
    get_queue, merge_metrics, get_repo_root, run_ichorCNA
from logging_ops import setup_logger



def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script process incoming runs')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    parser.add_argument('-tf', '--testing_fast',action='store_true', help='Fast testing mode')

    return parser


def main():
    args = create_parser()
    testing = args.testing
    testing_fast = args.testing_fast
    repo_root = get_repo_root()

    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        servers = config['available_servers']
        server_availability_dir = Path(config['server_availability_dir'])
        server = get_server_ip()
        idle_tag = server_availability_dir / server / config['server_idle_tag']
        busy_tag = server_availability_dir / server / config['server_busy_tag']

    if not is_server_available(repo_root=repo_root):
        return

    queue_file = Path(repo_root).parent.parent / f'{server}_QUEUE.txt'
    pending_file = Path(repo_root).parent.parent / f'{server}_PENDING.txt'

    queue = get_queue(pending_file=pending_file, queue_file=queue_file, repo_root=repo_root)

    if queue is None:
        return

    busy_tag.touch()
    idle_tag.unlink()

    input_path, input_type, _, tag, flowcell = queue.iloc[0]

    last_sample_queue = False
    if input_type == 'sample' and len(queue['Tag'][queue['Tag'] == tag]) == 1:
        last_sample_queue = True

    last_sample_run = False
    queues = []
    for server in servers:
        queue_file = Path(repo_root).parent.parent / f'{server}_QUEUE.txt'
        queues.append(pd.read_csv(queue_file, sep='\t'))
    queue_merged = pd.concat(queues, ignore_index=True)
    if len(queue_merged['Flowcell'][queue_merged['Flowcell'] == flowcell]) == 0:
        last_sample_run = True

    paths = setup_paths(repo_root=repo_root, input_path=Path(input_path), input_type=input_type, tag=tag, flowcell=flowcell, config=config,
                              testing=testing, testing_fast=testing_fast)
    try:
        logger = setup_logger(logger_name='Logger',log_file=paths['log_file'])
        check_mountpoint(paths=paths, logger=logger)
        check_structure(paths=paths, logger=logger)
        check_docker_image(paths=paths, logger=logger)
        check_rsync(paths=paths, logger=logger)
        check_tso500_script(paths=paths, logger=logger)

        if paths['failed_tag'].exists() and not paths['analyzing_tag'].exists():
            paths['analyzing_tag'].touch()
        elif not paths['failed_tag'].exists() and not paths['analyzing_tag'].exists():
            paths['analyzing_tag'].touch()
            paths['queued_tag'].unlink()

        stage_object(paths=paths, input_type=input_type, last_sample_queue=last_sample_queue, logger=logger)

        process_object(paths=paths, input_type=input_type, last_sample_queue=last_sample_queue, logger=logger)

        if tag == 'ONC':
            run_ichorCNA(paths=paths, input_type=input_type, last_sample_queue=last_sample_queue, logger=logger)

        transfer_results(paths=paths, input_type=input_type, last_sample_queue=last_sample_queue, logger=logger, testing=testing)

        if last_sample_queue:
            merge_metrics(paths=paths)
        if last_sample_run or input_type == 'run':
            paths['analyzed_tag'].touch()
            paths['analyzing_tag'].unlink()

    except Exception:
        paths['failed_tag'].touch()
        paths['analyzing_tag'].unlink()
        raise RuntimeError
    finally:
        idle_tag.touch()
        busy_tag.unlink()


if __name__ == "__main__":
    main()
