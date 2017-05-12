#!/usr/bin/env python
import requests
import json
from collections import defaultdict
from ptpython.repl import embed
import csv
def _format_query_dict(query_dict):
    lst_parms = ["{}={}".format(key, query_dict[key]) for key in query_dict]
    return "&".join(lst_parms)



def get_docs(dict_parms):
    # escape to % type string -> urllib.quote(string[,save])
    base_url = "http://dev-search-api" 
    query = _format_query_dict(dict_parms)
    full_url = "{}/docs?{}".format(base_url, query)
    #print full_url
    #import sys; sys.exit()
    response = requests.get(full_url)
    return response.content


def get_all_docs(dict_parms):
    all_docs = []
    more_documents = True
    n_page = 1
    while more_documents:
        dict_parms['page'] = n_page
        ds = get_docs(dict_parms)
        json_objs = json.loads(ds)
        if len(json_objs["docs"]) == 0:
            more_documents = False
            break
        for obj in json_objs["docs"]:
            all_docs.append(obj)
        n_page += 1
    #embed(globals(), locals())
    return all_docs
            
def count_by_length(docs):
    counts = defaultdict(list) 

    for doc in docs:
        try:
            counts[len(doc['d'])].append(doc['id'])
        except:
            doc['d'] = []
            doc['d'].append(doc['id']) 
    
    return counts


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser("Get counts of duplicates between a company and a product")
    parser.add_argument("--source",  dest="source",                         required=True, help="Source csv file with col1: url, col2: product, col3: product_id")
    parser.add_argument("--cu",      dest="c_u",      default="amfam.com",  required=False, help="Company URL")
    parser.add_argument("--tawgids", dest="tawg_ids", default="p6426",        required=False, help="Tawg ids")
    args = parser.parse_args()

    outnum = 1
    with open(args.source, 'rb') as source:
        csv_file = csv.reader(source) 
        for row in csv_file:
            docs = get_all_docs(
                {
                    "c_u": row[0].strip(),
                    "tawg_ids": "p{}".format(row[2].strip()) 
                })


            counts = count_by_length(docs)
            num = 1
            arr_dups = []
            for key in counts.keys():
                if len(counts[key]) > 1:
                    #print num, key, counts[key]
                    arr_dups.append(len(counts[key]))
                num += 1

            print "{}\t{}\t{}\t{}\t{}".format(outnum, row[0].strip(), row[2].strip(), str(len(docs)), str(arr_dups))
            outnum += 1