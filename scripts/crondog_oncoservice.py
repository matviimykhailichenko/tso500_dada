from pathlib import Path
import yaml
import argparse



def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script to monitor CBmed sequencing directory')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser


def has_new_runs(runs_dir: Path,
                 blocking_tags: set,
                 ready_tags: set,
                 pending_tag: Path) -> bool:
    try:
        for run_dir in runs_dir.iterdir():
            for o in run_dir.iterdir():
                if not o .is_dir() or o.name == 'MyRun':
                    continue
                else:
                    run_files_dir_path = o

            txt_files = list(Path(run_files_dir_path).glob('*.txt'))
            file_names = [path.name for path in txt_files]

            if any(f in blocking_tags for f in file_names):
                continue

            if all(tag in file_names for tag in ready_tags):
                Path(pending_tag).write_text(str(run_files_dir_path))
                return True
        return False

    except StopIteration:
        return False
    except Exception as e:
        raise RuntimeError(f"Error checking for new runs: {e}")



def main():
    parser = create_parser()
    args = parser.parse_args()

    # Definitions
    with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        ready_tags = set(config['ready_tags'])
        blocking_tags = set(config['blocking_tags'])
        onco_dir = Path(config['oncoservice_dir'])
        runs_onco_dir_path = onco_dir / f'Runs{'_TEST' if args.testing else ''}'
        pending_onco_tag_path = Path(onco_dir / config['pending_run_tag'])

    if not has_new_runs(runs_dir=runs_onco_dir_path,
                     blocking_tags=blocking_tags,
                     ready_tags=ready_tags,
                     pending_tag=pending_onco_tag_path):
        return

if __name__ == "__main__":
    main()