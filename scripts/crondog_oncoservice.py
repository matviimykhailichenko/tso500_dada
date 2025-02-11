from pathlib import Path
import yaml



# TODO add to other crontab scripts
def has_new_runs(runs_dir: Path,
                 blocking_tags: set,
                 ready_tags: set,
                 pending_tag: Path) -> bool:
    try:
        for run_dir in runs_dir.iterdir():
            for dir in run_dir.iterdir():
                if dir.name != 'MyRun':
                    run_files_dir_path = dir
                else:
                    return False

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
    # Definitions
    with open('../config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        ready_tags = set(config['ready_tags'])
        blocking_tags = set(config['blocking_tags'])
        base_dir = config['base_dir']
        onco_dir = Path(base_dir) / config['oncoservice_dir']
        cbmed_dir = Path(base_dir) / config['cbmed_dir']
        results_dir = Path(base_dir) / config['results_dir']
        runs_dir = onco_dir / 'Runs'
        pending_onco_tag = Path(onco_dir / config['pending_run_tag'])
        pending_cbmed_tag = Path(cbmed_dir / config['pending_run_tag'])
        server_availability_dir = Path(base_dir) / config['server_availability_dir']
        server_idle_tag = server_availability_dir / config['server_idle_tag']
        server_busy_tag = server_availability_dir / config['server_busy_tag']


    if not has_new_runs(runs_dir=runs_dir,
                     blocking_tags=blocking_tags,
                     ready_tags=ready_tags,
                     pending_tag=pending_onco_tag):
        return

if __name__ == "__main__":
    main()