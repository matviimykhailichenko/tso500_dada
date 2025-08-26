import yaml
from pathlib import Path
import re
import pandas as pd



def main():
    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        ready_tags = config['ready_tags']
        blocking_tags = config['blocking_tags_validator']
    seq_dirs = [Path(config['oncoservice_sequencing_dir']), Path(config['cbmed_sequencing_dir']),
                Path(config['mixed_runs_dir']), Path(config['patho_sequencing_dir'])]
    # TOTO change in prod!
    expected_indexes = 'expected_indexes.csv'
    sample_sheet = None

    # for seq_dir in seq_dirs:
    #     for run_dir in seq_dir.iterdir():
    #         flowcell_dir = None
    #         for obj in run_dir.iterdir():
    #             if obj.is_dir() and re.search(r'^\d{6}_A01664_\d{4}_[A-Z0-9]{10}$', obj.name):
    #                 flowcell_dir = obj
    #         if not flowcell_dir:
    #             continue
    #
    #         txt_files = list(Path(flowcell_dir).glob('*.txt'))
    #         file_names = [path.name for path in txt_files]
    #         if any(f in blocking_tags for f in file_names):
    #             continue
    #         if not all(tag in file_names for tag in ready_tags):
    #             continue
    #
    #         sample_sheet = flowcell_dir / 'SampleSheet.csv'

    # TODO sandboxing the script, delete after putting to prod
    sample_sheet = 'SampleSheet250620_BI_739_batch1.csv'

    if sample_sheet is None:
        return

    with open(sample_sheet, 'r') as f:
        lines = f.readlines()
        section_header = None
        sections_dict = {}
        current_sections = []
        for line in lines:
            if line.startswith('['):
                if current_sections:
                    sections_dict[section_header] = current_sections
                    current_sections = []
                section_header = line
            elif line.startswith(','):
                continue
            else:
                current_sections.append(line)

    sections_dict[section_header] = current_sections

    # parced_sample_sheet = 'SampleSheet_parced.csv'
    # with open(parced_sample_sheet, 'w') as f:
    #     f.write(str(sections_dict))
    expected_headers = [
        "[Header],,,,\n",
        "[Reads],,,,\n",
        "[Sequencing_Settings],,,,\n",
        "[BCLConvert_Settings],,,,\n",
        "[BCLConvert_Data],,,,\n",
        "[TSO500L_Settings],,,,\n",
        "[TSO500L_Data],,,,\n",
    ]

    assert list(sections_dict.keys()) == expected_headers

    df_expected_indexes = pd.read_csv(expected_indexes)

    indexes = sections_dict.get('[TSO500L_Data],,,,\n')
    csv_string = "".join(indexes)
    from io import StringIO
    df_indexes = pd.read_csv(StringIO(csv_string)).drop(columns=['Sample_ID'])
    print(df_indexes)
    print(df_expected_indexes)

    df_indexes.to_csv('sample_sheet_indexes',index=False)

    assert (df_indexes.merge(df_expected_indexes.drop_duplicates()).shape[0]  == df_indexes.shape[0])


if __name__ == '__main__':
    main()
