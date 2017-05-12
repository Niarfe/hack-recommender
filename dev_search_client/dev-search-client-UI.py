#!/usr/bin/env python
import requests
import json
from collections import defaultdict
from ptpython.repl import embed

def _format_query_dict(query_dict):
    lst_parms = ["{}={}".format(key, query_dict[key]) for key in query_dict]
    return "&".join(lst_parms)



def get_docs(dict_parms):
    # escape to % type string -> urllib.quote(string[,save])
    base_url = "http://dev-search-api" 
    query = _format_query_dict(dict_parms)
    full_url = "{}/docs?{}".format(base_url, query)
    print full_url
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
        counts[len(doc['d'])].append(doc['id']) 
    
    return counts


if __name__ == "__main__":
    from Tkinter import *
    root = Tk()

    def show():
        docs = get_all_docs({
            "c_u": company_url.get(),
            "tawg_ids": tawgs.get()
        })
        print "Found {} documents".format(len(docs))
        counts = count_by_length(docs)
        num = 1
        for key in counts.keys():
            print num, key, counts[key]
            num += 1


    Label(root, text="Company url").grid(row=1, column=1)
    company_url = StringVar()
    Entry(root, width=40, textvariable=company_url).grid(row=1, column=2, columnspan=2)
    company_url.set("amfam.com")

    Label(root, text="Tawg IDs:").grid(row=2, column=1, sticky='w')
    tawgs= StringVar() # defines the widget state as string
    Entry(root, width=40,  textvariable=tawgs).grid(row=2, column=2, columnspan=2) 
    tawgs.set("p6426")

    Button(root,text="Search", command=show).grid(row=3, column=3)

    #demo of Boolean var
    remember_me = BooleanVar()
    Checkbutton(root, text="Remember Me", variable=remember_me).grid(row=3, column=2)
    remember_me.set(True)

    root.mainloop() 