from crontab import CronTab

def enable_testing_mode(server_ip):
    last_part = '.'.join(server_ip.split('.')[3:])
    cron = CronTab(user=True, tabfile=f'/mnt/NovaseqXplus/TSO_pipeline/03_Production/tso500_dragen_pipeline/files/crontabs/crontab_{last_part}_testing')
    cron.write()

def disable_testing_mode(server_ip, repo_root):
    last_part = '.'.join(server_ip.split('.')[3:])
    cron = CronTab(user=True, tabfile=f'{repo_root}/files/crontabs/crontab_{last_part}')
    cron.write()

