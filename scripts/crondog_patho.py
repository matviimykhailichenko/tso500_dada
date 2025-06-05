from pathlib import Path
import yaml
from crondog_oncoservice import has_new_runs
import argparse



# def create_parser():
#     parser = argparse.ArgumentParser(description='This is a crontab script to monitor CBmed sequencing directory')
#     parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
#     return parser



def main():
    # parser = create_parser()
    # args = parser.parse_args()

    # Definitions
    with open('/mnt/Novaseq/TSO_pipeline/03_Production/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        ready_tags = set(config['ready_tags'])
        blocking_tags = set(config['blocking_tags'])
        patho_dir = Path(config['patho_dir'])
        pending_patho_tag_path = Path(patho_dir / config['pending_run_tag'])

    if not has_new_runs(patho_dir,
                     blocking_tags,
                     ready_tags,
                     pending_patho_tag_path):
        return

if __name__ == "__main__":
    main()