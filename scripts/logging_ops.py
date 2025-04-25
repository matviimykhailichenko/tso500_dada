from discord import SyncWebhook
import logging
import os


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

