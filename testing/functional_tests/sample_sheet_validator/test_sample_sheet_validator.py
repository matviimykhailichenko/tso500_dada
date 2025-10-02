import pytest
from pathlib import Path
from shutil import copy as sh_copy, copytree as sh_copytree, rmtree as sh_rmtree
from subprocess import run as subp_run
import yaml
import random
import string
from datetime import datetime, timedelta


repo_root = '/mnt/NovaseqXplus/TSO_pipeline/01_Staging/sample-sheet-validator-fix'

def generate_flowcell_names(n=10, start_date=None):
    """
    Generate n flowcell names adhering to the pattern:
    YYMMDD_A01664_####_XXXXXXXXXX
    """
    if start_date is None:
        start_date = datetime.today()

    for i in range(n):
        # Date (YYMMDD)
        date_str = (start_date + timedelta(days=i)).strftime("%y%m%d")
        # Fixed instrument
        instrument = "A01664"
        # 4-digit run number
        run_num = f"{random.randint(0, 9999):04d}"
        # Random 10-char alphanumeric uppercase
        flowcell_id = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))

        yield f"{date_str}_{instrument}_{run_num}_{flowcell_id}"

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

            test_run_name = list(generate_flowcell_names(1))[0]
            current_test_run = mixed_runs_dir / test_run_name
            if not current_test_run.exists():
                sh_copytree(str(test_run_ns6000), str(current_test_run))

            sample_sheet_run_dir = current_test_run / '250213_A01664_0452_AH2J5VDMX2' / 'SampleSheet.csv'
            sh_copy(str(sample_sheet), str(sample_sheet_run_dir))

        elif 'Analysis' in sample_sheet.name:
            sample_sheet_counter += 1
            test_flowcell_name = f'test_flowcell{sample_sheet_counter}'
            current_test_run = mixed_runs_dir / test_flowcell_name
            if not current_test_run.exists():
                sh_copytree(str(test_run_nsx), str(current_test_run))

            sample_sheet_run_dir = current_test_run / 'SampleSheet_Analysis.csv'
            sh_copy(str(sample_sheet), str(sample_sheet_run_dir))


def test_scheduler(setup_environment):
    scheduler_call = f'/staging/env/tso500_dragen_pipeline/bin/python3 {repo_root}/scripts/scheduler.py -t'
    for i in range(1):
        subp_run(scheduler_call,check=True,shell=True)
