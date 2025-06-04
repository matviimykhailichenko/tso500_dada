import subprocess


file1_checksum = '/Users/matviimykhailichenko/Documents/tso500_dragen_pipeline/sandbox/compare_checksums/dir/1.sha256'
file2_checksum = '/Users/matviimykhailichenko/Documents/tso500_dragen_pipeline/sandbox/compare_checksums/dir/2.sha256'

compare_checksum_call = f'sha256sum {file1_checksum} {file2_checksum}'

subprocess.run(compare_checksum_call, shell=True, check=True)
