from shutil import which as sh_which

rsync_path = sh_which('rsync')
if rsync_path is None:
    raise FileNotFoundError
print('Rsync was foynd')

rsync_path = sh_which('rsynk')

if rsync_path is None:
    raise FileNotFoundError

print("Rsunk wasn't found")