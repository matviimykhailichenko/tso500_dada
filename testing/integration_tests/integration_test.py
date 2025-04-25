from shutil import copytree, rmtree
import pytest
import yaml
from pathlib import Path
from subprocess import run as subp_run, CalledProcessError
from scripts.processing import process_run
# TODO add a log file and notify bot that it had failed



config_path: str = "/mnt/Novaseq/TSO_Pipeline/01_Staging/pure-python-refactor/config.yaml"



# TODO copy test run to seqencing directory for Patho
# TODO get CBmed and Patho test runs
@pytest.fixture(params=['oncoservice',
                        # 'cbmed',
                        # 'patho'
                        ])
def test_environment(request):
    run_type:str = request.param
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        run_name: str = f'test_run_{run_type}'
        test_run: Path = Path(config['test_runs_dir']) / run_name
        if run_type == 'oncoservice':
            sequencing_dir: Path = Path(config['oncoservice_dir']) / 'Runs_TEST'
            results_dir: Path = Path(config['oncoservice_dir']) / 'Analyseergebnisse_TEST'
        elif run_type == 'cbmed':
            sequencing_dir: Path = Path(config['cbmed_seqencing_dir']) / 'Runs_TEST'
            results_dir: Path = Path(config['cbmed_results_dir'])
        elif run_type == 'patho':
            pass
        else:
            raise RuntimeError(f'Unknown run type :{run_type}')
        test_run_seq_dir: Path = sequencing_dir / run_name
        test_run_results: Path = results_dir / test_run.name
        test_checksums_file: Path = results_dir / f'{test_run.name}.sha256'

    copytree(str(test_run), str(test_run_seq_dir))

    yield run_type, test_run, results_dir, test_checksums_file, sequencing_dir, test_run_seq_dir

    if test_run_seq_dir.exists():
        rmtree(test_run_seq_dir)

    if test_run_results.exists():
        rmtree(test_run_results)

    if test_checksums_file.exists():
        test_checksums_file.unlink()


@pytest.mark.order(1)
def test_process_run(test_environment):
    run_type, test_run, _, _, sequencing_dir, test_run_seq_dir = test_environment
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        pending_tag: Path = sequencing_dir / config['pending_run_tag']
    with open(str(pending_tag), 'w'):
        file.write(str(test_run_seq_dir))

    try:
        process_run(str(run_type),
                    testing=True)
    except Exception as e:
        pytest.fail(f"Process run failed for {run_type} test run: {e}")


@pytest.mark.order(2)
def validate_checksums(test_environment):
    run_type, test_run, results_dir, test_checksums_file, _, _ = test_environment
    if run_type == 'oncoservice':
        test_run_results = results_dir / test_run.name
        test_checksums_file: Path = results_dir / f'{test_run.name}.sha256'
        golden_checksums_file: str = str(test_run) + '.sha256'
    elif run_type == 'cbmed':
        test_run_results = results_dir
        test_checksums_file: str = str(results_dir) + '.sha256'
        golden_checksums_file: str = str(test_run) + '.sha256'
    elif run_type == 'patho':
        pass
    else:
        pytest.fail(f"Unrecognosed run type: {run_type}")

    compute_checksums_call = (r'find '
                              f'{str(test_run_results)} '
                              r'-type f -exec sha256sum {} \; | tee  '
                              f'{str(test_checksums_file)}')
    try:
        subp_run(compute_checksums_call).check_returncode()
    except CalledProcessError as e:
        pytest.fail(f"Computing checksums for {run_type} test run results had failed with return a code {e.returncode}."
                    f" Error output: {e.stderr}")

    compare_checksums_call = (f'diff '
                              f'{str(test_checksums_file)} '
                              f'{golden_checksums_file}')
    try:
        subp_run(compare_checksums_call).check_returncode()
    except CalledProcessError as e:
        pytest.fail(f"Testing of {run_type} test run had failed with return a code {e.returncode}. Test checksums "
                    f"differ from golden truth! Error output: {e.stderr}")
