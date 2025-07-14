from pathlib import Path
from ..helpers import merge_metrics



paths = {}
paths['results_dir'] = (Path('/mnt/NovaseqXplus/07_Oncoservice/Analyseergebnisse/250710_TSO500_Onco'))
print(merge_metrics(paths=paths))