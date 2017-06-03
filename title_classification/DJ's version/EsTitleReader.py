import os
from collections import defaultdict
import json
from os.path import basename
from pprint import pprint

class EsTitleReader:

    def __init__(self, es, min_date='2000-01-01', debug_mode=False):
        self.es = es
        self.min_date = min_date
        self.debug_mode = debug_mode

    def get_top_products_used_by_title(self, title):
        query_response = self.es.search(
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
                                        "from": self.min_date
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
                        }
                    }
                }
            }
        )

        aggregation_results = query_response['aggregations']['unique_tawgs']['buckets']
        if self.debug_mode:
            print aggregation_results
        product_ids_to_return = [int(aggregation_result['key'][1:]) for aggregation_result in aggregation_results if
                                 aggregation_result['key'][0] == 'p' and aggregation_result['doc_count'] >= 10]
        # print product_ids_to_return
        return product_ids_to_return

    def get_urls_for_title_and_product(self, title, product_id):
        query_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "term": {"hg_title.title.title_e": title.lower()}
                            },
                            {
                                "range": {
                                    "dates": {
                                        "from": self.min_date
                                    }
                                }
                            }
                        ],
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
        if self.debug_mode:
            print json.dumps(query_body)
        query_response = self.es.search(
            index='docs',
            body=query_body
        )
        aggregation_results = query_response['aggregations']['unique_urls']['buckets']
        # print aggregation_results
        return [aggregation_result['key'] for aggregation_result in aggregation_results]


    def get_products_by_url_for_title(self, title):
        # product_type_id is the type_id of markets, most_recent_verified_date is the threshold for filter outdated products
        products_by_url = defaultdict(set)
        # products from the category of vertical markets
        product_ids = self.get_top_products_used_by_title(title)

        print '\nGetting URLs for %d products used by %s...' % (len(product_ids), title)

        for product_id in product_ids:
            if self.debug_mode:
                print 'Getting URLs with a %s using product %d...' % (title, product_id)
            urls = self.get_urls_for_title_and_product(title, product_id)
            for url in urls:
                products_by_url[url].add(product_id)
        print 'Fetched %d total URLs.' % len(products_by_url)
        print {url: list(products_by_url[url]) for url in products_by_url.keys()}
        return {url: list(products_by_url[url]) for url in products_by_url.keys()}

    def write_products_by_url_for_title(self, fname, title):
        persona_type = basename(os.path.splitext(fname)[0])
        if self.debug_mode:
            print 'title name', persona_type
            print 'sub title', title
        f = open(fname, mode='a+')
        products_by_url = self.get_products_by_url_for_title(title)
        json.dump({'title': title, 'urls': products_by_url}, f)
        f.write('\n')
        f.close()