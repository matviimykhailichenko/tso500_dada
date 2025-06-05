from pathlib import Path
import yaml
from crondog_oncoservice import has_new_runs
import argparse



def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script to monitor CBmed sequencing directory')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser



def main():
    parser = create_parser()
    args = parser.parse_args()

    # Definitions
    with open('/mnt/Novaseq/TSO_pipeline/03_Production/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        ready_tags = set(config['ready_tags'])
        blocking_tags = set(config['blocking_tags'])
        cbmed_dir = Path(config['cbmed_dir'])

        runs_cbmed_dir_path = cbmed_dir / f'Runs{'_TEST' if args.testing else ''}'
        pending_cbmed_tag = Path(cbmed_dir / config['pending_run_tag'])

    if not has_new_runs(runs_dir=runs_cbmed_dir_path):
        return

if __name__ == "__main__":
    main()