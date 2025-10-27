from pathlib import Path
sample_sheet = Path('/mnt/NovaseqXplus/07_Oncoservice/Runs/20250613_LH00803_0012_B232KMCLT3/SampleSheet_Analysis.csv')

if sample_sheet.exists():
    print('we are cooked')



