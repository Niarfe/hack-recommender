from __future__ import division
from build_multi_titles_classifier_inputs import *
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
import numpy as np


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


def get_model_from_results_file(title_filenames, results_filename, persona_type, products_to_use, test_r, balanced_training=False, balanced_test=False):
    """this function split results_filename into training set and test set, return model and print out
        the confusion matrix"""
    persona_type = get_persona_type(title_filenames)
    # build Positive Title Set
    products_to_use = get_top_products(results_filename, 20)

    X, y, testX, testY = build_matrix(results_filename, persona_type, products_to_use, test_r, balanced_training,
                                      balanced_test)
    x = pd.DataFrame(X, columns=products_to_use)   # finalize training X
    y_df = pd.DataFrame(y, columns=['job titles'])
    testY_series = pd.Series(testY)
    y_array = np.asarray(y)
    y_names = np.asarray(persona_type.keys())
    Y = pd.factorize(y_array)[0]    # factorize y
    # fit model
    model = LogisticRegression(solver='newton-cg', multi_class='multinomial')
    model = model.fit(x, y_array.ravel())
    preds = model.predict(testX)
    # print pd.crosstab(testY_series, preds, rownames=['Actual Species'], colnames=['Predicted Species'])
    # print 'accuracy', accuracy_score(testY, preds, normalize=True)
    """test category names"""
    # print len(model.coef_)
    # print len(model.coef_[0])
    # print len(testX)
    # print len(testX[0])
    # db = mysql.connector.connect(db='production', host='pdxn.cx0salcfdftt.us-west-2.rds.amazonaws.com',
    #                              user='grace.zhou', passwd='BrZIoLqPsH55emt47yJy')
    # products_lookup = get_product_lookup(db)
    # # coefficient array dimension is : numbers of categories in y (8) by numbers of features(products)
    # coef = np.asanyarray(model.coef_)
    # test1 = np.asanyarray(testX[0:10]).transpose()
    # caculation = np.dot(coef, test1)
    # print len(caculation)  # number of rows
    # print len(caculation[0])  # number of columns
    # print model.intercept_
    #
    # for i in range(len(products_to_use)):
    #     product_name = products_lookup[products_to_use[i]]
    #     print '+++++++++++++++++'
    #     print product_name
    #     print coef[:, i]

    # with open('outputs/multinomial_LG/test_sql_multi_LG_coef.txt', 'w') as csvfile:
    #     csvfile.write(
    #         'product_name\tcross_lob_exec\tdev_analyst\tent_cloud_arch\tfinance\tit_exec\tit_in_lob\tit_ops\tmarketing\n')
    #     for i in range(len(products_to_use)):  # loop over 994 products
    #         product_name = products_lookup[products_to_use[i]]
    #         # print '+++++++++++++++++++++++++++'
    #         # print product_name
    #         # print coef[:, i]
    #         # print type(coef[:, i])
    #         # print 'len', len(coef[:, i])
    #         csvfile.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_name, coef[0, i], coef[1, i],
    #                                                                     coef[2, i], coef[3, i], coef[4, i], coef[5, i],
    #                                                                     coef[6, i], coef[7, i]))

    # for i in range(len(test1[0])): # loop over the columns 8 columns
    #     print ' ++++++++++++++++++++++++++++++++++++++++ '
    #     print 'new obs'
    #     print 'getting cauculation', caculation[:, i]
    #     print 'delete intercept', caculation[:, i] + np.asanyarray(model.intercept_)
    #     print 'model predicted', preds[i]
    #     for j in range(len(test1)): # loop over the rows  994 products
    #         if test1[j][i] == 1:
    #             print 'check product usage', products_lookup[products_to_use[j]]
    #             print 'coef', coef[:, j]
    return model

#
def write_coefficients_to_file(model, products_to_use, products_lookup, output_filename):
    """ This function is for Logistic Regression, write the coefficient from Logistic Regression into a file"""
    coef = np.asanyarray(model.coef_)
    # print coef
    with open(output_filename, 'w') as csvfile:
        csvfile.write(
                    'product_name\tcross_lob_exec\tdev_analyst\tent_cloud_arch\tfinance\tit_exec\tit_in_lob\tit_ops\tmarketing\n')
        for i in range(len(products_to_use)):  # loop over 994 products
            product_name = products_lookup[products_to_use[i]]
            #         # print '+++++++++++++++++++++++++++'
            #         # print product_name
            #         # print coef[:, i]
            #         # print type(coef[:, i])
            #         # print 'len', len(coef[:, i])
            csvfile.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(product_name, coef[0, i], coef[1, i],
                                                                        coef[2, i], coef[3, i], coef[4, i], coef[5, i],
                                                                        coef[6, i], coef[7, i]))


def main():
    """ set up path for input data and get results from the model"""
    results_filename = 'inputs/results_sql.json'  # result file
    # files with titles for each persona
    title_filenames = [
        'inputs/titles/cross_lob_exec.txt',
        'inputs/titles/dev_analyst.txt',
        'inputs/titles/ent_cloud_arch.txt',
        'inputs/titles/finance.txt',
        'inputs/titles/it_exec.txt',
        'inputs/titles/it_in_lob.txt',
        'inputs/titles/it_ops.txt',
        'inputs/titles/marketing.txt'
    ]
    # type id that from the category of vertical market
    healthcare_id = 142
    # the date to filter outdated products
    dates_to_filter_outdated_products = '2014-01-01'
    """ fetch data """
    # fetch_results_from_es(title_filenames, results_filename, healthcare_id, dates_to_filter_outdated_products)
    # get the persona type from title files
    person_type = get_persona_type(title_filenames)
    # determine which products we want to use in our model
    products_to_use = get_top_products(results_filename, 100)
    # build model
    model = get_model_from_results_file(title_filenames, results_filename, person_type, products_to_use, .3, balanced_training=False, balanced_test=False)
    # get feature names(product names) from products.txt
    db = mysql.connector.connect(db='production', host='pdxn.cx0salcfdftt.us-west-2.rds.amazonaws.com',
                                 user='grace.zhou', passwd='BrZIoLqPsH55emt47yJy')
    products_lookup = get_product_lookup(db)
    print products_lookup[16146]
    feature_names = [str(product_id) + '\t' + products_lookup[product_id] for product_id in products_to_use]
    write_coefficients_to_file(model,  products_to_use, products_lookup, 'outputs/multinomial_LG/wrong_multi_LG_coef.txt')

if __name__ == "__main__":
    main()


