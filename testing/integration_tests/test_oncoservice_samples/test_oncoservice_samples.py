import pytest
from pathlib import Path
from shutil import copytree as sh_copytree, copy as sh_copy
from subprocess import run as subp_run, CalledProcessError, check_output as subp_check_output
import yaml



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
def setup_environment(request):
    repo_root = get_repo_root()

    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        onco_seq_dir:Path = Path(config['oncoservice_dir'] + '_TEST') / 'Runs'
        test_onco_samples:Path = Path('/mnt/NovaseqXplus/TSO_pipeline/test_runs/test_samples_oncoservice')
    test_onco_run_seq_dir = onco_seq_dir / 'test_samples'
    pending_blank: Path = Path(f'{repo_root}/testing/functional_tests/scheduler/PENDING_blank.txt')
    pending_file: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/10.200.214.104_PENDING.txt')

    sh_copy(str(pending_blank), str(pending_file))
    if not test_onco_run_seq_dir.exists():
        sh_copytree(str(test_onco_samples),str(test_onco_run_seq_dir))


@pytest.mark.dependency(name="scheduling")
def test_scheduling(setup_environment):
    repo_root = get_repo_root()
    scheduling_call = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/scheduler.py -t'
    subp_run(scheduling_call, check=True, shell=True)


@pytest.mark.dependency(depends=["scheduling"])
def test_processing():
    repo_root = get_repo_root()
    processing_call = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/processing.py -t'
    for i in range(2):
        subp_run(processing_call,check=True,shell=True)
