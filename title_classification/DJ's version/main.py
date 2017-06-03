from build_multi_titles_classifier_inputs import *
import pandas as pd
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB, GaussianNB, BernoulliNB
import operator
from sklearn.metrics import accuracy_score
from ProductBlacklist import ProductBlacklist
from EsTitleReader import EsTitleReader
from elasticsearch import Elasticsearch
import numpy as np


def get_model_from_results_file(title_filenames, results_filename, persona_type, products_to_use, test_r, balanced_training=False, balanced_test=False):

    persona_type = get_persona_type(title_filenames)
    # build Positive Title Set
    products_to_use = get_top_products(results_filename, 20)

    X, y, testX, testY = build_matrix(results_filename, persona_type, products_to_use, test_r, balanced_training,
                                      balanced_test)

    x = pd.DataFrame(X, columns=products_to_use)   # finalize training X
    y_df = pd.DataFrame(y, columns=['job titles'])
    testY_series = pd.Series(testY)
    y_array = np.asarray(y)
    y_names = np.asarray(persona_type.keys())
    Y = pd.factorize(y_array)[0]    # finalize training Y
    # fit model
    gnb = GaussianNB()
    mnb = MultinomialNB()
    y_pred_gnb = gnb.fit(X, y).predict(testX)
    print type(y_pred_gnb)
    print 'GaussianNB'
    print pd.crosstab(testY_series, y_pred_gnb, rownames=['Actual Species'], colnames=['Predicted Species'])
    print accuracy_score(testY, y_pred_gnb, normalize=True)

    print 'MultinomialNB'
    y_pred_mnb = mnb.fit(X, y).predict(testX)
    print pd.crosstab(testY_series, y_pred_mnb, rownames=['Actual Species'], colnames=['Predicted Species'])
    print accuracy_score(testY, y_pred_mnb, normalize=True)

    print 'BernoulliNB'
    clf = BernoulliNB()
    y_pred_clf = clf.fit(X, y).predict(testX)
    print pd.crosstab(testY_series, y_pred_clf, rownames=['Actual Species'], colnames=['Predicted Species'])
    print accuracy_score(testY, y_pred_clf, normalize=True)


def write_coefficients_to_file(model, feature_names, output_filename):
    feature_dict ={}
    for i in range(len(feature_names)):
        if feature_names[i] not in feature_dict:
            feature_dict[feature_names[i]] =[]
        feature_dict[feature_names[i]] = model.coef_[0][i]
    sorted_feature_dict = sorted(feature_dict.items(), key=operator.itemgetter(1),reverse=True)
    # print feature_dict
    # print sorted_feature_dict
    with open(output_filename, 'w') as report_file:
        for i in range(len(sorted_feature_dict)):
            report_file.write(sorted_feature_dict[i][0] + '\t' + str(sorted_feature_dict[i][1]) + '\n')

    pprint(sorted_feature_dict[:7])
    pprint(sorted_feature_dict[-7:])

def fetch_data(title_list_filenames, output_filename):
    es = Elasticsearch(hosts=['es-ruby'], port=9200)
    es_title_reader = EsTitleReader(es, min_date='2015-01-01', debug_mode=True)

    with open(output_filename, 'w') as jsonfile:
        jsonfile.truncate()
    for filename in title_list_filenames:
        with open(filename, 'r') as f:
            for row in f:
                print '\n', row.strip()
                es_title_reader.write_products_by_url_for_title(output_filename, row.strip())

def main():
    results_filename = 'inputs/results.json';
    title_filenames = [
        'inputs/titles/dev_analyst.txt',
        'inputs/titles/ent_cloud_arch.txt',
        'inputs/titles/finance.txt',
        'inputs/titles/it_exec.txt',
        'inputs/titles/it_in_lob.txt',
        'inputs/titles/it_ops.txt',
        'inputs/titles/marketing.txt',
        'inputs/titles/cross_lob_exec.txt'
    ]

    ######################## fetch data ###################
    fetch_data(title_filenames, results_filename)
    person_type = get_persona_type(title_filenames)

    # determine which products we want to use in our model
    top_products = get_top_products('inputs/results.json', 50)
    db = mysql.connector.connect(db='matcher', host='db-raven', user='lucia_databaser', passwd='yZdpi8SKeeaNLGMUjS6H')
    product_blacklist = ProductBlacklist(db)
    product_blacklist.add_products_with_tag_id(142)
    products_to_use = list(set(top_products).difference(product_blacklist.product_ids))

    # build model
    model = get_model_from_results_file(title_filenames, results_filename, person_type, products_to_use, .3, balanced_training=False, balanced_test=False)

    # get feature names from products.txt
    products_lookup = {}
    with open('inputs/products.txt', 'r') as f:
        for row in f:
            line = row.split('\t')
            products_lookup[int(line[0])] = line[1].strip()
    feature_names = [str(product_id) + '\t' + products_lookup[product_id] for product_id in products_to_use]

    # write coefficients to data/lgcoef.txt
    # write_coefficients_to_file(model, feature_names, 'outputs/lg_coef2.txt')





if __name__ == "__main__":
    main()


