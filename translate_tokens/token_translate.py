FR = '/Users/gracezhou/Downloads/tokens for GRACE.csv'
fr = open(FR)
print fr.readline()

token = []
data = {}
for line in fr.readlines():
      la = line.strip().split(',')
      token = la[1].replace('"', '').lower().replace('/', '').replace('\\', '')
      unit = token.strip().split(' ')
      # print unit
      product_id = la[3]
      if product_id not in data:
            data[product_id] = []
      data[product_id].append(token)
      for x in unit:
            # print product_id
            # print 'token', token
            # print 'unit', unit
            # print x
            # print data[product_id]
            # print '++++++++++++'
            if x in data[product_id]:
                  continue
            data[product_id].append(x)
      # data[product_id].append(x for x in unit)

print data
# print token
# for x in token:
#       print x.replace('"', "")

product_ids = data.keys()
print product_ids
LP = '/Users/gracezhou/Documents/DataOps/language_detection_for_patterns.csv'
fw = open(LP, 'w')
fw.write("product_id, pattern, detected_language, translated_language \n")
for i in range(len(product_ids)):
      for j in range(len(data[product_ids[i]])):
            confidence_score, detected_lang = snippets.detect_language(data[product_ids[i]][j])
            if detected_lang != 'en':
                  translated_lang = snippets.translate_text('en', data[product_ids[i]][j])
            else:
                  translated_lang = data[product_ids[i]][j]
            fw.write('{}, {}, {}, {}\n'.format(product_ids[i], data[product_ids[i]][j], detected_lang,  translated_lang))
fw.close()
