# Monitor Oncoservice
# Monitor CBmed
# Monitor Patho

import argparse
import yaml
from pathlib import Path
from helpers import scan_dir

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
        onco_nsq6000_dir = Path(config['oncoservice_novaseq6000_dir']) / f'Runs {'_TEST' if testing else ''}'
        onco_nsqx_dir = Path(config['oncoservice_novaseqx_dir'] + '_TEST' if testing else '') / 'Runs'
        cbmed_nsq6000_dir = Path(config['cbmed_nsq6000_dir']) / f'Runs {'_TEST' if testing else ''}'
        # TODO STUPID
        cbmed_nsqx_dir = Path(f'/mnt/NovaseqXplus/08_Projekte{'_TEST' if testing else ''}') / 'Runs'
        patho_dir = Path(config['pathology_dir'])
        mixed_runs_dir = Path(config['mixed_runs'])
    seq_dirs = [onco_nsq6000_dir, onco_nsqx_dir, cbmed_nsq6000_dir, cbmed_nsqx_dir, patho_dir, mixed_runs_dir]

    for dir in seq_dirs:
        if not scan_dir(dir):
            pass


if __name__ == '__main__':
    main()