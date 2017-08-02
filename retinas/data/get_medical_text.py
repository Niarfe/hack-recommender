#!/usr/bin/env python

source_name = 'medical_docs.csv'
target_name = 'medical_docs_content.txt'

import csv
with open(source_name, 'r') as source, open(target_name, 'wr') as target:
    csv_text = csv.reader(source)
    for row in csv_text:
        target.write(row[7])