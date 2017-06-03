from get_products_by_title import write_products_by_url_for_title
import json
import csv
from collections import defaultdict
from django.utils.encoding import smart_str
import random
from pprint import pprint
import os
from os.path import basename
from django.utils.encoding import smart_str
import mysql.connector


def fetch_results_from_es(input_title_filenames, output_filename):
    with open(output_filename,'w') as jsonfile:
        jsonfile.truncate()
    for filename in input_title_filenames:
        with open(filename,'r') as f:
             for row in f:
                 print '\n', row.strip()
                 write_products_by_url_for_title(output_filename, row.strip())

def get_persona_type(input_title_filenames):
    persona_type = {}
    for filename in input_title_filenames:
        persona_type[basename(os.path.splitext(filename)[0])] = []
        with open(filename,'r') as f:
             for row in f:
                 # print '\n', row.strip()
                 persona_type[basename(os.path.splitext(filename)[0])].append(row.strip())
    return persona_type

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

def get_blacklisted_products_by_product_type(resultsfile_name, product_type_id):
    """ create a product blacklist of products that are from the category of vertical market """
    # get urls
    urls = []
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            for url in title_data['urls'].keys():
                urls.append(url)
    db = mysql.connector.connect(db='matcher', host='PC4', user='grace', passwd='2DM1YG6SrQUW4yg6')
    c = db.cursor(buffered=True)
    query = ("""select p.name, pt.product_id from production.products p
                join production.products_tags pt on p.id=pt.product_id
                join production.tags t on pt.tag_id=t.id
                where t.id={};""")
    query = query.format(product_type_id)
    iterable = c.execute(query, multi=True)
    black_prod_dict = {}
    for item in iterable:
        for result in item.fetchall():
            product_name = result[0]
            product_id = result[1]
            if product_id not in black_prod_dict:
                black_prod_dict[product_id] = product_name
    return black_prod_dict.keys()

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

def get_blacklist_products_by_last_date_verified(resultsfile_name, most_recent_verified_date):
    """ filter products by last verification date,
    create a black list of products that is verified before most_recent_verified_date"""
    # get urls
    urls = []
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            for url in title_data['urls'].keys():
                urls.append(url)
    db = mysql.connector.connect(db='matcher', host='PC4', user='grace', passwd='2DM1YG6SrQUW4yg6')
    c = db.cursor(buffered=True)
    query = ("""SELECT url, product_id, last_verified_at
                FROM matcher.url_mrf_global_hits
                WHERE url IN {} and WHERE last_verified_at < {};""")
    query = query.format(tuple(urls), most_recent_verified_date)
    iterable = c.execute(query, multi=True)
    black_dict = {}
    for item in iterable:
        for result in item.fetchall():
            url = result[0]
            product_id = result[1]
            if url not in black_dict:
                black_dict[url] = []
                if product_id not in black_dict[url]:
                    black_dict[url].append(product_id)
    return black_dict




def build_matrix(resultsfile_name, persona_type, products_to_use, test_r, balanced_training=False, balanced_test=False):
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
    """ get revenue range and employee range by url"""
    # get urls
    rev_emp_lookup = {}
    urls = []
    db = mysql.connector.connect(db='matcher', host='db-raven', user='lucia_databaser', passwd='yZdpi8SKeeaNLGMUjS6H')
    c = db.cursor(buffered=True)
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            for url in title_data['urls'].keys():
                urls.append(smart_str(url))
    for i in range((len(urls)/5000)+1):
        # print i
        query = ("""SELECT url, revenue_range_name, employees_range_name
                                    FROM integration.url_firmographics
                                    WHERE url IN {};""")
        if (i+1)*5000 < len(urls):
            query = query.format(tuple(urls[i*5000:(i+1)*5000]))
        else:
            # print'last piece', len(urls[i*5000:len(urls)-1])
            query = query.format(tuple(urls[i*5000:len(urls)-1]))
        # print query
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
    # print rev_emp_lookup
    return rev_emp_lookup


def freq_analysis_adding_rev_emp_inputs(resultsfile_name, persona_type):
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


def get_urls_in_results(resultsfile_name, url_output):
    fw = open(url_output, 'w')
    fw.write('url\n')
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            for url in title_data['urls'].keys():
                fw.write('{}\n'.format(smart_str(url)))
    fw.close()

def freq_analysis_inputs(resultsfile_name, persona_type):
    persona_dict = {}
    with open(resultsfile_name) as jsonfile:
        for title_data_str in jsonfile:
            title_data = json.loads(title_data_str)
            # print title_data
            # for url in title_data['urls'].keys():
            for psna_type in persona_type.keys():
                if title_data['title'] in persona_type[psna_type]:
                    if psna_type not in persona_dict:
                        persona_dict[psna_type] = []
                    for url in title_data['urls'].keys():
                        persona_dict[psna_type].append(title_data['urls'][url])
    return persona_dict
