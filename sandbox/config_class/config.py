import yaml
from pathlib import Path



def parse_config:
    # TODO for loop and




class Config:
    def __init__(self, config_file_path: Path):
        with open(config_file_path, 'r') as config_file:
            config = yaml.safe_load(config_file)
