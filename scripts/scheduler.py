import argparse
import yaml
from pathlib import Path
from scripts.helpers import scan_dir_nsq6000, scan_dir_nsqx, append_pending_run, append_pending_samples, rearrange_fastqs
from scripts.logging_ops import notify_bot


def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script to monitor sequencing directories')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser



def main():
    parser = create_parser()
    args = parser.parse_args()
    testing = args.testing

    with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        sx182_mountpoint = config['sx182_mountpoint']
        sy176_mountpoint = config['sy176_mountpoint']
        onco_nsq6000_dir = Path(config['oncoservice_novaseq6000_dir']) / f'Runs{'_TEST' if testing else ''}'
        onco_nsqx_dir = Path(config['oncoservice_novaseqx_dir'] + '_TEST' if testing else '') / 'Runs'
        cbmed_nsq6000_dir = Path(config['cbmed_nsq6000_dir']+ f'{'_TEST' if testing else ''}')
        # TODO STUPID
        cbmed_nsqx_dir = Path(f'/mnt/NovaseqXplus/08_Projekte{'_TEST' if testing else ''}') / 'Runs'
        patho_dir = Path(config['pathology_dir'])
        mixed_runs_dir = Path(config['mixed_runs_dir'])
    seq_dirs = [onco_nsq6000_dir, onco_nsqx_dir, cbmed_nsq6000_dir, cbmed_nsqx_dir, patho_dir, mixed_runs_dir]

    input_path = None
    input_type = None
    sample_ids = None
    for dir in seq_dirs:
        if sx182_mountpoint in str(dir):
            input_type = 'run'
            input_path = scan_dir_nsq6000(seq_dir=dir)

        elif sy176_mountpoint in str(dir):
            input_type = 'sample'
            input_path = scan_dir_nsqx(seq_dir=dir)
            sample_ids: list = rearrange_fastqs(fastq_dir=input_path)
        else:
            RuntimeError(f'Unrecognised sequencing directory: {str(dir)}')

    if not input_path or not input_type:
        exit(0)

    if input_type == 'run':
        append_pending_run(input_dir=input_path, testing=testing)
    elif input_type == 'sample':
        append_pending_samples(input_dir=input_path, sample_ids=sample_ids, testing=testing)
    else:
        RuntimeError(f'Unrecognised input type: {input_type}')


if __name__ == '__main__':
    main()