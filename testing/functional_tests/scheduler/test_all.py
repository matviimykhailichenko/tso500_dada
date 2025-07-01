import pytest
from pathlib import Path
from shutil import copytree as sh_copytree
from subprocess import run as subp_run
import yaml


@pytest.fixture()
def setup_environment():
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        onco_seq_dir:Path = Path(config['oncoservice_sequencing_dir'] +'_TEST') / 'Runs'
        cbmed_seq_dir:Path = Path(config['cbmed_sequencing_dir'] +'_TEST') / 'Runs'
        mixed_seq_dir:Path = Path(config['mixed_runs_dir'] +'_TEST')
        test_run:Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_oncoservice_1')
        test_samples:Path = Path('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_onco_nsqx')
    test_onco_run_seq_dir = onco_seq_dir / 'test_run'
    test_cbmed_run_seq_dir = cbmed_seq_dir / 'test_run'
    test_mixed_run_seq_dir = mixed_seq_dir / 'test_run'
    test_onco_samples_seq_dir = onco_seq_dir / 'test_samples'
    test_cbmed_samples_seq_dir = cbmed_seq_dir / 'test_samples'
    test_mixed_samples_seq_dir = mixed_seq_dir / 'test_samples'

    if not test_onco_run_seq_dir.exists():
        sh_copytree(str(test_run),str(test_onco_run_seq_dir))

    if not test_cbmed_run_seq_dir.exists():
        sh_copytree(str(test_run), str(test_cbmed_run_seq_dir))

    if not test_mixed_run_seq_dir.exists():
        sh_copytree(str(test_run), str(test_mixed_run_seq_dir))

    if not test_onco_samples_seq_dir.exists():
        sh_copytree(str(test_samples),str(test_onco_samples_seq_dir))

    if not test_cbmed_samples_seq_dir.exists():
        sh_copytree(str(test_samples), str(test_cbmed_samples_seq_dir))

    if not test_mixed_samples_seq_dir.exists():
        sh_copytree(str(test_samples), str(test_mixed_samples_seq_dir))


def test_scheduler(setup_environment):
    scheduler_call = 'python3 /mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/scripts/scheduler.py -t'
    for i in range(6):
        subp_run(scheduler_call,check=True,shell=True)
