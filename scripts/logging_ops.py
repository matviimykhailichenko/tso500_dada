from discord import SyncWebhook
import logging
from logging import Logger


# TODO move the Webhook URL to config file
def notify_bot(msg: str,
               url: str ='https://discord.com/api/webhooks/1334878015078793310/qENtDsst4aV31baSn9BJ8cf4mEhk75QTpC_rRF5HZ5V5Q_gKzHivFcs9IS5rTHNUVjLL'):
    if len(msg) > 2000:
        msg = f"{msg[:1993]} [...]"

    webhook = SyncWebhook.from_url(url)
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


def notify_pipeline_status(paths, step:str,run_name:str,logger:Logger,input_type:str,tag:str ="",last_sample_queue:bool=False):
    prefix = f"the last {tag} sample in" if input_type == "sample" and last_sample_queue else ""

    if step == "staging":
        msg = f"Staging {prefix} the run {run_name}"

    elif step == "running":
        msg = f"Running the TSO500 script for {prefix} the run {run_name}"

    elif step == "running" and paths['tag'] == 'RNA':
        msg = f'Demuxing the run {run_name}'

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

