from helpers import validate_samplesheet, get_repo_root
from pathlib import Path
import yaml


repo_root = get_repo_root()

with open(f'{repo_root}/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    pipeline_dir: Path = Path(config['pipeline_dir'])

validate_samplesheet(repo_root=Path('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor'),
                     input_type='samples',
                     config = config,
                     sample_sheet = Path('/mnt/NovaseqXplus/10_MixedRuns/20250827_LH00803_0022_A235MT5LT3/SampleSheet_Analysis.csv'))