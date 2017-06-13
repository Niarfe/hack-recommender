import csv
import pandas as pd
import mysql.connector

product_ids = []

db = mysql.connector.connect(db='matcher', host='PC4', user='grace', passwd='2DM1YG6SrQUW4yg6')
c = db.cursor(buffered=True)
# c.execute("""SET @@group_concat_max_len = 6400000;""")

query = ("""select distinct id
            from production.products
            where is_active and id not in (562, 626, 631);""")
iterable = c.execute(query, multi=True)
for item in iterable:
    for result in item.fetchall():
        product_ids.append(int(result[0]))

# for product_id in product_ids:
#     file = '{}.csv'.format(product_id)
#     data_pprod = pd.read_table(file)

file = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/data/19.csv'
data_pprod =
