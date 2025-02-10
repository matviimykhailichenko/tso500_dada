from pathlib import Path
import yaml

# TODO add to other crontab scripts

def process_run(pending_tag: Path,
                server_idle_tag: Path,
                server_busy_tag: Path,
                results_dir: Path):
    try:
        server_idle_tag.unlink()
        run_dir = Path(pending_tag).read_text()
        samplesheet_path = Path(run_dir) / 'SampleSheet.csv'
        # TODO not sure if we need this if this is going to be reported to the bot
        # analysing_tag = Path(run_dir) / analysing_tag
        # analysing_tag.touch()
        server_busy_tag.touch()
        # TODO discord bot
        print(f'Here I would process run {run_dir} with this this samplesheet {samplesheet_path} and this results dir {results_dir}')
        server_busy_tag.unlink()
        server_idle_tag.touch()
        pending_tag.unlink()
    except Exception as e:
        raise RuntimeError(f"Error processing run {run_dir}: {e}")

def has_new_runs(runs_dir: Path,
                 blocking_tags: set,
                 ready_tags: set,
                 pending_tag: Path) -> bool:
    try:
        for run_dir in runs_dir.iterdir():
            for dir in run_dir.iterdir():
                if dir.name != 'MyRun':
                    run_files_dir = dir
                else:
                    return False

            txt_files = list(Path(run_files_dir).glob('*.txt'))
            file_names = [path.name for path in txt_files]

            if any(f in blocking_tags for f in file_names):
                continue

            if all(tag in file_names for tag in ready_tags):
                Path(pending_tag).write_text(str(run_dir))
                return True
        return False

    except StopIteration:
        return False
    except Exception as e:
        raise RuntimeError(f"Error checking for new runs: {e}")


def is_server_available(server_idle_tag: Path,
                        server_busy_tag: Path) -> bool:
    try:
        if Path(server_busy_tag).exists() and not Path(server_idle_tag).exists():
            return True
        return False
    except Exception as e:
        # TODO discord bot?
        print(f"Error checking server availability: {e}")
        # Or raise a more specific exception
        raise RuntimeError(f"Failed to check server status: {e}")



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

    if is_server_available(server_idle_tag=server_idle_tag,
                           server_busy_tag=server_busy_tag):
        return

    if not has_new_runs(runs_dir=runs_dir,
                     blocking_tags=blocking_tags,
                     ready_tags=ready_tags,
                     pending_tag=pending_onco_tag):
        return

    process_run(pending_tag=pending_onco_tag,
                server_idle_tag=server_idle_tag,
                server_busy_tag=server_busy_tag,
                results_dir=results_dir)



if __name__ == "__main__":
    main()