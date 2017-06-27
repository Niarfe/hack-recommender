import numpy as np
import pandas as pd
from django.utils.encoding import smart_str
import mysql.connector
import statsmodels.api as sm
from sklearn import linear_model
import matplotlib.pyplot as plt

def get_product_lookup(db):
    """
    :param db: the credentials for connecting pdxn, use pdxn instead of pc4 is because pdxn has latest table,
            pc4 is outdated

    :return: products_lookup dictionary, {product_id: product_name}
    """
    products_lookup = {}
    c = db.cursor(buffered=True)
    query = ("""
        SELECT id, name FROM production.products;
        """)
    iterable = c.execute(query, multi=True)
    for item in iterable:
        for result in item.fetchall():
            product_id = result[0]
            product_name = smart_str(result[1])
            if product_id not in products_lookup:
                products_lookup[product_id] = []
            products_lookup[product_id] = product_name
    return products_lookup



def get_outliers():
    product_ids = get_product_lookup(db)
    OF = 'output/detected_outlier2.txt'
    of = open(OF, mode='a+')
    of.write('product_id\tdate\tnum_prod_hits\n')
    for product_id in product_ids:
        # print product_id
        try:
            FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/duns/{}.txt'.format(product_id)
            dataframe = pd.read_table(FN, sep='\t')
            Q3, Q1 = np.percentile(dataframe['duns_product_hits'], [75, 25])
            iqr = Q3 - Q1
            upper_limit = Q3 + 1.5 * iqr
            lower_limit = Q1 - 1.5 * iqr
            num_prod_hits = list(dataframe['duns_product_hits'])
            dates = list(dataframe['date'])
            # print num_prod_hits
            # print dates
            for i in range(len(num_prod_hits)):
                # print num_prod_hits[i] > upper_limit or num_prod_hits[i] < lower_limit
                # print num_prod_hits[i]
                # print upper_limit
                # print lower_limit
                # if (num_prod_hits[i] > upper_limit) or (num_prod_hits[i] < lower_limit):
                if num_prod_hits[i] > upper_limit:
                    # print product_ids[product_id], dates[i], num_prod_hits[i]
                    of.write('{}\t{}\t{}\n'.format(product_ids[product_id], dates[i], num_prod_hits[i]))
        except IOError as err:
            print err
        except ValueError as errs:
            print product_id, errs


def get_outliers_with_z_score():
    product_ids = get_product_lookup(db)
    OF = 'output/detected_outlier_z_score.txt'
    of = open(OF, mode='a+')
    of.write('product_id\tdate\tnum_prod_hits\n')
    for product_id in product_ids:
        try:
            FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/duns/{}.txt'.format(product_id)
            dataframe = pd.read_table(FN, sep='\t')
            threshold = 3
            mean_y = np.mean(dataframe['duns_product_hits'])
            stdev_y = np.std(dataframe['duns_product_hits'])
            num_prod_hits = list(dataframe['duns_product_hits'])
            dates = list(dataframe['date'])
            # print num_prod_hits
            # print dates
            for i in range(len(num_prod_hits)):
                print np.abs((num_prod_hits[i] - mean_y)/stdev_y) > threshold
                if np.abs((num_prod_hits[i] - mean_y)/stdev_y) > threshold:
                # if (num_prod_hits[i] - mean_y) / stdev_y > threshold:
                    # print product_ids[product_id], dates[i], num_prod_hits[i]
                    of.write('{}\t{}\t{}\n'.format(product_ids[product_id], dates[i], num_prod_hits[i]))
        except IOError as err:
            print err


def get_outliers_with_modified_z_score():
    product_ids = get_product_lookup(db)
    OF = 'output/detected_outlier_modified_z_score.txt'
    of = open(OF, mode='a+')
    of.write('product_id\tdate\tnum_prod_hits\n')
    for product_id in product_ids:
        try:
            FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/duns/{}.txt'.format(product_id)
            dataframe = pd.read_table(FN, sep='\t')
            threshold = 3.5
            median_y = np.median(dataframe['duns_product_hits'])
            num_prod_hits = list(dataframe['duns_product_hits'])
            dates = list(dataframe['date'])
            median_abs_dev_y = np.median([np.abs(y - median_y) for y in num_prod_hits])
            # print num_prod_hits
            # print dates
            for i in range(len(num_prod_hits)):
                print np.abs(0.6745 * (num_prod_hits[i] - median_y) / median_abs_dev_y) > threshold
                if np.abs(0.6745 * (num_prod_hits[i] - median_y) / median_abs_dev_y) > threshold:
                # if 0.6745 * (num_prod_hits[i] - median_y) / median_abs_dev_y > threshold:
                    # print product_ids[product_id], dates[i], num_prod_hits[i]
                    of.write('{}\t{}\t{}\n'.format(product_ids[product_id], dates[i], num_prod_hits[i]))
        except IOError as err:
            print err


def get_outliers_with_e_score():
    product_ids = get_product_lookup(db)
    OF = 'output/detected_outlier_e_score.txt'
    of = open(OF, mode='a+')
    of.write('product_id\tdate\tnum_prod_hits\n')
    for product_id in product_ids:
        try:
            FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/duns/{}.txt'.format(product_id)
            dataframe = pd.read_table(FN, sep='\t')
            Q3, Q1 = np.percentile(dataframe['duns_product_hits'], [75, 25])
            iqr = Q3 - Q1
            median_y = np.median(dataframe['duns_product_hits'])
            num_prod_hits = list(dataframe['duns_product_hits'])
            dates = list(dataframe['date'])
            threshold = 1.75
            # print num_prod_hits
            # print dates
            for i in range(len(num_prod_hits)):
                # print np.abs((num_prod_hits[i] - median_y) / iqr) > threshold
                if np.abs((num_prod_hits[i] - median_y) / iqr) > threshold:
                # if (num_prod_hits[i] - median_y) / iqr > threshold:
                    # print product_ids[product_id], dates[i], num_prod_hits[i]
                    of.write('{}\t{}\t{}\n'.format(product_ids[product_id], dates[i], num_prod_hits[i]))
        except IOError as err:
            print err
        except ValueError as errs:
            print product_id, errs


def outlier_detection_with_regression():
    OF = 'output/detected_outlier_regression.txt'
    of = open(OF, mode='a+')
    of.write('product_id\tdate\tnum_prod_hits\n')
    for product_id in product_ids:
        print '+++++++++++++++++'
        print product_id
        try:
            FN = '/Users/gracezhou/PycharmProjects/data_ops/detect_anomalies/duns/{}.txt'.format(product_id)
            df = pd.read_table(FN, sep='\t')
            sorted_df = df.sort(['date'])
            dates = list(sorted_df['date'])
            duns_counts = list(sorted_df['duns_product_hits'])
            for i in range(len(dates) - 1):
                if all([dates[i + 1] - dates[i] > 1, dates[i + 1] - dates[i] < 12]):
                    # print dates[i]
                    # print dates[i+1]
                    gap = dates[i + 1] - dates[i]
                    gap_list = sorted([dates[i] + diff for diff in range(1, gap)], reverse=True)
                    # print gap_list
                    gap_zeros = [0] * (gap - 1)
                    # print gap_zeros
                    for j in range(len(gap_list)):
                        dates.insert(i + 1, gap_list[j])
                        duns_counts.insert(i + 1, gap_zeros[j])
            x = range(len(dates))
            # print dates
            regression = sm.OLS(x, duns_counts).fit()
            test = regression.outlier_test()
            outliers = [[dates[i], duns_counts[i]] for i, t in enumerate(test) if t[2] < 0.5]
            # print 'Outlier', outliers
            if len(outliers) != 0:
                for i in range(len(outliers)):
                    of.write("{}\t{}\t{}\n".format(product_ids[product_id], outliers[i][0], outliers[i][1]))
                    # plt.plot(dates, duns_counts)
        except IOError as err:
            print err
        except ValueError as errs:
            print product_id, errs

if __name__ == "__main__":
    db = mysql.connector.connect(db='production', host='pdxn.cx0salcfdftt.us-west-2.rds.amazonaws.com',
                                 user='grace.zhou', passwd='BrZIoLqPsH55emt47yJy')
    # get_outliers()
    product_ids = get_product_lookup(db)
    outlier_detection_with_regression()