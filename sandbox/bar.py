from subprocess import run

f1 = "/mnt/CBmed_NAS3/Genomics/TSO500_liquid/dragen_TEST/20251127_BI_733_b01_s01/250213_A01664_0452_AH2J5VDMX2.sha256"
f2 = "/mnt/CBmed_NAS3/Genomics/TSO500_liquid/dragen_TEST/20251127_BI_733_b01_s01/250213_A01664_0452_AH2J5VDMX2_Results_HumGenNAS.sha256"

diff_call = f"diff <(sort '{f1}') <(sort '{f2}')"

result = run(diff_call, shell=True, capture_output=True, text=True,
             executable="/bin/bash")

stdout = result.stdout.strip()

if stdout:
    print(f"Checksums differ:\n{stdout}")
