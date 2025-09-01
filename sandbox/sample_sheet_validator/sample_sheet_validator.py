import re
import yaml
from pathlib import Path
import pandas as pd
from io import StringIO



def main():


    with open('/home/matvii/PycharmProjects/TSO_500_DRAGEN_pipeline/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        ready_tags = config['ready_tags']
        blocking_tags = config['blocking_tags_validator']
    seq_dirs = [Path(config['oncoservice_sequencing_dir']), Path(config['cbmed_sequencing_dir']),
                Path(config['mixed_runs_dir']), Path(config['patho_sequencing_dir'])]
    # TODO change in prod!
    expected_indexes = 'expected_indexes_updated.csv'
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

    input_type = 'run'

    # TODO sandboxing the script, delete after putting to prod
    sample_sheet = ('SampleSheet2.csv')

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

    if input_type == 'samples':
        expected_headers = [
        "[Header],\n",
        "[Reads]\n",
        "[Sequencing_Settings]\n",
        "[BCLConvert_Settings]\n",
        "[TSO500L_Settings]\n",
        "[TSO500L_Data]\n"
        ]

        # Run name is variable
        expected_header_section = [
            "FileFormatVersion,2\n",
            "InstrumentPlatform,NovaSeqXSeries\n",
            "IndexOrientation,Forward\n",
            "\n"
        ]

        expected_read_section = [
            "Read1Cycles,151\n",
            "Read2Cycles,151\n",
            "Index1Cycles,10\n",
            "Index2Cycles,10\n",
            "\n"
        ]

        expected_seq_settings_section = [
            'LibraryPrepKits,TSO500ctDNA_v2\n',
            "\n"
        ]

        expected_bcl_settings_section = [
            "SoftwareVersion,2.1.1\n",
            "AdapterRead1,CTGTCTCTTATACACATCT\n",
            "AdapterRead2,CTGTCTCTTATACACATCT\n",
            "OverrideCycles,U7N1Y143;I10;I10;U7N1Y143\n",
            "MaskShortReads,35\n",
            "AdapterBehavior,trim\n",
            "MinimumTrimmedReadLength,35\n",
            "FastqCompressionFormat,gzip\n",
            "\n"
        ]

        expected_tso500_settings_section = [
            'SoftwareVersion,2.1.1\n',
            'StartsFromFastq,false\n',
            "\n"
        ]

        expected_sections = {
            "[Header],\n": expected_header_section,
            "[Reads]\n": expected_read_section,
            "[Sequencing_Settings]\n": expected_seq_settings_section,
            "[BCLConvert_Settings]\n": expected_bcl_settings_section,
            "[TSO500L_Settings]\n": expected_tso500_settings_section
        }

    elif input_type == 'run':
        expected_headers = [
            "[Header],,,,\n",
            "[Reads],,,,\n",
            "[Sequencing_Settings],,,,\n",
            "[BCLConvert_Settings],,,,\n",
            "[BCLConvert_Data],,,,\n",
            "[TSO500L_Settings],,,,\n",
            "[TSO500L_Data],,,,\n"
        ]

        expected_header_section = [
            "FileFormatVersion,2,,,\n",
            "InstrumentPlatform,NovaSeq,,,\n",
            "IndexOrientation,Forward,,,\n",
        ]

        expected_read_section = [
            "Read1Cycles,151,,,\n",
            "Read2Cycles,151,,,\n",
            "Index1Cycles,10,,,\n",
            "Index2Cycles,10,,,\n",
        ]

        expected_seq_settings_section = [
            "LibraryPrepKits,TSO500ctDNA_v2,,,\n",
        ]

        expected_bcl_settings_section = [
            "SoftwareVersion,02.01.2001,,,\n",
            "AdapterRead1,CTGTCTCTTATACACATCT,,,\n",
            "AdapterRead2,CTGTCTCTTATACACATCT,,,\n",
            "MaskShortReads,35,,,\n",
            "OverrideCycles,U7N1Y143,I10,I10,U7N1Y143\n",
            "AdapterBehavior,trim,,,\n",
            "MinimumTrimmedReadLength,35,,,\n",
        ]

        expected_tso500_settings_section = [
            "SoftwareVersion,02.01.2001,,,\n",
            "StartsFromFastq,0,,,\n",
        ]

        expected_sections = {
            "[Header],,,,\n": expected_header_section,
            "[Reads],,,,\n": expected_read_section,
            "[Sequencing_Settings],,,,\n": expected_seq_settings_section,
            "[BCLConvert_Settings],,,,\n": expected_bcl_settings_section,
            "[TSO500L_Settings],,,,\n": expected_tso500_settings_section
        }

    else:
        raise RuntimeError('Unexpected input type')



    #
    # print(list(sections_dict.keys()))
    # print(expected_headers)
    extra = set(sections_dict.keys()) - set(expected_headers)
    missing = set(expected_headers) - set(sections_dict.keys())
    assert not extra and not missing, (
        f"ERROR: Headers of sections are not as expected.\n"
        f"Extra: {extra}\n"
        f"Missing: {missing}")

    # df_expected_indexes = pd.read_csv(expected_indexes)
    df_expected_indexes = (pd.read_csv(expected_indexes, usecols=lambda col: col not in ["Index2nsqx" if input_type == "run" else "Index2nsq6000"])
                           .rename(columns={"Index2nsq6000" if input_type == "run" else "Index2nsqx": "Index2"}))

    indexes = sections_dict.pop(f"[TSO500L_Data]{",,,," if input_type == 'run' else ''}\n")

    sections_dict[f'[Header]{",,,," if input_type == 'run' else ','}\n'] = [
        e for e in sections_dict.get(f'[Header]{",,,," if input_type == 'run' else ','}\n', [])
        if not e.startswith("RunName")
    ]

    if input_type == "run":
        bcl_convert = sections_dict.pop(f"[BCLConvert_Data],,,,\n")

    for section_header in sections_dict:
        extra = set(sections_dict.get(section_header)) - set(expected_sections.get(section_header))
        missing = set(expected_sections.get(section_header)) - set(sections_dict.get(section_header))
        assert not extra and not missing, (
                f"ERROR: Section {section_header}  not as expected.\n"
                f"Extra: {extra}\n"
                f"Missing: {missing}")


    csv_string = "".join(indexes)

    df_indexes_no_sample_ids = pd.read_csv(StringIO(csv_string)).drop(columns=['Sample_ID'])
    df_sample_ids = pd.read_csv(StringIO(csv_string))['Sample_ID']
    df_indexes_no_sample_ids.to_csv('sample_sheet_indexes',index=False)

    for sample_id in df_sample_ids:
        assert re.fullmatch(r"[A-Za-z0-9_-]+", sample_id), f"Invalid ID: {sample_id}"

    for row in df_indexes_no_sample_ids.itertuples(index=False, name=None):
        assert row in set(df_expected_indexes.itertuples(index=False, name=None)), \
            f"Row {row} not found in expected dataframe"

    if input_type == 'run':
        rename_dict = {"index": "Index", "index2": "Index2"}
        df_indexes_for_bclconvert = (pd.read_csv(StringIO(csv_string))
                                     .drop(columns=['Sample_Type','Index_ID'])
                                     .rename(columns=rename_dict))

        df_bclconvert = pd.read_csv(StringIO("".join(bcl_convert))).dropna(axis=1)

        for row in df_bclconvert.itertuples(index=False, name=None):
            assert row in set(df_indexes_for_bclconvert.itertuples(index=False, name=None)), \
                f"Row {row} not found in expected dataframe"

    print('Samplesheet is valid')


if __name__ == '__main__':
    main()
