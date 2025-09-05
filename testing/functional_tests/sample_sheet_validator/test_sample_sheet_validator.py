import pytest
from pathlib import Path
from shutil import copy as sh_copy, copytree as sh_copytree, rmtree as sh_rmtree
from subprocess import run as subp_run
import yaml


repo_root = '/mnt/NovaseqXplus/TSO_pipeline/01_Staging/sample-sheet-validator'



@pytest.fixture()
def setup_environment():
    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        test_run_ns6000: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/test_runs/mock/test_run_ns6000')
        test_run_nsx: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/test_runs/mock/test_run_nsx')
        mixed_runs_dir: Path = Path(config['mixed_runs_dir'] + '_TEST')

    sample_sheet_dir = Path(f'{repo_root}/testing/functional_tests/sample_sheet_validator/sample_sheets')

    sample_sheet_counter = 0
    for sample_sheet in sample_sheet_dir.iterdir():
        if 'Analysis' not in sample_sheet.name:
            sample_sheet_counter += 1
            test_run_name = f'test_run{sample_sheet_counter}'
            current_test_run = mixed_runs_dir / test_run_name
            if not current_test_run.exists():
                sh_copytree(str(test_run_ns6000), str(current_test_run))

            sample_sheet_run_dir = current_test_run / '250213_A01664_0452_AH2J5VDMX2' / 'SampleSheet.csv'
            sh_copy(str(sample_sheet), str(sample_sheet_run_dir))

        elif 'Analysis' in sample_sheet.name:
            sample_sheet_counter += 1
        #     test_flowcell_name = f'test_flowcell{sample_sheet_counter}'
        #     current_test_run = mixed_runs_dir / test_flowcell_name
        #     if not current_test_run.exists():
        #         sh_copytree(str(test_run_nsx), str(current_test_run))
        #
        #     sample_sheet_run_dir = current_test_run / 'SampleSheet_Analysis.csv'
        #     sh_copy(str(sample_sheet), str(sample_sheet_run_dir))

        else:
            raise RuntimeError('Unexpected run type')


def test_scheduler(setup_environment):
    scheduler_call = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/scheduler.py -t'
    for i in range(11):
        subp_run(scheduler_call,check=True,shell=True)
