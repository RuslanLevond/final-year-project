# Bulk Download Guide - https://gist.github.com/rhine3/4829bf66381c7aa05c1f656cec4fa040
# API URL - https://xeno-canto.org/api/2/recordings?query=araripe%manakin

# Usage
# 1. wget -O noca-query.json <url>
# 2. python3 download.py
# 3. wget -P ./clips --trust-server-names -i xc-noca-urls.txt
# 4. python3 mp3_to_wav_converter.py

import json
import pandas as pd

# Get the json entries from your downloaded json
jsonFile = open('noca-query.json', 'r')
values = json.load(jsonFile)
jsonFile.close()

# Create a pandas dataframe of records & convert to .csv file
record_df = pd.DataFrame(values['recordings'])
record_df.to_csv('xc-noca.csv', index=False)

# Make wget input file
url_list = []
for file in record_df['file'].tolist():
    url_list.append(file)
with open('xc-noca-urls.txt', 'w+') as f:
    for item in url_list:
        f.write("{}\n".format(item))
