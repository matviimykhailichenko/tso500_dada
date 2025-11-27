from subprocess import run


diff_call = (
        f'diff <(sort {'/mnt/CBmed_NAS3/Genomics/TSO500_liquid/dragen_TEST/20251127_BI_733_b01_s01/250213_A01664_0452_AH2J5VDMX2.sha256'}) <(sort {'/mnt/CBmed_NAS3/Genomics/TSO500_liquid/dragen_TEST/20251127_BI_733_b01_s01/250213_A01664_0452_AH2J5VDMX2_Results_HumGenNAS.sha256'})'
    )
try:
    stdout = run(diff_call, shell=True, capture_output=True,text=True, check=True, executable='/bin/bash').stdout.strip()
    if stdout is not None:
        msg = f"Checksums in a CBmed run are different"
        print(msg)
        # raise RuntimeError(msg)