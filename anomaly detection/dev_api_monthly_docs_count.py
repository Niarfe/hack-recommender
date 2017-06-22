#!/usr/bin/env python
import requests
import json
from collections import defaultdict
from ptpython.repl import embed
from django.utils.encoding import smart_str
import mysql.connector
from ptpython.repl import embed
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


def get_histogram(dict_parms):
    # escape to % type string -> urllib.quote(string[,save])
    url = "http://dev-search-api/search_histograms"
    query = dict_parms
    header_dict = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'postman-token': "1708e6d6-98cb-4231-3fd6-beafd548aabb"
    }
    # import sys; sys.exit()
    response = requests.request("POST", url, data=query, headers=header_dict)
    return response.text



if __name__ == "__main__":
    db = mysql.connector.connect(db='production', host='pdxn.cx0salcfdftt.us-west-2.rds.amazonaws.com',
                                 user='grace.zhou', passwd='BrZIoLqPsH55emt47yJy')
    products_lookup = get_product_lookup(db)
    products_no_date = {}
    payload = "{\"search_histogram\":{\"search_count_type\":\"UNIQUE\",\"doc_field\":\"DUNS\",\"histogram_interval\":\"MONTHLY\",\"search_argument_set\":{\"id\":\"0bb12e97622e8c89\",\"arguments\":{\"c_u\":\"ibm.com\",\"tawg_ids\":\"p40\"}},\"search_histogram_counts\":[]}}"
    docs = get_histogram(payload)
    print docs