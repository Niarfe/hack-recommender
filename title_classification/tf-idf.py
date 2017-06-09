from sklearn.feature_extraction.text import TfidfTransformer
from build_multi_titles_classifier_inputs import *
from django.utils.encoding import smart_str
from sklearn.feature_extraction import DictVectorizer
import mysql.connector


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


def get_counts_for_products_for_personas(persona_dict, products_lookup):
    """
    :param persona_dict: a products usage dictionary,
                        {persona_type: products used by all urls in that persona were appended}
    :param products_lookup: products_lookup dictionary, {product_id: product_name}
    :return: a products counting dictionary, {persona_type: {product_id : count}... }
    """
    # get the count for each product in every persona
    prod_counts_dict = {}
    for persona_type in persona_dict.keys():
        if persona_type not in prod_counts_dict.keys():
            prod_counts_dict[persona_type] = defaultdict(int)
        for products_used_by_url in persona_dict[persona_type]:
            for product in products_used_by_url:
                prod_counts_dict[persona_type][products_lookup[product]] += 1
    return prod_counts_dict


def tf_idf_weighting(persona_dict, prod_counts_dict):
    """
    :param persona_dict: a products usage dictionary,
                        {persona_type: products used by all urls in that persona were appended}
    :param prod_counts_dict: a products counting dictionary, {persona_type: {product_id : count}... }
    :return: tf-idf weighting matrix, with dimension : # of features(products) by # of categories in dependent variable
            a list of feature(product) names and the sequence is the products sequence in tf-idf weighting matrix
    """
    v = DictVectorizer(sparse=False)
    dict_list = []
    for persona_type in persona_dict:
        dict_list.append(dict(prod_counts_dict[persona_type]))
    matrix = v.fit_transform(dict_list)
    feature_names = v.feature_names_
    transformer = TfidfTransformer()
    tfidf_weights = transformer.fit_transform(matrix).toarray().transpose()
    return tfidf_weights, feature_names


def save_tfidf_weights_to_file(tfidf_file, feature_names, tfidf_weights):
    """
    :param tfidf_file: the path to save files
    :param feature_names: a list of feature(product) names match the products sequence in tf-idf weighting matrix
    :param tfidf_weights: tf-idf weighting matrix,
                        with dimension : # of features(products) by # of categories in dependent variable
    :return: None
    """
    fw = open(tfidf_file, 'w')
    fw.write('products\tent_cloud_arch\tit_ops\tfinance\tmarketing\tit_in_lob\tit_exec\tcross_lob_exec\tdev_analyst\n')
    for i in range(tfidf_weights.shape[0]):  # loop over each products(rows)
        fw.write(
            '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(feature_names[i], tfidf_weights[i, 0], tfidf_weights[i, 1],
                                                          tfidf_weights[i, 2], tfidf_weights[i, 3], tfidf_weights[i, 4],
                                                          tfidf_weights[i, 5], tfidf_weights[i, 6],
                                                          tfidf_weights[i, 7]))
    fw.close()


if __name__ == "__main__":
    db = mysql.connector.connect(db='production', host='pdxn.cx0salcfdftt.us-west-2.rds.amazonaws.com',
                                 user='grace.zhou', passwd='BrZIoLqPsH55emt47yJy')  # provide credentials for database
    products_lookup = get_product_lookup(db)  # call function get_product_lookup to get lookup dictionary
    results_filename = 'inputs/results_sql.json'  # result file
    title_filenames = [                         # persona title files
        'inputs/titles/cross_lob_exec.txt',
        'inputs/titles/dev_analyst.txt',
        'inputs/titles/ent_cloud_arch.txt',
        'inputs/titles/finance.txt',
        'inputs/titles/it_exec.txt',
        'inputs/titles/it_in_lob.txt',
        'inputs/titles/it_ops.txt',
        'inputs/titles/marketing.txt',
    ]
    healthcare_id = 142     # type_id of products from category of vertical market
    dates_to_filter_outdated_products = '2014-01-01'     # the date to filter outdated products
    # fetch data
    # fetch_results_from_es(title_filenames, results_filename, healthcare_id, dates_to_filter_outdated_products)
    person_type = get_persona_type(title_filenames)  # call get_persona_type function to get persona type
    persona_dict = freq_analysis_inputs(results_filename, person_type)  # get a product usage dictionary
    prod_counts_dict = get_counts_for_products_for_personas(persona_dict, products_lookup)
    # put all products dictionary to a list and vectorize the dictionary to a array
    tfidf_weights, feature_names = tf_idf_weighting(persona_dict, prod_counts_dict)
    tfidf_file = 'outputs/tf_idf/tfidf_weights2.txt'
    save_tfidf_weights_to_file(tfidf_file, feature_names, tfidf_weights)
