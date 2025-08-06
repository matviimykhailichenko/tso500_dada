import yaml
from pathlib import Path
import re



def main():
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        ready_tags = config['ready_tags']
        blocking_tags = config['blocking_tags_validator']
    seq_dirs = [Path(config['oncoservice_sequencing_dir']), Path(config['cbmed_sequencing_dir']),
                Path(config['mixed_runs_dir']), Path(config['patho_sequencing_dir'])]
    sample_sheet = None

    for seq_dir in seq_dirs:
        for run_dir in seq_dir.iterdir():
            flowcell_dir = None
            for obj in run_dir.iterdir():
                if obj.is_dir() and re.search(r'^\d{6}_A01664_\d{4}_[A-Z0-9]{10}$', obj.name):
                    flowcell_dir = obj
            if not flowcell_dir:
                continue

            txt_files = list(Path(flowcell_dir).glob('*.txt'))
            file_names = [path.name for path in txt_files]
            if any(f in blocking_tags for f in file_names):
                continue
            if not all(tag in file_names for tag in ready_tags):
                continue

            sample_sheet = flowcell_dir / 'SampleSheet.csv'

    if sample_sheet is None:
        return

    with open(sample_sheet, 'r') as f:
        lines = f.readlines()
        section_header = None
        sections_dict = {}
        current_sections = []
        for line in lines:
            if line.startswith('['):
                if current_sections is not []:
                    sections_dict[section_header] = current_sections
                    current_sections = []
                section_header = section_header = re.sub(r'[\[\],]', '', line)
            elif line.startswith(','):
                continue
            else:
                current_sections.append(line)




if __name__ == '__main__':
    main()
# TODO parse section
# TODO
# TODO
# TODO