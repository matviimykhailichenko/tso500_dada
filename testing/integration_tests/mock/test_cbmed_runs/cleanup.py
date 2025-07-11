import shutil

def sh_rmtree(path):
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass

sh_rmtree('/mnt/CBmed_NAS3/Genomics/TSO500_liquid_TEST/test_run_cbmed_2')
sh_rmtree('/mnt/CBmed_NAS3/Genomics/TSO500_liquid_TEST/test_run_cbmed_1')
sh_rmtree('/mnt/CBmed_NAS3/Genomics/TSO500_liquid_TEST/flowcells/250213_A01664_0452_AH2J5VDMX2')
sh_rmtree('/mnt/CBmed_NAS3/Genomics/TSO500_liquid_TEST/dragen/250213_A01664_0452_AH2J5VDMX2')

