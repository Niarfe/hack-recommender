from __future__ import division
from build_titles_within_persona_classifier_inputs import *
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn import metrics
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
import operator
import numpy as np
from sklearn import svm
import numpy as np


def get_model_from_results_file(title_filenames, results_filename, persona_type, products_to_use, test_r, balanced_training=False, balanced_test=False):

    persona_type = get_persona_type(title_filenames)
    # build Positive Title Set
    products_to_use = get_top_products(results_filename, 20)

    X, y, testX, testY = build_matrix(results_filename, persona_type, products_to_use, test_r, balanced_training,
                                      balanced_test)

    x = pd.DataFrame(X, columns=products_to_use)   # finalize training X
    y_df = pd.DataFrame(y, columns=['job titles'])
    testY_series = pd.Series(testY)
    y_array = np.asarray(y)
    Y = pd.factorize(y_array)[0]    # factorize y
    # fit model
    # print testX
    """ Logistic Regression"""
    # model = LogisticRegression(solver ='newton-cg', multi_class='multinomial')
    # model = model.fit(x, y_array.ravel())
    # preds = model.predict(testX)
    # # print testY_series
    # print pd.crosstab(testY_series, preds, rownames=['Actual Species'], colnames=['Predicted Species'])
    # print 'accuracy', accuracy_score(testY, preds, normalize=True)
    # # print model.intercept_
    # print model.coef_
    # print model.intercept_
    # return model

    """ Naive Bayes"""
    # gnb = GaussianNB()
    # mnb = MultinomialNB()
    # y_pred_gnb = gnb.fit(X, y).predict(testX)
    # print type(y_pred_gnb)
    # print 'GaussianNB'
    # print pd.crosstab(testY_series, y_pred_gnb, rownames=['Actual Species'], colnames=['Predicted Species'])
    # print accuracy_score(testY, y_pred_gnb, normalize=True)
    #
    # print 'MultinomialNB'
    # y_pred_mnb = mnb.fit(X, y).predict(testX)
    # print pd.crosstab(testY_series, y_pred_mnb, rownames=['Actual Species'], colnames=['Predicted Species'])
    # print accuracy_score(testY, y_pred_mnb, normalize=True)
    """ NN"""
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(450), random_state=1)
    model = clf.fit(X, y)
    preds = clf.predict(testX)
    print clf.coefs_
    print pd.crosstab(testY_series, preds, rownames=['Actual Species'], colnames=['Predicted Species'])
    print accuracy_score(testY, preds, normalize=True)



def write_coefficients_to_file(model, feature_names, output_filename):
    feature_dict ={}
    for i in range(len(feature_names)):
        if feature_names[i] not in feature_dict:
            feature_dict[feature_names[i]] =[]
        for j in range(len(model.coef_)):
            feature_dict[feature_names[i]].append(model.coef_[j][i])
    # print feature_dict
    # print sorted_feature_dict
    with open(output_filename, 'w') as csvfile:
        csvfile.write('product_id\tproduct_name\tCEO\tCOO\tExecutive\tExecutive Director\tExecutive Manager\n')
        for i in range(len(feature_names)):
            csvfile.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(feature_names[i], feature_dict[feature_names[i]][0], feature_dict[feature_names[i]][1], feature_dict[feature_names[i]][2], feature_dict[feature_names[i]][3], feature_dict[feature_names[i]][4]))




def main():
    results_filename = 'inputs/within_persona_classifier/cross_lob_exec/results.json';
    title_filenames = [
        'inputs/titles/cross_lob_exec.txt'
        # 'inputs/titles/dev_analyst.txt',
        # 'inputs/titles/ent_cloud_arch.txt',
        # 'inputs/titles/finance.txt',
        # 'inputs/titles/it_exec.txt',
        # 'inputs/titles/it_in_lob.txt',
        # 'inputs/titles/it_ops.txt',
        # 'inputs/titles/marketing.txt'

    ]
    healthcare_id = 142
    dates_to_filter_outdated_products = '2014-01-01'
    ######################## fetch data ###################
    # fetch_results_from_es(title_filenames, results_filename, healthcare_id, dates_to_filter_outdated_products)
    person_type = get_persona_type(title_filenames)

    # determine which products we want to use in our model
    products_to_use = get_top_products(results_filename, 100)

    # build model
    model = get_model_from_results_file(title_filenames, results_filename, person_type, products_to_use, .3, balanced_training=False, balanced_test=False)

    # get feature names from products.txt
    products_lookup = {}
    with open('inputs/products.txt', 'r') as f:
        for row in f:
            line = row.split('\t')
            products_lookup[int(line[0])] = line[1].strip()
    feature_names = [str(product_id) + '\t' + products_lookup[product_id] for product_id in products_to_use]
    # print feature_names

    # write coefficients to data/lgcoef.txt
    # write_coefficients_to_file(model, feature_names, 'outputs/within_persona_classifier/cross_lob_exec/cross_lob_exec_multi_LG_coef.txt')



    ##### other stuff #####

    # get_summary_data_from_single_title_input_file('cloud_arch_titles.txt')
    # get_summary_data_from_single_title_input_file('it_security_titles.txt')




if __name__ == "__main__":
    main()


