import pytest
from pathlib import Path
from shutil import copy as sh_copy, copytree as sh_copytree, rmtree as sh_rmtree
from subprocess import run as subp_run, check_output as subp_check_output, CalledProcessError
import yaml
from datetime import datetime


def get_repo_root() -> str:
    script_path = Path(__file__).parent
    try:
        root = subp_check_output(
            f"cd {script_path} && git rev-parse --show-toplevel",
            text=True, shell=True
        ).strip()
        return root
    except CalledProcessError:
        raise RuntimeError("Not inside a git repository")


@pytest.fixture()
def setup_environment():
    repo_root = get_repo_root()
    today = datetime.now().strftime("%Y%m%d")
    run_name = f"{today}_A01664_2749_CICEAJ7JXH"
    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        onco_seq_dir:Path = Path(config['oncoservice_sequencing_dir'] + '_TEST') / 'Runs'
        pending_blank:Path = Path(f'{repo_root}/testing/functional_tests/scheduler/PENDING_blank.txt')
        test_onco_run:Path = Path('/mnt/NovaseqXplus/TSO_pipeline/test_runs/mock/test_run_nsx_onc')
    server_ip = '10.200.214.104'
    pending_file = pipeline_dir / f'{server_ip}_PENDING.txt'
    test_onco_run_seq_dir = onco_seq_dir / run_name

    if test_onco_run_seq_dir.exists():
        sh_rmtree(test_onco_run_seq_dir)
    if pending_file.exists():
        pending_file.unlink()

    sh_copytree(str(test_onco_run), str(test_onco_run_seq_dir))
    sh_copy(str(pending_blank),str(pending_file))

    yield


def test_scheduler(setup_environment):
    repo_root = get_repo_root()
    cmd = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/scheduler.py -t'

    subp_run(cmd,check=True,shell=True)
