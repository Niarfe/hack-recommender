import re
import snippets
import csv
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "token-translate-0411726cdfed.json"


""" read token for GRACE.csv"""
FR = 'tokens for GRACE.csv'
fr = open(FR)
fr.readline()

pattern = {}

data = {}
with open(FR, 'rb') as csvfile:
    next(csvfile)
    reader = csv.reader(csvfile, delimiter=',')
    for row in enumerate(reader):
        la = row[1]
        # remove / \\ and numbers and * from patterns
        ptn = la[1]
        token = re.sub(r'\s+', ' ', re.sub(r'\d', ' ', re.sub(r'\W', ' ', la[1].lower()))).strip()
        unit = token.strip()
        unit2 = unit.split(' ')
        unit2 = [x.strip() for x in unit2]
        product_id = la[3]
        if product_id not in data:
            data[product_id] = []
        if product_id not in pattern:
            pattern[product_id] = []
        if ptn in pattern[product_id]:
            continue
        pattern[product_id].append(ptn)
        if token in data[product_id]:
            continue
        data[product_id].append(token)
        for x in unit2:
            if x in data[product_id] or len(x) == 1:
                continue
            data[product_id].append(x)

""" read products for Grace.csv """
PD = 'products for GRACE.csv'
prod = open(PD)
prod.readline()
lookup = {}
with open(PD, 'rb') as csvfile:
    next(csvfile)
    reader = csv.reader(csvfile, delimiter=',')
    for row in enumerate(reader):
        ls = row[1]
        prod_id = ls[0]
        prod_name = ls[1].replace('"', '')
        if prod_id not in lookup:
            lookup[prod_id] = []
        lookup[prod_id] = prod_name

"""save txt file with \t as seperator"""
product_ids = data.keys()
LP = '../language_detection_for_patterns.txt'
fw = open(LP, 'w')
fw.write("product_id\tproduct_name\toriginal pattern\ttoken and separated token\tdetected_language\tconfidence_score\ttranslated_language \n")
for i in range(len(product_ids)):
    for j in range(len(data[product_ids[i]])):
        print product_ids[i]
        confidence_score, detected_lang = snippets.detect_language(data[product_ids[i]][j])
    if detected_lang != 'en':
            translated_lang = snippets.translate_text('en', data[product_ids[i]][j])
    else:
            translated_lang = data[product_ids[i]][j]
    fw.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_ids[i], lookup[product_ids[i]], pattern[product_ids[i]], 
                                                   data[product_ids[i]][j], detected_lang, confidence_score, translated_lang))
fw.close()
