from pathlib import Path
import yaml

paths = {}
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

paths['pipeline_dir'] = Path(config['pipeline_dir'])
paths['resources_dir'] = paths['pipeline_dir'] / 'resources'
paths['ichorCNA_repo'] = paths['resources_dir'] / 'ichorCNA'
print(paths['ichorCNA_repo'])