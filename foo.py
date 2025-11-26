import re

m = re.fullmatch(r'\d{6}_A01664_\d{4}_[A-Z0-9]{10}', '250123_A01664_0443_AH2J5YDMX2')

if m:
    print(m.group())     # the actual matched string
else:
    print("No match")
