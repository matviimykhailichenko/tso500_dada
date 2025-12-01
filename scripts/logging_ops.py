from discord import SyncWebhook
import logging
from logging import Logger
from pathlib import Path
import yaml



def notify_bot(msg: str, testing:bool = False):
    from helpers import get_repo_root

    if testing:
        print(msg)
        return

    config_path = Path(get_repo_root()) / 'config.yaml'
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    if len(msg) > 2000:
        msg = f"{msg[:1993]} [...]"

    webhook = SyncWebhook.from_url(config['bot_webhook'])
    webhook.send(content=msg)


def setup_logger(logger_name: str,
                 log_file: str):
    logger = logging.getLogger(logger_name)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


def notify_pipeline_status(step:str,run_name:str,logger:Logger,input_type:str,tag:str ="",last_sample_queue:bool=False):
    prefix = f"the last {tag} sample in" if input_type == "sample" and last_sample_queue else ""

    if step == "staging":
        msg = f"Staging {prefix} the run {run_name}"

    elif step == "running":
        msg = f"Running the TSO500 script for {prefix} the run {run_name}"

    elif step == "running_ichorCNA":
        msg = f"Running the ichorCNA docker for {prefix} the run {run_name}"

    elif step == "transferring":
        msg = f"Transferring the results for {prefix} the run {run_name}"

    elif step == 'finished':
        msg = f"Finished processing {prefix} the run {run_name}"

    else:
        raise RuntimeError(f'Unknown step:{step}')

    if (input_type == 'sample' and last_sample_queue) or input_type == 'run':
        notify_bot(msg)
    logger.info(msg)

