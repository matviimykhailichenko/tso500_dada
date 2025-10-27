import pytest
from pathlib import Path
from shutil import copytree, copy, rmtree, move
from subprocess import run as subp_run, CalledProcessError, check_output as subp_check_output
import yaml
from datetime import datetime
import random, string



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


@pytest.fixture(scope="module")
def setup_environment(request):
    repo_root = get_repo_root()
    today = datetime.now().strftime("%y%m%d")
    run_name = f"{today}_A01664_2749_CICEAJ7JXH"


    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        onco_seq_dir:Path = Path(config['oncoservice_dir'] + '_TEST') / 'Runs'
        test_onco_samples:Path = Path('/mnt/NovaseqXplus/TSO_pipeline/test_runs/test_samples_oncoservice')
    test_onco_run_seq_dir = onco_seq_dir / run_name
    pending_blank: Path = Path(f'{repo_root}/testing/functional_tests/scheduler/PENDING_blank.txt')
    pending_file: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/10.200.214.104_PENDING.txt')

    copy(str(pending_blank), str(pending_file))
    if not test_onco_run_seq_dir.exists():
        copytree(str(test_onco_samples),str(test_onco_run_seq_dir))

    # Provide paths to tests
    yield {
        "pending_file": pending_file,
        "test_run_dir": test_onco_run_seq_dir
    }

    # --- TEARDOWN ---
    fastq_gen_dir = test_onco_run_seq_dir / 'FastqGeneration'
    fastq_arrival_dir = test_onco_run_seq_dir / 'Analysis/1/Data/BCLConvert/fastq'
    for sample_dir in fastq_gen_dir.iterdir():
        for fastq in sample_dir.iterdir():
            move(fastq, fastq_arrival_dir)

    if pending_file.exists():
        pending_file.unlink()


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
