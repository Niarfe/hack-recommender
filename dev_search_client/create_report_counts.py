#!/usr/bin/env python

with open('sofarxaa.tsv', 'r') as source, open('countreport.tsv', 'wr') as target:
    for line in source:
        l_items = line.split('\t')
        company = l_items[1]
        pid = l_items[2]
        doc_total = int(l_items[3])
        try:
            print eval(l_items[4])
            l_dups = eval(l_items[4])
        except:
            print "EXCEPTION converting l_items for {}-{}".format(company, pid)
            l_dups = []     
        cardinality = len(l_dups)
        total_dups = sum(l_dups)
        unique_docs = doc_total - total_dups + cardinality
        
        percent_loss = float(doc_total - unique_docs)/doc_total * 100.0 if doc_total > 0 else 0
        target.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
            company,
            pid,
            doc_total,
            unique_docs,
            percent_loss,
            cardinality
        )) 

        