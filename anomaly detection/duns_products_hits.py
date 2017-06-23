import mysql.connector
from django.utils.encoding import smart_str


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


def query_duns(db, product_ids):
    """

    :param db: mysql database credentials
    :param product_ids: a list of all product id in our database
    :return: a dictionary like {product_id : { yearmonth : [duns...]} }
    """
    c = db.cursor(buffered=True)
    query = ("""
        SELECT h.product_id, h.dates, cd.duns FROM matcher.hits h JOIN integration.cid_duns cd ON h.cid = cd.cid
        where product_id IN {};
        """)
    # iterable = c.execute(query.format(tuple(product_ids)), multi=True)
    iterable = c.execute(query.format(tuple(product_ids)), multi=True)
    print query.format(tuple(product_ids))
    duns_dict = {}
    for item in iterable:
        for result in item.fetchall():
            product_id = result[0]
            dates = result[1].split(',')
            # print dates
            duns = result[2]
            if product_id not in duns_dict:
                duns_dict[product_id] = {}
            for date in dates:
                yearmonth = date[:6]
                if yearmonth not in duns_dict[product_id]:
                    duns_dict[product_id][yearmonth] = []
                duns_dict[product_id][yearmonth].append(duns)
    print duns_dict.keys()
    # print duns_dict[duns_dict.keys()[1]]
    return duns_dict


def save_duns_prod_hits():
    """

    :return: save all duns count in a file with the product id as the txt name
    """
    duns_dict = query_duns(db, product_ids)
    for product_id in duns_dict:
        file = "../detect_anomalies/duns/{}.txt".format(product_id)
        fw = open(file, 'w')
        fw.write("date\tduns_product_hits\n")
        for date in duns_dict[product_id]:
            duns_counts = len(set(duns_dict[product_id][date]))  # count the unique duns
            fw.write("{}\t{}\n".format(date, duns_counts))
    fw.close()



if __name__ == "__main__":
    db = mysql.connector.connect(db='matcher', host='pc4', user='grace', passwd='2DM1YG6SrQUW4yg6')
    db_pdxn = mysql.connector.connect(db='production', host='pdxn.cx0salcfdftt.us-west-2.rds.amazonaws.com',
                                    user='grace.zhou', passwd='BrZIoLqPsH55emt47yJy')
    products_lookup = get_product_lookup(db_pdxn)
    product_ids = products_lookup.keys()
    # query_duns(db, product_ids)
    save_duns_prod_hits()