import re
import snippets
import csv
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/gracezhou/PycharmProjects/translate/cloud-client/token-translate-0411726cdfed.json"


""" read token for GRACE.csv, create two dictionaries. data dictionary saves all the cleaned patterns,
    product_id as key and cleaned patterns are appended in the value. pattern dictionary saves all the original patterns
    for reference, product_id as key and original patterns are appended in the value."""
FR = 'tokens for GRACE.csv'
pattern = {}
data = {}
with open(FR, 'rb') as csvfile:   #use csv library so that it can be read in the right format
    next(csvfile)
    reader = csv.reader(csvfile, delimiter=',')
    for row in enumerate(reader):
        la = row[1]
        ptn = la[1]
        # remove / \\ and numbers and * from patterns
        lwr_ptn = la[1].lower()
        # only include word character
        wd_ptn = re.sub(r'\W', ' ', lwr_ptn)
        # remove numbers from pattern
        nonum_ptn = re.sub(r'\d', ' ', wd_ptn)
        # combine all spaces to one space
        token = re.sub(r'\s+', ' ', nonum_ptn).strip()
        unit = token.strip()
        unit2 = unit.split(' ')
        unit2 = [x.strip() for x in unit2]
        product_id = la[3]
        # create data dictionary, product_id as the key and all patterns are the value
        if product_id not in data:
            data[product_id] = []
        # create pattern dictionary for lookup, product_id as the key and original patterns are appended in the value
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

""" read products for Grace.csv, create a lookup dictionary for product name matching,
    in the lookup dictionary, product_id as the key and product name as the value"""
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

""" save the translated pattern into a txt file with \t as separator"""
product_ids = data.keys()
LP = 'language_detection_for_patterns.txt'
fw = open(LP, 'w')
fw.write("product_id\tproduct_name\toriginal pattern\ttoken and separated token\tdetected_language\tconfidence_score\ttranslated_language \n")
for i in range(len(product_ids)):
      for j in range(len(data[product_ids[i]])):
        # detect original language and the confidence score for that detection
        confidence_score, detected_lang = snippets.detect_language(data[product_ids[i]][j])
        # if they are not English then translate to English
        if detected_lang != 'en':
                translated_lang = snippets.translate_text('en', data[product_ids[i]][j])
        else:
            # if they are detected as English then copy the string to translated cell
                translated_lang = data[product_ids[i]][j]
        fw.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_ids[i], lookup[product_ids[i]], pattern[product_ids[i]],
                                                       data[product_ids[i]][j], detected_lang, confidence_score, translated_lang))
fw.close()
