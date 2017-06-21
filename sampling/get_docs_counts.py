#!/usr/bin/env python
import requests
import json
from collections import defaultdict
from ptpython.repl import embed
from django.utils.encoding import smart_str
import mysql.connector
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd

def get_product_lookup(db):
    """
    :param db: the credentials for connecting pdxn, use pdxn instead of pc4 is because pdxn has latest table,
            pc4 is outdated

    :return: products_lookup dictionary, {product_id: product_name}
    """
    products_lookup = {}
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
    return products_lookup


def _format_query_dict(query_dict):
    lst_parms = ["{}={}".format(key, query_dict[key]) for key in query_dict]
    return "&".join(lst_parms)


def get_docs_counts(dict_parms):
    # escape to % type string -> urllib.quote(string[,save])
    base_url = "http://dev-search-api"
    query = _format_query_dict(dict_parms)
    full_url = "{}/docs?{}".format(base_url, query)
    # print full_url
    # import sys; sys.exit()
    response = requests.get(full_url)
    jdata = json.loads(response.content)
    total_num = jdata["meta"]["total"]
    return total_num



def write_prod_total_docs_to_file(db, file):
    products_lookup = get_product_lookup(db)
    products_doc_counts = {}
    fw = open(file, 'w')
    fw.write("product_id\tproduct_name\ttotal_docs\n")
    for product_id in products_lookup:
        if product_id not in products_doc_counts:
            products_doc_counts[product_id] = []
            total_num = get_docs_counts(
                {
                    "tawg_ids": "p{}".format(product_id),
                    "per": 1
                }
            )
        fw.write('{}\t{}\t{}\n'.format(product_id, products_lookup[product_id], total_num))
    fw.close()


if __name__ == "__main__":
    db = mysql.connector.connect(db='production', host='pdxn.cx0salcfdftt.us-west-2.rds.amazonaws.com',
                                 user='grace.zhou', passwd='BrZIoLqPsH55emt47yJy')
    file = '../sampling/data/June2017.txt'
    write_prod_total_docs_to_file(db, file)