from pathlib import Path
import yaml
import argparse
from datetime import datetime
from subprocess import run as subp_run, CalledProcessError
from helpers import is_server_available, get_server_ip
from logging_ops import notify_bot



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
        onco_results_dir = Path(config['oncoservice_sequencing_dir'] + '_TEST' if testing else '') / 'Analyseergebnisse'
        queue_file = pipeline_dir.parent.parent / f'{server}_QUEUE.txt'
        pending_file = pipeline_dir.parent.parent / f'{server}_PENDING.txt'
        reference_version = 'hg19'
        reference = next(Path('/staging/references').rglob(f"{reference_version}.fna"))
        archive_dir = Path(config['archive_dir'] + '_TEST') / str(datetime.now().year) / 'TSO500'

    if not is_server_available() or not queue_file.stat().st_size < 38 or not pending_file.stat().st_size < 38:
        return

    busy_tag.touch()
    idle_tag.unlink()

    try:
        bam_files = []
        run_name = None
        for results_dir in onco_results_dir.iterdir():
            run_name = results_dir
            if not (results_dir / analyzed_tag).exists():
                continue
            bam_files = [
                f for f in (results_dir / 'Logs_Intermediates/DragenCaller').rglob("*.bam")
                if not f.name.startswith("evidence")
            ]
            break

        if not bam_files or not run_name:
            return

        archive_dir = archive_dir / run_name
        archive_dir.mkdir(exist_ok=True)

        for bam_file in bam_files:

            cram_file = archive_dir / bam_file.with_suffix('.cram').name
            cmd = (f"docker run -it tso500_archiving "
                  f"-v /mnt/NovaseqXplus:/mnt/NovaseqXplus -v /staging:/staging "
                  f"samtools view -@ 40 -T {reference} -C -o {cram_file} {bam_file}")
            try:
                subp_run(cmd, check=True, shell=True)
            except CalledProcessError as e:
                err = e.stderr.decode() if e.stderr else str(e)
                msg = f"CRAM onversion had failed: {err}"
                notify_bot(msg)
                raise RuntimeError(msg)

        (results_dir / archived_tag).touch()
        (results_dir / archiving_tag).unlink()

    except Exception:
        if (results_dir / archiving_tag).exists():
            (results_dir / archiving_tag).unlink()
        (results_dir / archiving_failed_tag).touch()
        raise RuntimeError
    finally:
        idle_tag.touch()
        busy_tag.unlink()


if __name__ == "__main__":
    main()
