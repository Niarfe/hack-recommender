import mysql.connector
from datetime import datetime
import pandas as pd
import numpy as np
from django.utils.encoding import smart_str
import matplotlib.pyplot as plt


def get_product_ids(db):
    product_ids = {}
    c = db.cursor(buffered=True)
    # c.execute("""SET @@group_concat_max_len = 6400000;""")
    query = ("""select distinct id, name
            from production.products
            where is_active and id not in (562, 626, 631);""")
    iterable = c.execute(query, multi=True)
    for item in iterable:
        for result in item.fetchall():
            id = result[0]
            name = result[1]
            if id not in product_ids:
                product_ids[id] = []
            product_ids[id] = name
    return product_ids


def write_prod_hits_to_file(db):
    c = db.cursor(buffered=True)
    product_ids = get_product_ids(db)
    query2 = ("""
                select concat(year(date), lpad(month(date),2,'0')) as yearmonth, count(*) as hits_this_month
                from matcher.url_mrf_global_hits h
                join matcher.url_mrf_global_hit_dates hd on h.mrf_id = hd.mrf_id
                where product_id = {}
                group by yearmonth;
            """)
    for product_id in product_ids:
        FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/data/{}.csv'.format(product_id)
        fw = open(FN, 'w')
        fw.write("date, number of hits\n")
        print product_id
        query2 = query2.format(product_id)
        iterable = c.execute(query2, multi=True)
        for item in iterable:
            for result in item.fetchall():
                date = datetime.strptime(result[0], '%Y%m').strftime('%Y-%m')
                hits_count = result[1]
                print date, hits_count
                fw.write('{}, {}\n'.format(date, hits_count))
    fw.close()


def get_outliers(db):
    product_ids = get_product_ids(db)
    OF = 'output/detected_outlier.txt'
    of = open(OF, mode='a+')
    of.write('product_id\tdate\tnum_prod_hits\n')
    for product_id in product_ids:
        try:
            FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/data/{}.csv'.format(product_id)
            dataframe = pd.read_table(FN, sep=',')
            Q3, Q1 = np.percentile(dataframe[' number of hits'], [75, 25])
            iqr = Q3 - Q1
            upper_limit = Q3 + 1.5 * iqr
            lower_limit = Q1 - 1.5 * iqr
            num_prod_hits = list(dataframe[' number of hits'])
            dates = list(dataframe['date'])
            # print num_prod_hits
            # print dates
            for i in range(len(num_prod_hits)):
                print num_prod_hits[i] > upper_limit or num_prod_hits[i] < lower_limit
                # print num_prod_hits[i]
                # print upper_limit
                # print lower_limit
                if (num_prod_hits[i] > upper_limit) or (num_prod_hits[i] < lower_limit):
                    print product_ids[product_id], dates[i], num_prod_hits[i]
                    of.write('{}\t{}\t{}\n'.format(product_ids[product_id], dates[i], num_prod_hits[i]))
        except IOError as err:
            print err


def get_outliers_with_z_score(db):
    product_ids = get_product_ids(db)
    OF = 'output/detected_outlier_z_score.txt'
    of = open(OF, mode='a+')
    of.write('product_id\tdate\tnum_prod_hits\n')
    for product_id in product_ids:
        try:
            FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/data/{}.csv'.format(product_id)
            dataframe = pd.read_table(FN, sep=',')
            threshold = 3
            mean_y = np.mean(dataframe[' number of hits'])
            stdev_y = np.std(dataframe[' number of hits'])
            num_prod_hits = list(dataframe[' number of hits'])
            dates = list(dataframe['date'])
            # print num_prod_hits
            # print dates
            for i in range(len(num_prod_hits)):
                print np.abs((num_prod_hits[i] - mean_y)/stdev_y) > threshold
                if np.abs((num_prod_hits[i] - mean_y)/stdev_y) > threshold:
                    # print product_ids[product_id], dates[i], num_prod_hits[i]
                    of.write('{}\t{}\t{}\n'.format(product_ids[product_id], dates[i], num_prod_hits[i]))
        except IOError as err:
            print err


def get_outliers_with_modified_z_score(db):
    product_ids = get_product_ids(db)
    OF = 'output/detected_outlier_modified_z_score.txt'
    of = open(OF, mode='a+')
    of.write('product_id\tdate\tnum_prod_hits\n')
    for product_id in product_ids:
        try:
            FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/data/{}.csv'.format(product_id)
            dataframe = pd.read_table(FN, sep=',')
            threshold = 3.5
            median_y = np.median(dataframe[' number of hits'])
            num_prod_hits = list(dataframe[' number of hits'])
            dates = list(dataframe['date'])
            median_abs_dev_y = np.median([np.abs(y - median_y) for y in num_prod_hits])
            # print num_prod_hits
            # print dates
            for i in range(len(num_prod_hits)):
                print np.abs(0.6745 * (num_prod_hits[i] - median_y) / median_abs_dev_y) > threshold
                if np.abs(0.6745 * (num_prod_hits[i] - median_y) / median_abs_dev_y) > threshold:
                    # print product_ids[product_id], dates[i], num_prod_hits[i]
                    of.write('{}\t{}\t{}\n'.format(product_ids[product_id], dates[i], num_prod_hits[i]))
        except IOError as err:
            print err


def get_outliers_with_e_score(db):
    product_ids = get_product_ids(db)
    OF = 'output/detected_outlier_modified_z_score.txt'
    of = open(OF, mode='a+')
    of.write('product_id\tdate\tnum_prod_hits\n')
    for product_id in product_ids:
        try:
            FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/data/{}.csv'.format(product_id)
            dataframe = pd.read_table(FN, sep=',')
            Q3, Q1 = np.percentile(dataframe[' number of hits'], [75, 25])
            iqr = Q3 - Q1
            median_y = np.median(dataframe[' number of hits'])
            num_prod_hits = list(dataframe[' number of hits'])
            dates = list(dataframe['date'])
            threshold = 1.75
            # print num_prod_hits
            # print dates
            for i in range(len(num_prod_hits)):
                print np.abs((num_prod_hits[i] - median_y) / iqr) > threshold
                if np.abs((num_prod_hits[i] - median_y) / iqr) > threshold:
                    # print product_ids[product_id], dates[i], num_prod_hits[i]
                    of.write('{}\t{}\t{}\n'.format(product_ids[product_id], dates[i], num_prod_hits[i]))
        except IOError as err:
            print err


def url_hits_plot():
    product_ids = get_product_ids(db)
    for product_id in product_ids:
        print product_id
        try:
            FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/data/{}.csv'.format(product_id)
            dataframe = pd.read_table(FN, sep=',')
            print dataframe
            num_prod_hits = list(dataframe[' number of hits'])
            dates = list(dataframe['date'])
            start_date = dates[0]
            start_year = str(start_date)[:4]
            start_month = str(start_date)[5:]
            dt_series = pd.date_range(datetime(int(start_year), int(start_month), 1), periods=len(dates), freq='M')
            # print dt_series
            plt.plot(dt_series, num_prod_hits)
        except IOError as err:
            print err
    plt.show()

if __name__ == "__main__":
    db = mysql.connector.connect(db='matcher', host='PC4', user='grace', passwd='2DM1YG6SrQUW4yg6')
    # product_ids = get_product_ids(db)
    write_prod_hits_to_file(db)
    # get_outliers_with_modified_z_score(db)
    url_hits_plot()
