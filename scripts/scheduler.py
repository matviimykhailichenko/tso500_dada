import argparse
import yaml
from pathlib import Path
from scripts.helpers import scan_dir_nsq6000, scan_dir_nsqx, append_pending_run, append_pending_samples, \
    rearrange_fastqs, setup_paths_scheduler
from scripts.logging_ops import notify_bot


def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script to monitor sequencing directories')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser



def main():
    parser = create_parser()
    args = parser.parse_args()
    testing = args.testing

    paths = setup_paths_scheduler(testing=testing)
    seq_dirs = [paths['onco_nsq6000_dir'], paths['onco_nsqx_dir'], paths['cbmed_nsq6000_dir'], paths['cbmed_nsqx_dir'],
                paths['patho_seq_dir'], paths['mixed_runs_dir']]
    input_path = None
    input_type = None
    sample_ids = None
    for dir in seq_dirs:
        if paths['sx182_mountpoint'] or paths['patho_seq_dir'] in str(dir):
            input_type = 'run'
            input_path = scan_dir_nsq6000(seq_dir=dir)

        elif paths['sy176_mountpoint'] in str(dir):
            notify_bot(str(dir))
            input_type = 'sample'
            input_path = scan_dir_nsqx(seq_dir=dir)
            if not input_path:
                continue
            sample_ids: list = rearrange_fastqs(fastq_dir=input_path)
        else:
            RuntimeError(f'Unrecognised sequencing directory: {str(dir)}')

        if input_path:
            break

    if not input_path or not input_type:
        exit(0)

    if input_type == 'run':
        append_pending_run(paths=paths, input_dir=input_path, testing=testing)
    elif input_type == 'sample':
        append_pending_samples(input_dir=input_path, sample_ids=sample_ids, testing=testing)
    else:
        RuntimeError(f'Unrecognised input type: {input_type}')


if __name__ == '__main__':
    main()