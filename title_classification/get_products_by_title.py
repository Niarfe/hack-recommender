import requests
from elasticsearch import Elasticsearch
from pprint import pprint
from collections import defaultdict
import json

es = Elasticsearch(hosts=['es-ruby'], port=9200)

def get_top_products_used_by_title(title):
    query_response = es.search(
        index='docs',
        body={
            "query": {
                "bool": {
                    "must": {
                        "term": {"hg_title.title.title_e": title.lower()}
                    },"filter": {
                        "term": {"is_match": True}
                    }
                }
            },
            "aggs": {
                "unique_tawgs": {
                    "terms": {
                        "field": "tawgs.id",
                        "size": 200
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
    product_ids_to_return = [int(aggregation_result['key'][1:]) for aggregation_result in aggregation_results if aggregation_result['key'][0] == 'p' and aggregation_result['doc_count'] >= 10]
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
    return [aggregation_result['key'] for aggregation_result in aggregation_results]

def get_products_by_url_for_title(title):
    products_by_url = defaultdict(set)

    product_ids = get_top_products_used_by_title(title)
    print 'Getting URLs for %d products...' % len(product_ids)
    for product_id in product_ids:
        urls = get_urls_for_title_and_product(title, product_id)
        for url in urls:
            products_by_url[url].add(product_id)

    print 'Fetched %d total URLs.' % len(products_by_url)
    return {url: list(products_by_url[url]) for url in products_by_url.keys()}

def write_products_by_url_for_title(fname, title):
    f = open(fname, mode='a+')
    products_by_url = get_products_by_url_for_title(title)
    json.dump({'title': title, 'urls': products_by_url}, f)
    f.write('\n')
    f.close()

