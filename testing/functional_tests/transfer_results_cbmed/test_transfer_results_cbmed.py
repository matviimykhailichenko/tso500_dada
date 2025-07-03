from scripts.helpers import transfer_results_cbmed, setup_paths
from scripts.logging_ops import setup_logger
import pytest
from pathlib import Path
from shutil import copytree as sh_copytree, copy as sh_copy, move as sh_move
from subprocess import run as subp_run
import yaml



@pytest.fixture()
def setup_environment(request):
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        cbmed_seq_dir: Path = Path(config['cbmed_sequencing_dir'] + '_TEST')
        flowcell_name = '250123_A01664_0443_AH2J5YDMX2'
        test_cbmed_samples: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/testing/integration_tests/mock/test_run_onco_nsqx')
    test_cbmed_run_seq_dir = cbmed_seq_dir / flowcell_name
    test_results =
    test_results_staging = Path('/staging/tmp/test_results')
    pending_blank: Path = Path('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/scheduler/PENDING_blank.txt')
    pending_file: Path = Path('/mnt/NovaseqXplus/TSO_pipeline/10.200.215.35_PENDING.txt')

    sh_copy(str(pending_blank), str(pending_file))
    if not test_cbmed_run_seq_dir.exists():
        sh_copytree(str(test_cbmed_samples),str(test_cbmed_run_seq_dir))
    if not test_results.exists():
        sh_copytree(str(test_cbmed_samples), str(test_cbmed_run_seq_dir))


@pytest.mark.dependency(depends=["scheduling"])
def test_transfer_results_cbmed():
    flowcell_name = '250123_A01664_0443_AH2J5YDMX2'
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    paths = setup_paths(input_path=f'/mnt/CBmed_NAS3/Genomics/TSO500_liquid_TEST/{flowcell_name}',
                        input_type='samples',
                        tag='CBM',
                        flowcell=flowcell_name,
                        config=config)
    logger_runtime = setup_logger('transfer_results_cbmed',
                                  '/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/testing/functional_tests/transfer_results_cbmed/last_execution.log')
    transfer_results_cbmed(paths=paths,
                           flowcell='test_run_files_dir',
                           input_type='samples',
                           logger=logger_runtime,
                           testing=True)
