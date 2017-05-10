#!/usr/bin/env python
import requests
import json
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


if __name__ == "__main__":
    # str_res =  get_docs({
    #      "c_u": "ucp.org",
    #      "tawg_ids": "p8982",
    #      })

    from Tkinter import *
    root = Tk()

    def show():
        ds = get_docs({
            "c_u": company_url.get(),
            "tawg_ids": tawgs.get()
        })
        json_objs = json.loads(ds)
        print json.dumps(json_objs["docs"], indent=4, sort_keys=True)
        print "Found {} documents".format(json_objs["meta"]["total"])
        print "Length of current retrieved docs: {}".format(len(json_objs["docs"]))
        for doc in json_objs["docs"]:
            print "length {}\tID: {}".format(len(doc["d"]), doc["id"])


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