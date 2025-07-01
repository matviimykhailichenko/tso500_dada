import argparse
from helpers import scan_dir_nsq6000, scan_dir_nsqx, append_pending_run, append_pending_samples, \
    rearrange_fastqs, setup_paths_scheduler, get_server_ip
from logging_ops import notify_bot
import re


def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script to monitor sequencing directories')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser



def main():
    parser = create_parser()
    args = parser.parse_args()
    testing = args.testing

    paths = setup_paths_scheduler(testing=testing)
    seq_dirs = [paths['onco_seq_dir'], paths['cbmed_seq_dir'], paths['mixed_runs_dir']]
    if get_server_ip() == '10.200.215.35':
        seq_dirs.append(paths['patho_seq_dir'])
    input_path = None
    input_type = None
    sample_ids = None
    for seq_dir in seq_dirs:
        notify_bot(str(seq_dir))
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
                notify_bot(f'Found NSQX+ run {run_dir}')
                input_type = 'sample'
                input_path = scan_dir_nsqx(run_dir=run_dir)
                sample_ids: list = rearrange_fastqs(fastq_dir=input_path)
            elif myrun_dir.exists() and flowcell_dir is not None:
                notify_bot(f'Found NSQ6000 run {run_dir}')
                input_type = 'run'
                input_path = scan_dir_nsq6000(flowcell_dir=flowcell_dir)

            if not input_path:
                continue
        else:
            RuntimeError(f'Unrecognised sequencing directory: {str(dir)}')

        if input_path:
            break

    if not input_path or not input_type:
        exit(0)

    if input_type == 'run':
        append_pending_run(paths=paths, input_dir=input_path, testing=testing)
    elif input_type == 'sample':
        append_pending_samples(paths=paths, input_dir=input_path, sample_ids=sample_ids, testing=testing)
    else:
        RuntimeError(f'Unrecognised input type: {input_type}')


if __name__ == '__main__':
    main()