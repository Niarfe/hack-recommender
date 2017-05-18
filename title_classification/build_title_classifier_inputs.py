from get_products_by_title import write_products_by_url_for_title
import json
import csv
from collections import defaultdict
import random
from pprint import pprint

def fetch_results_from_es(input_title_filenames, output_filename):
    with open(output_filename,'w') as jsonfile:
        jsonfile.truncate()
    for filename in input_title_filenames:
        with open(filename,'r') as f:
             for row in f:
                 print '\n', row.strip()
                 write_products_by_url_for_title(output_filename, row.strip())

def get_counts_by_product(resultsfile_name):
    products = defaultdict(int)
    count = 0
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            # print title_data
            for each_url in title_data['urls'].values():
                for each_prod in each_url:
                    products[each_prod] += 1
    return dict(products)

def get_top_products(resultsfile_name, minicount):
    products = get_counts_by_product(resultsfile_name)
    return sorted([product for product in products.keys() if products[product] >= minicount])


def get_product_hits_by_title(resultsfile_name):
    products = defaultdict(int)
    count = 0
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            # print title_data
            for each_url in title_data['urls'].values():
                count += 1
                for each_prod in each_url:
                    products[each_prod] += 1
    return dict(products), count


def split_results_into_training_and_test(resultsfile_name, percent_test):
    test_file = open('test.json', 'w')
    training_file = open('training.json', 'w')
    with open(resultsfile_name) as resultsfile:
        for row in resultsfile:
            if random.uniform(0, 1) < percent_test:
                test_file.write(row + '\n')
            else:
                training_file.write(row + '\n')


def build_matrix(resultsfile_name, positive_title_set, products_to_use, test_r, balanced_training, balanced_test):
    X = []
    y = []
    testX = []
    testY = []
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            for url in title_data['urls'].keys():

                #create independent variables
                X_row = []
                for product_id in products_to_use:
                    if product_id in title_data['urls'][url]:
                        X_row.append(1)
                    else:
                        X_row.append(0)

                #create dependent variables
                y_val = int(title_data['title'] in positive_title_set)

                #add to X, y, testX, and testY
                if random.uniform(0, 1) < test_r:
                    testX.append(X_row)
                    testY.append(y_val)
                else:
                    X.append(X_row)
                    y.append(y_val)

    if balanced_training:
        sample_size_limit = min(sum(y), len(y) + 1 - sum(y))
        i = 0

        positive_count = 0
        negative_count = 0
        while i < len(y):
            if y[i]:
                positive_count += 1
                if positive_count > sample_size_limit:
                    X.pop(i)
                    y.pop(i)
                else:
                    i += 1
            else:
                negative_count += 1
                if negative_count > sample_size_limit:
                    X.pop(i)
                    y.pop(i)
                else:
                    i += 1
    if balanced_test:
        sample_size_limit = min(sum(testY), len(testY) + 1 - sum(testY))
        i = 0

        positive_count = 0
        negative_count = 0
        while i < len(testY):
            if testY[i]:
                positive_count += 1
                if positive_count > sample_size_limit:
                    testX.pop(i)
                    testY.pop(i)
                else:
                    i += 1
            else:
                negative_count += 1
                if negative_count > sample_size_limit:
                    testX.pop(i)
                    testY.pop(i)
                else:
                    i += 1

    print sum(y), 'positive data points'
    print len(y) + 1 - sum(y), 'negative data points'

    return X, y, testX, testY





