import argparse
from helpers import scan_dir_nsq6000, scan_dir_nsqx, append_pending_run, append_pending_samples, \
    rearrange_fastqs, setup_paths_scheduler, get_server_ip, get_repo_root
from shutil import copy as sh_copy
from logging_ops import notify_bot
import re
import yaml
from pathlib import Path


def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script to monitor sequencing directories')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    testing = args.testing

    repo_root = get_repo_root()

    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        servers = config['available_servers']
        queue_blank = Path(f'{repo_root}/testing/functional_tests/scheduler/PENDING_blank.txt')

    paths = setup_paths_scheduler(testing=testing, repo_root=repo_root)
    # TODO assumption: for now CBmed are only on NS6000 and version 2.1.
    seq_dirs = [paths['onco_seq_dir'], paths['mixed_runs_dir'], paths['research_seq_dir']]
    if get_server_ip() == '10.200.215.35':
        seq_dirs.append(paths['patho_seq_dir'])
        seq_dirs.append(paths['cbmed_seq_dir'])

    for server in servers:
        queue_file = Path(repo_root).parent.parent / f'{server}_QUEUE.txt'
        pending_file = Path(repo_root).parent.parent / f'{server}_PENDING.txt'
        if not queue_file.exists():
            sh_copy(queue_blank, queue_file)
        if not pending_file.exists():
            sh_copy(queue_blank, pending_file)

    input_path = None
    input_type = None
    sample_ids = None
    for seq_dir in seq_dirs:
        for run_dir in seq_dir.iterdir():
            if not run_dir.is_dir():
                continue
            analysis_dir = run_dir / 'Analysis'
            data_dir = run_dir / 'Data'
            myrun_dir = run_dir / 'MyRun'
            flowcell_dir = None
            for obj in run_dir.iterdir():
                if obj.is_dir() and re.search(r'^\d{6}_A01664_\d{4}_[A-Z0-9]{10}$', obj.name):
                    flowcell_dir = obj

            if analysis_dir.exists() and data_dir.exists():
                input_type = 'sample'
                input_path = scan_dir_nsqx(run_dir=run_dir, repo_root=repo_root)
                flowcell_name = run_dir.name
                flowcell_dir = run_dir

            elif myrun_dir.exists() and flowcell_dir is not None:
                input_type = 'run'
                input_path = scan_dir_nsq6000(flowcell_dir=flowcell_dir, repo_root=repo_root)

            if not input_path or flowcell_dir is None:
                continue

            if input_path:
                if input_type == 'sample':
                    sample_ids: list = rearrange_fastqs(paths=paths, fastq_dir=input_path)

                notify_bot(f'Found run {run_dir}')
                break

        if input_path:
            break

    if not input_path or not input_type:
        return

    if input_type == 'run':
        append_pending_run(repo_root=repo_root, paths=paths, input_dir=input_path, testing=testing)
    elif input_type == 'sample':
        append_pending_samples(repo_root=repo_root, paths=paths, flowcell_name=flowcell_name, input_dir=input_path, sample_ids=sample_ids, testing=testing)
    else:
        raise RuntimeError(f'Unrecognised input type: {input_type}')


if __name__ == '__main__':
    main()