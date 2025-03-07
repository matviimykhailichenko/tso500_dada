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


def process_run(run_type: str = 'None',
                testing: bool = False):
    with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir_path = Path(config['pipeline_dir'])
        onco_dir_path = Path(config['oncoservice_dir'])
        server_availability_dir = Path(config['server_availability_dir'])
        server_idle_tag = server_availability_dir / config['server_idle_tag']
        server_busy_tag = server_availability_dir / config['server_busy_tag']
        cbmed_seqencing_dir = Path(config['cbmed_seqencing_dir'])
        pending_tag = config['pending_run_tag']

    if testing:
        if run_type == 'oncoservice':
            run_files_dir_path: Path = Path(config['oncoservice_dir']) / 'Runs_TEST' / f'test_run{run_type}'
        elif run_type == 'cbmed':
            run_files_dir_path: Path = Path(config['cbmed_seqencing_dir']) / 'Runs_TEST' / f'test_run{run_type}'

    elif run_type == 'oncoservice':
        pending_tag_path = onco_dir_path / pending_tag
        run_files_dir_path = pending_tag_path.read_text()

    elif run_type == 'cbmed':
        pending_tag_path = cbmed_seqencing_dir / pending_tag
        run_files_dir_path = pending_tag_path.read_text()

    elif run_type == 'patho':
        pending_tag_path = cbmed_seqencing_dir / pending_tag
        run_files_dir_path = pending_tag_path.read_text()
    else:
        notify_bot(f"Unrecognised run type: {run_type}")
        raise RuntimeError(f"Unrecognised run type: {run_type}")

    failed_tag: Path = run_files_dir_path / config['failed_tag']
    analysed_tag: Path = run_files_dir_path / config['analysed_tag']
    server_idle_tag.unlink()
    snakefile_path = pipeline_dir_path / 'snakefile'
    config_file_path = pipeline_dir_path / 'config.yaml'
    server_busy_tag.touch()

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
        message = f"Error processing run {run_files_dir_path}: {e.stderr}"
        notify_bot(message)
        failed_tag.touch()
        raise RuntimeError(message)

    analysed_tag.touch()
    server_busy_tag.unlink()
    server_idle_tag.touch()
    pending_tag_path.unlink()


def check_pending_runs():
    with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        onco_dir_path = Path(config['oncoservice_dir'])
        cbmed_seqencing_dir = Path(config['cbmed_seqencing_dir'])
        pending_onco_tag = Path(onco_dir_path / config['pending_run_tag'])
        pending_cbmed_tag = Path(cbmed_seqencing_dir / config['pending_run_tag'])

    if pending_onco_tag.exists():
        print('Oncoservice run was detected')
        return 'oncoservice'
    elif pending_cbmed_tag.exists():
        print('CBmed run was detected')
        return 'cbmed'
    else:
        print('No Oncoservice or CBmed runs are detected, quitting...')
        return None


def main():
    args = create_parser().parse_args()
    testing: bool = args.testing

    if is_server_available():
        return

    if testing:
        process_run(testing=args.testing)
    else:
        run_type = check_pending_runs()
        if run_type is None:
            pass
        else:
            # TODO check an assumption that there would not be 2 runs of one type
            process_run(run_type=run_type, testing=False)


if __name__ == "__main__":
    main()
