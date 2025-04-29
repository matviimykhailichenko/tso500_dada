from pathlib import Path
from subprocess import CalledProcessError
import yaml
import subprocess
import argparse
from filelock import FileLock
import pandas as pd
from scripts.helpers import is_server_available, get_server_ip, load_config, setup_paths, check_mountpoint, check_rsync, \
    check_structure, check_docker_image, check_tso500_script, stage_object, process_object, transfer_results
from scripts.logging_ops import notify_bot, setup_logger



def create_parser():
    parser = argparse.ArgumentParser(description='This is a crontab script process incoming runs')
    parser.add_argument('-t', '--testing',action='store_true', help='Testing mode')
    return parser

#
# def run_automation(run_type: str = 'None', testing: bool = False):
#     with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
#         config = yaml.safe_load(file)
#         pipeline_dir: Path = Path(config['pipeline_dir'])
#         onco_dir: Path = Path(config['oncoservice_dir'])
#         server_availability_dir: Path = Path(config['server_availability_dir'])
#         server_idle_tag: Path = server_availability_dir / config['server_idle_tag']
#         server_busy_tag: Path = server_availability_dir / config['server_busy_tag']
#         cbmed_seqencing_dir: Path = Path(config['cbmed_seqencing_dir'])
#         pending_tag: str = config['pending_run_tag']
#
#     if run_type == 'oncoservice':
#         pending_tag: Path = onco_dir / pending_tag
#         run_files_dir: Path = Path(pending_tag.read_text())
#
#     elif run_type == 'cbmed':
#         pending_tag: Path = cbmed_seqencing_dir / pending_tag
#         run_files_dir: Path = Path(pending_tag.read_text())
#
#     elif run_type == 'patho':
#         pending_tag: Path = cbmed_seqencing_dir / pending_tag
#         run_files_dir: Path = Path(pending_tag.read_text())
#     else:
#         if testing:
#             notify_bot(f"TESTING TSO500: Unrecognised run type: {run_type}")
#         raise RuntimeError(f"Unrecognised run type: {run_type}")
#
#     failed_tag: Path = run_files_dir / config['failed_tag']
#     analysed_tag: Path = run_files_dir / config['analysed_tag']
#     server_idle_tag.unlink()
#     snakefile_path = pipeline_dir / 'snakefile'
#     config_file_path = pipeline_dir / 'config.yaml'
#     server_busy_tag.touch()
#
#     snakemake_call =[
#             "conda", "run", "-n", "tso500_dragen_pipeline",
#             "snakemake", "-s", str(snakefile_path),
#             "--configfile", str(config_file_path),
#             "--config", f"run_files_dir={str(run_files_dir)}", f'run_type={run_type}', f'testing={str(testing)}'
#     ]
#     try:
#         subprocess.run(snakemake_call).check_returncode()
#     except CalledProcessError as e:
#         message = f"Error processing run {run_files_dir}: {e}"
#         if testing:
#             notify_bot(f"TESTING TSO500: Error processing run {run_files_dir}: {e}")
#         failed_tag.touch()
#         server_busy_tag.unlink()
#         server_idle_tag.touch()
#         pending_tag.unlink()
#         raise RuntimeError(message)
#
#     analysed_tag.touch()
#     server_busy_tag.unlink()
#     server_idle_tag.touch()
#     pending_tag.unlink()


# TODO add checking for patho dir
def check_pending_runs():
    with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        onco_dir = Path(config['oncoservice_dir'])
        cbmed_seqencing_dir = Path(config['cbmed_seqencing_dir'])
        pending_onco_tag = Path(onco_dir / config['pending_run_tag'])
        pending_cbmed_tag = Path(cbmed_seqencing_dir / config['pending_run_tag'])

    if pending_onco_tag.exists():
        print('Oncoservice run was detected')
        return 'oncoservice'
    elif pending_cbmed_tag.exists():
        print('CBmed run was detected')
        return 'cbmed'
    else:
        print('No Oncoservice or CBmed runs are detected, quitting...')
        return None



def main():
    args = create_parser().parse_args()
    testing: bool = args.testing

    with open('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        pipeline_dir: Path = Path(config['pipeline_dir'])

    # if not is_server_available():
    #     return

    server = get_server_ip()
    queue_file = pipeline_dir.parent.parent / f'{server}_QUEUE.txt'
    pending_file = pipeline_dir.parent.parent / f'{server}_PENDING.txt'
    pending_lock = Path(str(queue_file) + '.lock')

    # TODO if pending not empty

    if not pending_file.stat().st_size == 0:
        with FileLock(pending_lock):
            queue = pd.read_csv(pending_file, sep='\t')
            queue = queue.sort_values(by='Priority', ascending=True)
            queue_no_processing = queue.iloc[1:, ]

            for index, row in queue.iterrows():
                with open(queue_file, 'a') as f:
                    f.write('\t'.join(map(str, row)) + '\n')
                    queue_no_processing.to_csv(queue_file, sep='\t', index=False)

                open(str(pending_file), "w").close()

                pass


    path, input_type, _, tag, flowcell = queue.iloc[0]

    config = load_config('/mnt/Novaseq/TSO_pipeline/01_Staging/pure-python-refactor/config.yaml')

    paths: dict = setup_paths(input_path=Path(path),input_type=input_type,tag=tag,config=config)

    logger = setup_logger(logger_name='Logger',log_file=paths['log_file'])

    check_mountpoint(paths=paths, logger=logger)

    check_structure(paths=paths, logger=logger)

    check_docker_image(logger=logger)

    check_rsync(paths=paths, logger=logger)

    check_tso500_script(paths=paths, logger=logger)

    stage_object(paths=paths,input_type=input_type,logger=logger)

    # process_object(paths=paths, logger=logger)
    #
    # transfer_results(paths=paths, logger=logger)

    # TODO while stuff in queue process stuff, but check priority first

    # TODO sort queue
    # TODO process 1 sample/run with most proprity:
    # TODO stage
    # TODO run script
    # TODO transfer

if __name__ == "__main__":
    main()
