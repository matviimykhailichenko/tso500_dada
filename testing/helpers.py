from crontab import CronTab

def enable_testing_mode(server_ip):
    last_part = server_ip.split('.')[-1]
    tabfile = f'/mnt/NovaseqXplus/TSO_pipeline/03_Production/tso500_dragen_pipeline/files/crontabs/crontab_{last_part}_testing'
    cron = CronTab(tabfile=tabfile)
    cron.write_to_user(user=True)  # <--- this activates it for the current user

def disable_testing_mode(server_ip, repo_root):
    last_part = server_ip.split('.')[-1]
    tabfile = f'{repo_root}/files/crontabs/crontab_{last_part}'
    cron = CronTab(tabfile=tabfile)
    cron.write_to_user(user=True)  # <--- restores normal crontab
