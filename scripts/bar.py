sample_ids = ['Sample_1-CBM', 'Sample_1-CBM']
tags = [s.split("-", 1)[1].split("_", 1)[0] for s in sample_ids]
print(tags)