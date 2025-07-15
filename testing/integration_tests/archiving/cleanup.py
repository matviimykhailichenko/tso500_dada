from pathlib import Path



for sample_dir in Path('/mnt/NovaseqXplus/07_Oncoservice_TEST/Analyseergebnisse/250710_TSO500_Onco/Logs_Intermediates/DragenCaller').iterdir():
    sample_dir.glob('*.cram').unlink()