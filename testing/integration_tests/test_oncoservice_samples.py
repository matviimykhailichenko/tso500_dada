import pytest
from pathlib import Path
from shutil import copytree as sh_copytree
from subprocess import run as subp_run
import yaml


@pytest.fixture()
def setup_environment():
    with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        onco_seq_dir:Path = Path(config['oncoservice_novaseqx_dir']) / 'Runs'
        test_onco_samples:Path = Path('/mnt/Novaseq/TSO_pipeline/test_runs/test_samples_oncoservice')

    pending_file = pipeline_dir.parent.parent / f'10.200.215.35_PENDING.txt'
    test_onco_run_seq_dir = onco_seq_dir / 'test_run_onco_nsqx'

    if not test_onco_run_seq_dir.exists():
        sh_copytree(str(test_onco_samples),str(test_onco_run_seq_dir))

    yield

    pending_file.unlink()


@pytest.mark.dependency()
def test_scheduling(setup_environment):
    scheduling_call = 'conda run -n tso500_dragen_pipeline python3 /mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/scripts/scheduler.py -t'
    subp_run(scheduling_call, check=True, shell=True)


@pytest.mark.dependency(depends=["test_scheduling"])
def test_processing():
    processing_call = 'conda run -n tso500_dragen_pipeline python3 /mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/scripts/processing.py -t'
    for i in range(2):
        subp_run(processing_call,check=True,shell=True)
