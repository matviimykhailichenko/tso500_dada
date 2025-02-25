import subprocess
from scripts.logging_ops import notify_bot, setup_logger
from datetime import datetime



def main():
    logger = setup_logger(rule_name='check_structure')
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'/staging/dragen_output_{timestamp}.log'

        dragen_call = ['DRAGEN_TruSight_Oncology_500_ctDNA.sh',
                       '--runFolder', str('/staging/250224_TSO'),
                       '--analysisFolder', str('/staging/250224_TSO_Results')]

        with open(output_file, 'w') as f:
            subprocess.run(dragen_call, stdout=f, stderr=subprocess.STDOUT)
    except Exception as e:
        notify_bot(msg=f'Script called system error: {e}')



if __name__=="__main__":
    main()
