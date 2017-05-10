#!/usr/bin/env python
import json
import csv
import re
import sys
from ptpython.repl import embed

key_schema = [
    u'begin-year',
    u'begin-day',
    u'begin-month',
    u'end-year',
    u'end-day',
    u'end-month',
    u'description',
    u'employer',
    u'current',
    u'location-country',
    u'location-state',
    u'location-city',
    u'position',
    u'uid',
    u'industry',
    u'linkedinid',
    u'size'
    ]

def raw_dump_to_json_one_per():
    stopat=0
    keylist = []
    with open('Smart_Recruiters_Sample.csv', 'r') as source:
        with open('smart_recruiters_sample.json', 'wr') as target:
            for line in source:
                line =  line.replace('""','"')
                sline = line.partition("[")
                fixedline = '{"date":' + sline[0] + '","data":' + sline[1] + sline[2].strip().rstrip('"') + '}\n'
                jobj = json.loads(fixedline)
                for obj in jobj['data']:
                    jdump = {}
                    jdump['date'] = jobj['date']
                    jdump['snippet'] = obj
                    target.write(json.dumps(jdump) + '\n')

raw_dump_to_json_one_per()

# def get_compund_key_value(d_obj, compound_key):
#     """Extracts a value from d_obj from a compunt key <key1>-<key2>.
#         The compound key is a string with a dash.  It may be only a single key"""
    
#     c_keys = compound_key.split('-')
#     if c_keys[0] not in d_obj.keys():
#         return ""

#     assert len(c_keys) <= 2, "YO! there are more than 2 keys in {}".format(compount_key)
#     if len(c_keys) == 2:
#         #print "\t\t{}".format(d_obj)
#         #print "\t\tCOMPOUND KEYS: {}".format(c_keys)
#         if type(d_obj[c_keys[0]]) == type({}) and c_keys[1] in d_obj[c_keys[0]].keys():
#             return d_obj[c_keys[0]][c_keys[1]]
#         else:
#             return ""
#             #embed(globals(), locals())
#             #raise "We really should return something for compound key" 
#     elif len(c_keys) == 1:
#         val = d_obj[c_keys[0]]
#         if type(val) == type(False):
#             return str(val)
#         if type(val) != type(u''):
#             print "Wrong object type return"
#             print d_obj
#             print c_keys
#             print d_obj[c_keys[0]]
#             print type(d_obj[c_keys[0]])
#             sys.exit()
        
#         return d_obj[c_keys[0]]
#     else:
#         raise "More than 2 keys in dictionary"

# snippet = ""
# with open('smart_recruiters_sample.json', 'r') as source:
#     with open('smart_snippets.tsv', 'wr') as target:
#         header = "date\t"
#         for key in key_schema:
#             header += "{}\t".format(key)
#         header += '\n'
#         target.write(header)
#         for line in source:
#             jstr = json.loads(line)
#             date = jstr['date']
#             for obj in jstr['data']:
#                 snippet = "{}\t".format(date)
#                 for c_key in key_schema:
#                     snippet += "{}\t".format(get_compund_key_value(obj, c_key).encode('ascii', 'ignore').decode('ascii').replace('\t', ' ').replace('\n', ' ').replace('\r', ' '))
#                 snippet += '\n'
#                 target.write(snippet)
#             snippet = ''

                