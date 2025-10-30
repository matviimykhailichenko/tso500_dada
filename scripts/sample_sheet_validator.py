from helpers import validate_samplesheet, get_repo_root
import yaml
from pathlib import Path
from logging_ops import notify_bot
from shutil import move as sh_move



def main():
    repo_root = get_repo_root()
    with open(f'{repo_root}/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir = Path(config['pipeline_dir'])
        validator_dir = pipeline_dir / 'sample_sheet_validator'
        samplesheet_ns6000 = validator_dir / 'SampleSheet.csv'
        samplesheet_nsx = validator_dir / 'SampleSheet_Analysis.csv'
        sample_sheet_valid_tag = validator_dir / config['sample_sheet_valid_tag']

    if samplesheet_nsx.exists():
        input_type = 'sample'
        sample_sheet = samplesheet_nsx

    elif samplesheet_ns6000.exists():
        input_type = 'run'
        sample_sheet = samplesheet_ns6000

    else:
        return

    ok, reason = validate_samplesheet(repo_root=repo_root, input_type=input_type, config=config, sample_sheet=sample_sheet)
    sample_sheet_name = sample_sheet.name.split('.')[0]

    if not ok:
        sample_sheet_broken = sample_sheet.parent / f'{sample_sheet_name}_BROKEN_{reason}.csv'
        message = (f'Samplesheet validation had failed:\n'
                   f'{reason}')
        notify_bot(message)
        sh_move(sample_sheet, sample_sheet_broken)
        raise RuntimeError(message)

    sample_sheet_valid_tag.touch()

    print(reason)

if __name__ == '__main__':
    main()