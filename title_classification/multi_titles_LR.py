from __future__ import division
from build_multi_titles_classifier_inputs import *
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
import numpy as np


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
    print pd.crosstab(testY_series, preds, rownames=['Actual Species'], colnames=['Predicted Species'])
    print 'accuracy', accuracy_score(testY, preds, normalize=True)
    return model


def write_coefficients_to_file(model, feature_names, output_filename):
    """ This function is for Logistic Regression, write the coefficient from Logistic Regression into a file"""
    feature_dict ={}
    for i in range(len(feature_names)):
        if feature_names[i] not in feature_dict:
            feature_dict[feature_names[i]] =[]
        for j in range(len(model.coef_)):
            feature_dict[feature_names[i]].append(model.coef_[j][i])
    # print feature_dict
    # print sorted_feature_dict
    with open(output_filename, 'w') as csvfile:
        csvfile.write('product_id\tproduct_name\tcross_lob_exec\tdev_analyst\tent_cloud_arch\tfinance\tit_exec\tit_in_lob\tit_ops\tmarketing\n')
        for i in range(len(feature_names)):
            csvfile.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(feature_names[i], feature_dict[feature_names[i]][0], feature_dict[feature_names[i]][1], feature_dict[feature_names[i]][2], feature_dict[feature_names[i]][3], feature_dict[feature_names[i]][4], feature_dict[feature_names[i]][5], feature_dict[feature_names[i]][6], feature_dict[feature_names[i]][7]))


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
        'inputs/titles/marketing.txt',
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
    products_lookup = {}
    with open('inputs/products.txt', 'r') as f:
        for row in f:
            line = row.split('\t')
            products_lookup[int(line[0])] = line[1].strip()
    feature_names = [str(product_id) + '\t' + products_lookup[product_id] for product_id in products_to_use]
    write_coefficients_to_file(model, feature_names, 'outputs/multinomial_LG/sql_multi_LG_coef.txt')

if __name__ == "__main__":
    main()


