import subprocess

from scripts.logging_ops import notify_bot



def main():
    try:
        dragen_call = ['DRAGEN_TruSight_Oncology_500_ctDNA.sh', '--runFolder', str('/staging/250224_TSO'),
                                '--analysisFolder', str('/staging/250224_TSO_Results')]
        subprocess.run(dragen_call)
    except SystemError as e:
        notify_bot(msg=f'Script called system error: {e}')



if __name__=="__main__":
    main()
