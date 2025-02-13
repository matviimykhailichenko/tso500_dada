from pathlib import Path
import yaml
import subprocess
import argparse
from helpers import is_server_available


def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script process incoming runs')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser


def process_run(run_type: str,
                pipeline_dir: Path,
                onco_dir_path: Path,
                cbmed_dir_path: Path,
                server_idle_tag: Path,
                server_busy_tag: Path,
                pending_tag: str,
                testing: bool):
    try:
        if run_type == 'oncoservice':
            pending_tag_path = onco_dir_path / pending_tag
            run_files_dir_path = Path(pending_tag_path).read_text()
            results_dir_path = onco_dir_path/ f'Analyseergebnisse{'_TEST' if testing else ''}'

        elif run_type == 'cbmed':
            pending_tag_path = cbmed_dir_path / pending_tag
            run_files_dir_path = Path(pending_tag_path).read_text()
            results_dir_path = cbmed_dir_path / Path(run_files_dir_path).name

        else:
            raise RuntimeError(f"Unrecognised run type") # TODO log

        server_idle_tag.unlink()
        snakefile_path = str(pipeline_dir / 'snakefile')
        config_file_path = str(pipeline_dir / 'config.yaml')
        # TODO not sure if we need this if this is going to be reported to the bot
        # analysing_tag = Path(run_dir) / analysing_tag
        # analysing_tag.touch()
        server_busy_tag.touch()
        # TODO discord bot

        try:
            subprocess.run([ # TODO check if it runs on full cores
                "conda", "run", "-n", "tso500_dragen_pipeline",
                "snakemake", "-s", snakefile_path,
                "--configfile", config_file_path,
                "--config", f"run_files_dir_path={run_files_dir_path}", f'results_dir_path={results_dir_path}', f'run_type={run_type}'
            ])
        except Exception as e:
            # TODO put failed tag
            raise RuntimeError(f"Error processing run {run_files_dir_path}: {e}")

        print(f'Processing run {run_files_dir_path}')
        server_busy_tag.unlink()
        server_idle_tag.touch()
        pending_tag_path.unlink()
    except Exception as e:
        raise RuntimeError(f"Error processing run {run_files_dir_path}: {e}")


def check_pending_runs(pending_onco_tag: Path,
                    pending_cbmed_tag: Path):
    if pending_onco_tag.exists():
        return 'oncoservice'
    elif pending_cbmed_tag.exists():
        return 'cbmed'
    else:
        # TODO change to logging
        print('No Oncoservice or CBmed runs are detected, quitting...')



def main():
    parser = create_parser()
    args = parser.parse_args()
    # TODO make a class that would pull every definition
    # Definitions
    with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir = Path(config['pipeline_dir'])
        onco_dir_path = Path(config['oncoservice_dir'])
        cbmed_dir_path = Path(config['cbmed_dir'])
        pending_tag = config['pending_run_tag']
        pending_onco_tag = Path(onco_dir_path / config['pending_run_tag'])
        pending_cbmed_tag = Path(cbmed_dir_path / config['pending_run_tag'])
        server_availability_dir = Path(config['server_availability_dir'])
        server_idle_tag = server_availability_dir / config['server_idle_tag']
        server_busy_tag = server_availability_dir / config['server_busy_tag']

    if is_server_available(server_idle_tag=server_idle_tag,
                           server_busy_tag=server_busy_tag):
        return

    run_type = check_pending_runs(pending_onco_tag=pending_onco_tag,
                               pending_cbmed_tag=pending_cbmed_tag)

    # TODO check an assumption that there would not be 2 runs of one type
    process_run(run_type=run_type,
                pipeline_dir=pipeline_dir,
                onco_dir_path=onco_dir_path,
                cbmed_dir_path=cbmed_dir_path,
                server_idle_tag=server_idle_tag,
                server_busy_tag=server_busy_tag,
                pending_tag=pending_tag,
                testing=args.testing)

if __name__ == "__main__":
    main()
