from pathlib import Path



base_dir = Path('/mnt/NovaseqXplus/07_Oncoservice_TEST/Analyseergebnisse/250710_TSO500_Onco')

if (base_dir / 'ARCHIVED.txt').exists():
    (base_dir / 'ARCHIVED.txt').unlink()

if not (base_dir / 'ANALYZED.txt').exists():
    (base_dir / 'ANALYZED.txt').touch()

if (base_dir / 'ARCHIVING_FAILED.txt').exists():
    (base_dir / 'ARCHIVING_FAILED.txt').unlink()