from pathlib import Path
import yaml
import argparse
from datetime import datetime
from subprocess import run as subp_run, CalledProcessError
from helpers import is_server_available, get_server_ip
from logging_ops import notify_bot
from shutil import copy as sh_copy, move as sh_move, rmtree as sh_rmtree



def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script process incoming runs')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    parser.add_argument('-tf', '--testing_fast',action='store_true', help='Fast testing mode')

    return parser


def main():
    args = create_parser().parse_args()
    testing: bool = args.testing

    with open('/mnt/NovaseqXplus/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])
        server_availability_dir: Path = Path(config['server_availability_dir'])
        server = get_server_ip()
        idle_tag = server_availability_dir / server / config['server_idle_tag']
        busy_tag = server_availability_dir / server / config['server_busy_tag']
        analyzed_tag = config['analyzed_tag']
        archiving_tag = config['archiving_tag']
        archived_tag = config['archived_tag']
        reanalysis_failed_tag = config['reanalysis_failed_tag']
        onco_results_dir = Path(config['oncoservice_sequencing_dir'] + '_TEST' if testing else config['oncoservice_sequencing_dir']) / 'Analyseergebnisse'
        onco_seq_dir = Path(config['oncoservice_sequencing_dir'] + '_TEST' if testing else config['oncoservice_sequencing_dir'] ) / 'Runs'
        mixed_runs_dir = Path(config['mixed_runs_dir'] + '_TEST' if testing else config['mixed_runs_dir'] ) / 'Runs'
        queue_file = pipeline_dir.parent.parent / f'{server}_QUEUE.txt'
        pending_file = pipeline_dir.parent.parent / f'{server}_PENDING.txt'
        archive_dir = Path(config['archive_dir'] + '_TEST') / str(datetime.now().year) / 'TSO500'
        reanalysis_dir = Path(config['reanalysis_dir'] + '_TEST' if testing else config['reanalysis_dir']) / 'TSO500'
        server = get_server_ip()
        if server == '10.200.214.104':
            reference = Path('/staging/illumina/DRAGEN_TSO500_2.6.1/resources/hg19_decoy/genome.fa')
        elif server == '10.200.215.35':
            reference = Path('/staging/illumina/DRAGEN_TruSight_Oncology_500_ctDNA/resources/hg19_decoy/genome.fa')
        reference_hash = Path(str(reference) + '.md5')

    if not is_server_available() or not queue_file.stat().st_size < 38 or not pending_file.stat().st_size < 38:
        return

    busy_tag.touch()
    idle_tag.unlink()

    try:
        caller_dir = None
        for run_dir in reanalysis_dir.iterdir():
            if (run_dir / 'ARCHIVED.txt').exists():
                caller_dir = run_dir / 'pipeline_output/Logs_Intermediates/DragenCaller'
                break
        if caller_dir is None:
            raise RuntimeError('No run to process')

        cmd = f'diff {reference_hash} {run_dir}/genome.fa.md5'
        try:
            subp_run(cmd, check=True, shell=True)
        except CalledProcessError as e:
            print(f"Hashes are different for archived and current reference: {e}")
            raise

        fastq_dir = run_dir / 'FastqGeneration'

        for sample_dir in caller_dir.iterdir():
            sample_id = sample_dir.name
            cram_file = next(sample_dir.glob('*.cram'))
            cmd = (
                f"docker run --rm -it -v /mnt/NovaseqXplus:/mnt/NovaseqXplus tso500_archiving "
                f"/opt/conda/envs/tso500_archiving/bin/samtools "
                f"fastq -@ 40 -N "
                f"-1 {str(fastq_dir)}/{sample_id}_S0_R1_001.fastq.gz -2 {str(fastq_dir)}/{sample_id}_S0_R1_001.fastq.gz "
                f"-0 {str(fastq_dir)}/unpaired.fastq.gz -s {str(fastq_dir)}/unpaired.fastq.gz -n "
                f"-t -F 0x900 -f 0x1 -O -o /dev/null {cram_file} "
                f"-T {reference}"
            )
            try:
                subp_run(cmd, check=True, shell=True)
            except CalledProcessError as e:
                print(f"FASTQ conversion failed: {e}")
                raise

        # TODO add check for 06_Reanalyse dir to scheduler
        # TODO add special behaviour for processing


    except Exception:
        if caller_dir.exists():
            (run_dir / reanalysis_failed_tag).touch()
        raise RuntimeError
    finally:
        idle_tag.touch()
        busy_tag.unlink()


if __name__ == "__main__":
    main()
