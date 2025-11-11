from crontab import CronTab

def enable_testing_mode(server_ip):
    last_part = server_ip.split('.')[-1]
    crontab_testing = f'/mnt/NovaseqXplus/TSO_pipeline/03_Production/tso500_dragen_pipeline/files/crontabs/crontab_{last_part}_testing'
    cron = CronTab(tabfile=crontab_testing)
    cron.write_to_user(user=True)

def disable_testing_mode(server_ip, repo_root):
    last_part = server_ip.split('.')[-1]
    crontab_production = f'{repo_root}/files/crontabs/crontab_{last_part}'
    cron = CronTab(tabfile=crontab_production)
    cron.write_to_user(user=True)
