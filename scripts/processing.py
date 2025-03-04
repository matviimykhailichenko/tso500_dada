from pathlib import Path
from subprocess import CalledProcessError
import yaml
import subprocess
import argparse
from scripts.helpers import is_server_available
from scripts.logging_ops import notify_bot


def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script process incoming runs')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser


def process_run(run_type: str,
                testing: bool):
    with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir_path = Path(config['pipeline_dir'])
        onco_dir_path = Path(config['onco_dir'])
        server_availability_dir = Path(config['server_availability_dir'])
        server_idle_tag = server_availability_dir / config['server_idle_tag']
        server_busy_tag = server_availability_dir / config['server_busy_tag']
        cbmed_seqencing_dir = Path(config['cbmed_seqencing_dir'])
        pending_tag = config['pending_run_tag']
        
    try:
        if run_type == 'oncoservice':
            pending_tag_path = onco_dir_path / pending_tag
            run_files_dir_path = Path(pending_tag_path).read_text()

        elif run_type == 'cbmed':
            pending_tag_path = cbmed_seqencing_dir / pending_tag
            run_files_dir_path = Path(pending_tag_path).read_text()

        elif run_type == 'patho':
            pending_tag_path = cbmed_seqencing_dir / pending_tag
            run_files_dir_path = Path(pending_tag_path).read_text()

        else:
            notify_bot(f"Unrecognised run type: {run_type}")
            raise RuntimeError(f"Unrecognised run type: {run_type}") # TODO log

        server_idle_tag.unlink()
        snakefile_path = pipeline_dir_path / 'snakefile'
        config_file_path = pipeline_dir_path / 'config.yaml'
        # TODO not sure if we need this if this is going to be reported to the bot
        # analysing_tag = Path(run_dir) / analysing_tag
        # analysing_tag.touch()
        server_busy_tag.touch()
        # TODO discord bot

        snakemake_cmd =[
                "conda", "run", "-n", "tso500_dragen_pipeline",
                "snakemake", "-s", str(snakefile_path),
                "--configfile", str(config_file_path),
                "--config", f"run_files_dir_path={str(run_files_dir_path)}", f'run_type={run_type}', f'testing={str(testing)}'
        ]
        try:
            subprocess.run(snakemake_cmd).check_returncode()
        except CalledProcessError as e:
            # failed_tag_path = run_files_dir_path / failed_tag
            # failed_tag_path.touch()
            raise RuntimeError(f"Error processing run {run_files_dir_path}: {e}")

        print(f'Processing run {run_files_dir_path}')
        server_busy_tag.unlink()
        server_idle_tag.touch()
        pending_tag_path.unlink()
    except Exception as e:
        raise RuntimeError(f"Error processing run {run_files_dir_path}: {e}")


def check_pending_runs(pending_onco_tag: Path,
                       pending_cbmed_tag: Path):
    with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        onco_dir_path = Path(config['oncoservice_dir'])
        cbmed_seqencing_dir = Path(config['cbmed_seqencing_dir'])
        pending_onco_tag = Path(onco_dir_path / config['pending_run_tag'])
        pending_cbmed_tag = Path(cbmed_seqencing_dir / config['pending_run_tag'])

    if pending_onco_tag.exists():
        return 'oncoservice'
    elif pending_cbmed_tag.exists():
        return 'cbmed'
    else:
        print('No Oncoservice or CBmed runs are detected, quitting...')
        return None



def main():
    parser = create_parser()
    args = parser.parse_args()
    # TODO put in prod
    # Definitions
    with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        failed_tag = config['blocking_tags'][1]

    if is_server_available:
        return

    run_type = check_pending_runs()

    if run_type is None:
        pass

    # TODO check an assumption that there would not be 2 runs of one type
    process_run(run_type=run_type,
                testing=args.testing)

if __name__ == "__main__":
    main()
