from get_products_by_title_adding_filters_version import write_products_by_url_for_title
import json
from collections import defaultdict
import random
import os
from os.path import basename
from django.utils.encoding import smart_str
import mysql.connector


def fetch_results_from_es(input_title_filenames, output_filename, product_type_id, most_recent_verified_date):
    """

    :param input_title_filenames: persona title files, each file has the titles for that person
    :param output_filename: result json file with url and the products that used by that url and the title for that usage
    :param product_type_id: the type id of the products from the category of vertical market
    :param most_recent_verified_date: the minimum date for filter the outdated products
    :return: return result json file
    """
    with open(output_filename, 'w') as jsonfile:
        jsonfile.truncate()
    for filename in input_title_filenames:
        with open(filename,'r') as f:
            for row in f:
                print '\n', row.strip()
                write_products_by_url_for_title(output_filename, row.strip(), product_type_id, most_recent_verified_date)


def get_persona_type(input_title_filenames):
    """

    :param input_title_filenames: persona title files, each file has the titles for that person
    :return: the name of each title file to get the persona type, because all persona files were named by person
    """
    persona_type = {}
    for filename in input_title_filenames:
        persona_type[basename(os.path.splitext(filename)[0])] = []
        with open(filename,'r') as f:
             for row in f:
                 # print '\n', row.strip()
                 persona_type[basename(os.path.splitext(filename)[0])].append(row.strip())
    return persona_type


def get_counts_by_product(resultsfile_name):
    """

    :param resultsfile_name: results json file
    :return: a dictionary with product id is the key and the value is the occurence of that product
            in result file
    """
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
    """

    :param resultsfile_name: result json file
    :param minicount: the mini frequent that we only include products have counts more than mini frequent
    :return: a list of products that counts more than mini frequent
    """
    products = get_counts_by_product(resultsfile_name)
    return sorted([product for product in products.keys() if products[product] >= minicount])


def get_product_hits_by_title(resultsfile_name):
    """

    :param resultsfile_name: result json fiel
    :return: return a dictionary with product_id is key value and the frequent is the value
    """
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
    """

    :param resultsfile_name: result json file
    :param percent_test: the ratio of test set we want to set
    :return:
    """
    test_file = open('test.json', 'w')
    training_file = open('training.json', 'w')
    with open(resultsfile_name) as resultsfile:
        for row in resultsfile:
            if random.uniform(0, 1) < percent_test:
                test_file.write(row + '\n')
            else:
                training_file.write(row + '\n')


def build_matrix(resultsfile_name, persona_type, products_to_use, test_r, balanced_training=False, balanced_test=False):
    """

    :param resultsfile_name: result json file
    :param persona_type: the name of each persona
    :param products_to_use: the products that we want to include
    :param test_r: test ratio
    :param balanced_training: a switch for manually balancing training set
    :param balanced_test: a switch for manually balancing test set
    :return: training set, test set
    """
    X = []
    y = []
    testX = []
    testY = []
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            # print title_data
            for url in title_data['urls'].keys():
                # print url
                #create independent variables
                X_row = []
                for product_id in products_to_use:
                    if product_id in title_data['urls'][url]:
                        X_row.append(1)
                    else:
                        X_row.append(0)
            # create dependent variables
            # y_val = []

                for psna_type in persona_type.keys():
                    if title_data['title'] in persona_type[psna_type]:
                        # print 'document title', title_data['title']
                        # print title
                        y_val = psna_type
                        # print 'y for each url', y_val
                #add to X, y, testX, and testY
                if random.uniform(0, 1) < test_r:
                    testX.append(X_row)
                    testY.append(y_val)
                else:
                    X.append(X_row)
                    y.append(y_val)
    # # if balanced_training:
    #     sample_size_limit = min(sum(y), len(y) + 1 - sum(y))
    #     i = 0
    #
    #     positive_count = 0
    #     negative_count = 0
    #     while i < len(y):
    #         if y[i]:
    #             positive_count += 1
    #             if positive_count > sample_size_limit:
    #                 X.pop(i)
    #                 y.pop(i)
    #             else:
    #                 i += 1
    #         else:
    #             negative_count += 1
    #             if negative_count > sample_size_limit:
    #                 X.pop(i)
    #                 y.pop(i)
    #             else:
    #                 i += 1
    # if balanced_test:
    #     sample_size_limit = min(sum(testY), len(testY) + 1 - sum(testY))
    #     i = 0
    #
    #     positive_count = 0
    #     negative_count = 0
    #     while i < len(testY):
    #         if testY[i]:
    #             positive_count += 1
    #             if positive_count > sample_size_limit:
    #                 testX.pop(i)
    #                 testY.pop(i)
    #             else:
    #                 i += 1
    #         else:
    #             negative_count += 1
    #             if negative_count > sample_size_limit:
    #                 testX.pop(i)
    #                 testY.pop(i)
    #             else:
    #                 i += 1
    #
    # print sum(y), 'positive data points'
    # print len(y) + 1 - sum(y), 'negative data points'

    return X, y, testX, testY


def revenue_company_size_lookup(resultsfile_name):
    """

    :param resultsfile_name: result json file
    :return: a dictionary with url is the key and for each url, revenue_range and employees_range are the values
    """
    # get urls
    rev_emp_lookup = {}
    urls = []
    db = mysql.connector.connect(db='matcher', host='PC4', user='grace', passwd='2DM1YG6SrQUW4yg6')
    # db = mysql.connector.connect(db='matcher', host='db-raven', user='lucia_databaser', passwd='yZdpi8SKeeaNLGMUjS6H')
    c = db.cursor(buffered=True)
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            for url in title_data['urls'].keys():
                urls.append(smart_str(url))
    for i in range((len(urls)/5000)+1):
        query = ("""SELECT url, revenue_range, employees_range
                                    FROM integration.combined_urls
                                    WHERE url IN {};""")
        if (i+1)*5000 < len(urls):
            query = query.format(tuple(urls[i*5000:(i+1)*5000]))
        else:
            query = query.format(tuple(urls[i*5000:len(urls)-1]))
        iterable = c.execute(query, multi=True)
        for item in iterable:
            for result in item.fetchall():
                url = smart_str(result[0])
                revenue_range = smart_str(result[1])
                # print revenue_range
                employees_range = smart_str(result[2])
                if url not in rev_emp_lookup:
                    rev_emp_lookup[url] = {}
                rev_emp_lookup[url]['revenue_range'] = revenue_range
                rev_emp_lookup[url]['employees_range'] = employees_range
    print len(rev_emp_lookup.keys())
    print len(list(set(urls)))
    return rev_emp_lookup


def freq_analysis_adding_rev_emp_inputs(resultsfile_name, persona_type):
    """

    :param resultsfile_name: result jason file
    :param persona_type: name of each persona
    :return: a persona dictionary with persona type is key and for different revenue_range and employees size
            the products that are used by the urls in that revenue range and employees size.
    """
    persona_dict = {}
    rev_emp_lookup = revenue_company_size_lookup(resultsfile_name)
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            # print title_data
            # for url in title_data['urls'].keys():
            for psna_type in persona_type.keys():
                if title_data['title'] in persona_type[psna_type]:
                    if psna_type not in persona_dict:
                        persona_dict[psna_type] = {}
                    for url in title_data['urls'].keys():
                        if smart_str(url) in rev_emp_lookup.keys():
                            revenue = smart_str(rev_emp_lookup[smart_str(url)]['revenue_range'])
                            employee = smart_str(rev_emp_lookup[smart_str(url)]['employees_range'])
                        else:
                            revenue = 'None'
                            employee = 'None'
                        if revenue not in persona_dict[psna_type].keys():
                            persona_dict[psna_type][revenue] = []
                        if employee not in persona_dict[psna_type].keys():
                            persona_dict[psna_type][employee] = []
                        persona_dict[psna_type][revenue].append(title_data['urls'][url])
                        persona_dict[psna_type][employee].append(title_data['urls'][url])
    print persona_dict['finance']
    return persona_dict


def freq_analysis_inputs(resultsfile_name, persona_type):
    """

    :param resultsfile_name: result json file
    :param persona_type: the name of persona type
    :return: a dictionary, persona type is the key and the value is the lists of products used by the url in that pesona
            type.
    """
    persona_dict = {}
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            for psna_type in persona_type.keys():
                if title_data['title'] in persona_type[psna_type]:
                    if psna_type not in persona_dict:
                        persona_dict[psna_type] = []
                    for url in title_data['urls'].keys():
                        persona_dict[psna_type].append(title_data['urls'][url])
    return persona_dict
