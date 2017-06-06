import requests
from elasticsearch import Elasticsearch
from pprint import pprint
from collections import defaultdict
import json
from django.utils.encoding import smart_str
import os
from os.path import basename
import mysql.connector

es = Elasticsearch(hosts=['es-ruby'], port=9200)

def get_top_products_used_by_title(title, min_date='2000-01-01'):
    query_response = es.search(
        index='docs',
        body={
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {"hg_title.title.title_e": title.lower()}
                        },
                        {
                            "range": {
                                "dates": {
                                    "from": min_date
                                }
                            }
                        }
                    ],
                    "filter": {
                        "term": {"is_match": True}
                    }
                }
            },
            "aggs": {
                "unique_tawgs": {
                    "terms": {
                        "field": "tawgs.id",
                        "size": 300
                    },
                    # "aggs": {
                    #     "unique_urls": {
                    #         "top_hits": {
                    #             "field": "tawgs.id"
                    #         },
                    #     }
                    # }
                }
            }
        }
    )

    # pprint(query_response['aggregations']['unique_tawgs']['buckets'])
    aggregation_results = query_response['aggregations']['unique_tawgs']['buckets']
    # print aggregation_results
    product_ids_to_return = [int(aggregation_result['key'][1:]) for aggregation_result in aggregation_results if aggregation_result['key'][0] == 'p' and aggregation_result['doc_count'] >= 10]
    # print product_ids_to_return
    return product_ids_to_return

def get_urls_for_title_and_product(title, product_id):
    query_response = es.search(
        index='docs',
        body={
            "query": {
                "bool": {
                    "must": [{
                        "term": {"hg_title.title.title_e": title.lower()}
                    }],
                    "filter": [{
                        "term": {"tawgs.id": "p" + str(product_id)}

                    }]
                }
            },
            "aggs": {
                "unique_urls": {
                    "terms": {
                        "field": "c_u.c_u_e",
                        "size": 1000
                    },
                }
            }
        }
    )
    aggregation_results = query_response['aggregations']['unique_urls']['buckets']
    # print aggregation_results
    return [aggregation_result['key'] for aggregation_result in aggregation_results]

def generate_blacklist_by_product_type(product_type_id):
    """ create a product blacklist of products that are from the category of vertical market,
    it returns a dictionary with product id is key and the product name from the category of veritcal market as value"""
    # get urls
    # db = mysql.connector.connect(db='matcher', host='PC4', user='grace', passwd='2DM1YG6SrQUW4yg6')
    db = mysql.connector.connect(db='matcher', host='db-raven', user='lucia_databaser', passwd='yZdpi8SKeeaNLGMUjS6H')
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
    return black_prod_dict


def generate_blacklist_by_LastVerifDate(target_urls, most_recent_verified_date):
    """ filter products by last verification date,
    create a black list of products that is verified before most_recent_verified_date,
    it returns a dictionary with url as key and value is the product id of the outdated products."""
    clean_urls = [smart_str(url) for url in target_urls]
    str_urls = map(str, clean_urls)
    # print str_urls
    # db = mysql.connector.connect(db='matcher', host='PC4', user='grace', passwd='2DM1YG6SrQUW4yg6')
    db = mysql.connector.connect(db='matcher', host='db-raven', user='lucia_databaser', passwd='yZdpi8SKeeaNLGMUjS6H')
    c = db.cursor(buffered=True)
    if len(str_urls) > 1:
        query = ("""SELECT url, product_id, last_verified_at
                    FROM matcher.url_mrf_global_hits
                    WHERE url IN {} and last_verified_at < '{}';""")
        query = query.format(tuple(str_urls), most_recent_verified_date)
    else:
        query = ("""SELECT url, product_id, last_verified_at
                    FROM matcher.url_mrf_global_hits
                    WHERE url = '{}' and last_verified_at < '{}';""")
        element = ' '.join(str(x) for x in str_urls)
        query = query.format(element, most_recent_verified_date)
    # print query
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
    print 'outdated info', len(black_dict.keys())
    return black_dict


def get_products_by_url_for_title(title, product_type_id, most_recent_verified_date):
    # product_type_id is the type_id of markets, most_recent_verified_date is the threshold for filter outdated products
    products_by_url = defaultdict(set)
    # products from the category of vertical markets
    vertical_market_prod = generate_blacklist_by_product_type(product_type_id)
    product_ids = get_top_products_used_by_title(title)
    # print product_ids
    # print 'Getting URLs for %d products...' % len(product_ids)
    for product_id in product_ids:
        if product_id in vertical_market_prod.keys():
            print '{} is not in the right market'.format(product_id)
            continue
        else:
            urls = get_urls_for_title_and_product(title, product_id)
            outdated_urls = generate_blacklist_by_LastVerifDate(urls, most_recent_verified_date)
            # print 'urls with outdated products', outdated_urls
            for url in urls:
                if url in outdated_urls.keys() and product_id == outdated_urls[url]:
                    print '{} with outdated product {}'.format(url, product_id)
                    continue
                else:
                    products_by_url[url].add(product_id)
    # print 'Fetched %d total URLs.' % len(products_by_url)
    print {url: list(products_by_url[url]) for url in products_by_url.keys()}
    return {url: list(products_by_url[url]) for url in products_by_url.keys()}

def write_products_by_url_for_title(fname, title, product_type_id, most_recent_verified_date):
    # persona_type = basename(os.path.splitext(fname)[0])
    # print 'title name', persona_type
    # print 'sub title', title
    f = open(fname, mode='a+')
    products_by_url = get_products_by_url_for_title(title, product_type_id, most_recent_verified_date)
    json.dump({'title': title, 'urls': products_by_url}, f)
    f.write('\n')
    f.close()

