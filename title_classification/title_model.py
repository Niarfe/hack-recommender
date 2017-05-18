from __future__ import division
from build_title_classifier_inputs import *
from sklearn.naive_bayes import BernoulliNB
import numpy as np
import random
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import operator
import pandas as pd

pts = []
with open('cloud_arch_titles.txt','r') as f:
     for row in f:
         pts.append(row.strip())
products_to_use, all_prod_dict, total_count= get_top_products('results.json', 20)
cloud_dict, cloud_count = get_product_hits_by_title('cloud_arch.json')
it_dict, it_count = get_product_hits_by_title('it_security.json')

print cloud_dict
print it_dict

products_lookup = {}
with open('products.txt', 'r') as f:
    for row in f:
        line = row.split('\t')
        products_lookup[int(line[0])] = line[1].strip()

cloud_prod_dict = {}
it_prod_dict = {}
for prod in cloud_dict.keys():
    prod_name = products_lookup[prod]
    cloud_prod_dict[prod_name] = cloud_dict[prod] / cloud_count

for prod in it_dict.keys():
    prod_name = products_lookup[prod]
    it_prod_dict[prod_name] = it_dict[prod] / it_count

#sort dictionary by probabilities
sorted_cloud_prob = sorted(cloud_prod_dict.items(), key=operator.itemgetter(1), reverse= True)
sorted_it_prob = sorted(it_prod_dict.items(), key=operator.itemgetter(1), reverse=True)

sorted_cloud_df = pd.DataFrame(sorted_cloud_prob, columns=['product', 'Cloud_arch_weights'])
sorted_it_df = pd.DataFrame(sorted_it_prob, columns=['product', 'IT_security_weights'])

combined_df = pd.merge(sorted_cloud_df, sorted_it_df, how='outer', on=['product']).fillna(0)
combined_df['weight difference'] = np.abs(combined_df['Cloud_arch_weights'] - combined_df['IT_security_weights'])

combined_df.to_csv('data/combined_report.csv')
filename = 'data/cloud_weights.txt'
fw = open(filename, 'w')
fw.write('product\tweights\n')
for element in sorted_cloud_prob:
    fw.write('{}\t{}\n'.format(element[0], element[1]))
fw.close()

filename = 'data/it_weights.txt'
fw = open(filename, 'w')
fw.write('product\tweights\n')
for element in sorted_it_prob:
    fw.write('{}\t{}\n'.format(element[0], element[1]))
fw.close()
#
X, y, testX, testY = build_matrix('results.json', pts, products_to_use, .3, balanced_training=False, balanced_test=False)
bnb = BernoulliNB()
x_test = np.zeros(len(X[0]))
bnb.fit(X, y)
y_pred = bnb.predict(testX)
cnf_matrix_mnb = confusion_matrix(testY, y_pred)
print total_count
print cloud_count
print it_count
print cnf_matrix_mnb
print accuracy_score(testY, y_pred, normalize=True)


# with open('cloud_arch_product_coef_report.txt', 'w') as report_file:
#     for i in range(len(products_to_use)):
#         product_id = products_to_use[i]
#         product_name = products_lookup[product_id]
#         coef = bnb.coef_[0][i]
#         report_file.write(str(product_id) + '\t' + product_name + '\t'+ str(coef) + '\n')





