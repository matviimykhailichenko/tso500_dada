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
        archiving_failed_tag = config['archiving_failed_tag']
        onco_results_dir = Path(config['oncoservice_sequencing_dir'] + '_TEST' if testing else config['oncoservice_sequencing_dir']) / 'Analyseergebnisse'
        onco_seq_dir = Path(config['oncoservice_sequencing_dir'] + '_TEST' if testing else config['oncoservice_sequencing_dir'] ) / 'Runs'
        mixed_runs_dir = Path(config['mixed_runs_dir'] + '_TEST' if testing else config['mixed_runs_dir'] ) / 'Runs'
        queue_file = pipeline_dir.parent.parent / f'{server}_QUEUE.txt'
        pending_file = pipeline_dir.parent.parent / f'{server}_PENDING.txt'
        archive_dir = Path(config['archive_dir'] + '_TEST') / str(datetime.now().year) / 'TSO500'
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
        bam_files = []
        cram_files = []
        run_name = None
        for results_dir in onco_results_dir.iterdir():
            run_name: str = results_dir.name
            if not (results_dir / analyzed_tag).exists() or (results_dir / archiving_failed_tag).exists():
                continue
            bam_files = [
                f for f in (results_dir / 'Logs_Intermediates/DragenCaller').rglob("*.bam")
                if not f.name.startswith("evidence")
            ]
            break

        if not bam_files or not run_name:
            return

        run_archive = archive_dir / run_name
        run_archive.mkdir(exist_ok=True, parents=True)

        (results_dir / archiving_tag).touch()
        (results_dir / analyzed_tag).unlink()

        reference_path = run_archive / 'reference_path.txt'
        with open(reference_path, 'w') as f:
            f.write(str(reference))

        reference_hash_archive = run_archive / reference_hash.name
        sh_copy(reference_hash, reference_hash_archive)

        for bam_file in bam_files:
            cram_file = run_archive / bam_file.with_suffix('.cram').name
            cram_files.append(cram_file)
            cmd = (f"docker run --rm -it -v /mnt/NovaseqXplus:/mnt/NovaseqXplus -v /staging:/staging tso500_archiving "
                  f"/opt/conda/envs/tso500_archiving/bin/samtools view -@ 40 -T {reference} -C -o {cram_file} {bam_file}")
            try:
                subp_run(cmd, check=True, shell=True)
            except CalledProcessError as e:
                err = e.stderr.decode() if e.stderr else str(e)
                msg = f"CRAM conversion had failed: {err}"
                notify_bot(msg)
                raise RuntimeError(msg)

            cmd = f'samtools index {cram_file}'
            try:
                subp_run(cmd, check=True, shell=True)
            except CalledProcessError as e:
                err = e.stderr.decode() if e.stderr else str(e)
                msg = f"CRAM indexing had failed: {err}"
                notify_bot(msg)
                raise RuntimeError(msg)

        expected_cram_files = []
        [expected_cram_files.append(f.with_suffix('.cram')) for f in bam_files]
        for f in expected_cram_files:
            assert f.exists() and f.stat().st_size > 1, f"{f} does not exist or is too small"

        for bam_file in bam_files:
            bam_file.unlink()

        (results_dir / archived_tag).touch()
        (results_dir / archiving_tag).unlink()

        run_prefix = run_name.split("_")[0]
        try:
            run_seq_dir = next(onco_seq_dir.glob(f'*{run_prefix}*'))
        except StopIteration:
            run_seq_dir = next(mixed_runs_dir.glob(f'*{run_prefix}*'))

        fastq_gen_dir = run_seq_dir / 'FastqGeneration'
        data_dir = run_seq_dir / 'Data'

        sh_rmtree(fastq_gen_dir)
        sh_rmtree(data_dir)

        sh_move(run_seq_dir, run_archive / 'run_files')
        sh_move(results_dir, run_archive / 'pipeline_output')

        (run_archive / archived_tag).touch()

    except Exception:
        if (results_dir / archiving_tag).exists():
            (results_dir / archiving_tag).unlink()
        if results_dir.exists():
            (results_dir / archiving_failed_tag).touch()
        raise RuntimeError
    finally:
        idle_tag.touch()
        busy_tag.unlink()


if __name__ == "__main__":
    main()
