from pathlib import Path
import yaml

flowcell = "test_run_files_dir"
testing = True
run_name = "test_results_dir"

with open('/mnt/Novaseq/TSO_pipeline/02_Development/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    cbmed_results_dir = Path(f"{config['cbmed_results_dir']}{'_TEST' if testing else ''}")
    staging_dir_path = Path(config['staging_dir'])
data_staging_dir_path = staging_dir_path / flowcell
data_cbmed_dir_path = cbmed_results_dir / 'flowcells' / flowcell
results_staging_dir_path = staging_dir_path / run_name
results_cbmed_dir_path = cbmed_results_dir / 'dragen' / flowcell / 'Results'
print(data_cbmed_dir_path, results_cbmed_dir_path)

data_cbmed_dir_path.mkdir(parents=True, exist_ok=True)
results_cbmed_dir_path.mkdir(parents=True, exist_ok=True)