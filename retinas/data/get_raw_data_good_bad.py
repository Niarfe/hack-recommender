#!/usr/bin/env python

source_name = 'raw_data_good_bad.tsv'
target_name = 'content_good_bad.txt'

import csv
with open(source_name, 'r') as source, open(target_name, 'wr') as target:
    for line in source.readlines():
        elems = line.split('\t')
        target.write("{} {}\n".format(elems[0], elems[1].lower().strip()))