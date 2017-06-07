from build_multi_titles_classifier_inputs import *
from pymining import itemmining
from fp_growth import find_frequent_itemsets
import operator



# determine which products we want to use in our model
products_to_use = get_top_products('inputs/results_sql.json', 100)

# get feature names from products.txt
products_lookup = {}
with open('inputs/products.txt', 'r') as f:
    for row in f:
        line = row.split('\t')
        products_lookup[int(line[0])] = line[1].strip()
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
# person_type = get_persona_type(title_filenames)
# persona_dict = freq_analysis_inputs('inputs/results.json', person_type)
# print persona_dict
# to get more frequent itemsets for it_exec
# relim_input = itemmining.get_relim_input(persona_dict['it_exec'])
# report = itemmining.relim(relim_input, min_support=200)
# sorted_report = sorted(report.items(), key=operator.itemgetter(1), reverse=True)
# for item in sorted_report:
#     products = []
#     for product in item[0]:
#         products.append(products_lookup[product])
#     print products,'\t',item[1]
# #
# for persona_type in persona_dict.keys():
#     filename = 'outputs/freq_itemsets/{}.txt'.format(persona_type)
#     fw = open(filename,'w')
#     fw.write('frequent_products\t number_of_counts\n')
#     print persona_type
#     for itemset in find_frequent_itemsets(persona_dict[persona_type], 500, include_support=True):
#         product_names = []
#         for product_id in itemset[0]:
#             product_names.append(products_lookup[product_id])
#         print product_names, itemset[1]
#         fw.write('{}\t{}\n'.format(product_names, itemset[1]))
#     fw.close()
#


""" frequent analysis with revenue and employees"""

person_type = get_persona_type(title_filenames)
persona_dict = freq_analysis_adding_rev_emp_inputs(results_filename, person_type)
print persona_dict
for persona_type in persona_dict.keys():
    for key in persona_dict[persona_type].keys():
        filename = 'outputs/freq_itemsets/with_rev_emp_sql/{}_{}.txt'.format(persona_type, key)
        fw = open(filename, 'w')
        fw.write('frequent_products\t number of counts\n')
        for itemset in find_frequent_itemsets(persona_dict[persona_type][key], 100, include_support=True):
            product_names = []
            for product_id in itemset[0]:
                product_names.append(products_lookup[product_id])
            print product_names, itemset[1]
            fw.write('{}\t{}\n'.format(product_names, itemset[1]))
fw.close()