#!/usr/bin/env python
"""
Load json database into your local couchdb database
or change the db string to point you any other db on network
* use at your own risk and feel free to use and distribute this code * 
Author Tanmay Dutta
"""
#  As per comment above this is from https://bitbucket.org/tdatta/tools/src/bb67f71fcf1b29678581ea36d55ad36e8bd463f7/jsonDb_to_Couch.py?at=master&fileviewer=file-view-default
#  which I got to after http://stackoverflow.com/questions/790757/import-json-file-to-couch-db

import sys
import couchdb
import json

DB_STRING="http://127.0.0.1:5984"


def main(json_file,
         db_name,
         couchdb_address):
    # 1. Create the database.. No error checking here because we want to get exception if db exists
    couch = couchdb.Server(couchdb_address)
    db = couch.create(db_name)
    # 2 Read the json line by line and put into the db
    with open(json_file) as jsonfile:
        for row in jsonfile:
            db_entry = json.loads(row) 
            db.save(db_entry)
    


if __name__=='__main__':
    print "Call as <jsondb.json> <new_db> <optional db string>"
    args = sys.argv[1:]
    json_file = args[0]
    try:
        db_name = args[1]
    except:
        db_name = json_file.split(".")[0]
    try:
        db_str = args[2]
    except:
        db_str = DB_STRING
    main(json_file,
         db_name,
         db_str)
