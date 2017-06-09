from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from collections import defaultdict
from build_multi_titles_classifier_inputs import *
from django.utils.encoding import smart_str
from sklearn.feature_extraction import DictVectorizer
import mysql.connector



# determine which products we want to use in our model
products_to_use = get_top_products('inputs/results_sql.json', 20)

# get feature names from products.txt
products_lookup = {}
db = mysql.connector.connect(db='production', host='pdxn.cx0salcfdftt.us-west-2.rds.amazonaws.com', user='grace.zhou', passwd='BrZIoLqPsH55emt47yJy')
c = db.cursor(buffered=True)
query = ("""
        SELECT id, name FROM production.products;
        """)
iterable = c.execute(query, multi=True)
for item in iterable:
    for result in item.fetchall():
        product_id = result[0]
        product_name = smart_str(result[1])
        if product_id not in products_lookup:
            products_lookup[product_id] = []
        products_lookup[product_id] = product_name

feature_names = [str(product_id) + ',' + products_lookup[product_id] for product_id in products_to_use]

results_filename='inputs/results_sql.json'
title_filenames = [
    'inputs/titles/cross_lob_exec.txt',
    'inputs/titles/dev_analyst.txt',
    'inputs/titles/ent_cloud_arch.txt',
    'inputs/titles/finance.txt',
    'inputs/titles/it_exec.txt',
    'inputs/titles/it_in_lob.txt',
    'inputs/titles/it_ops.txt',
    'inputs/titles/marketing.txt',
]
######################## fetch data ###################
# fetch_results_from_es(title_filenames, results_filename)
person_type = get_persona_type(title_filenames)
persona_dict = freq_analysis_inputs('inputs/results_sql.json', person_type)

# get the count for each product in every persona
prod_counts_dict = {}
for persona_type in persona_dict.keys():
    # print persona_type
    # print persona_dict[persona_type]
    if persona_type not in prod_counts_dict.keys():
        prod_counts_dict[persona_type] = defaultdict(int)
    for products_used_by_url in persona_dict[persona_type]:
        for product in products_used_by_url:
            prod_counts_dict[persona_type][products_lookup[product]] += 1



# put all products dictionary to a list and vectorize the dictionary to a array
v = DictVectorizer(sparse=False)
dict_list = []
for persona_type in persona_dict:
    print persona_type
    # print prod_counts_dict[persona_type]
    dict_list.append(dict(prod_counts_dict[persona_type]))
matrix = v.fit_transform(dict_list)
# print len(dict_list)
feature_names = v.feature_names_
transformer = TfidfTransformer()
tfidf_weights = transformer.fit_transform(matrix).toarray().transpose()
print tfidf_weights.shape
print tfidf_weights

tfidf_file = 'outputs/tf_idf/tfidf_weights.txt'
fw = open(tfidf_file, 'w')
fw.write('products\tent_cloud_arch\tit_ops\tfinance\tmarketing\tit_in_lob\tit_exec\tcross_lob_exec\tdev_analyst\n')
for i in range(tfidf_weights.shape[0]): # loop over each products(rows)
    # for j in range(tfidf_weights.shape[1]): # loop over each persona(columns)
    fw.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(feature_names[i], tfidf_weights[i,0], tfidf_weights[i,1], tfidf_weights[i,2], tfidf_weights[i,3], tfidf_weights[i,4], tfidf_weights[i,5], tfidf_weights[i,6], tfidf_weights[i,7]))
fw.close()


