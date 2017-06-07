from build_multi_titles_classifier_inputs import *
import pandas as pd
from sklearn import metrics
from sklearn.neural_network import MLPClassifier
import operator
from sklearn.metrics import accuracy_score
import numpy as np


def get_model_from_results_file(title_filenames, results_filename, persona_type, products_to_use, test_r, balanced_training=False, balanced_test=False):
    persona_type = get_persona_type(title_filenames)
    # output layer
    output_layer = len(persona_type.keys())
    print output_layer
    # build Positive Title Set
    products_to_use = get_top_products(results_filename, 20)

    X, y, testX, testY = build_matrix(results_filename, persona_type, products_to_use, test_r, balanced_training,
                                      balanced_test)
    # input layer
    input_layer = len(X[0])
    print input_layer
    x = pd.DataFrame(X, columns=products_to_use)   # finalize training X
    y_df = pd.DataFrame(y, columns=['job titles'])
    testY_series = pd.Series(testY)
    y_array = np.asarray(y)
    y_names = np.asarray(persona_type.keys())
    Y = pd.factorize(y_array)[0]    # finalize training Y
    # fit model
    # hidden_layer = tuple([np.mean(input_layer, output_layer)])
    # print hidden_layer
    clf = MLPClassifier(solver='lbfgs', alpha=1e-5, hidden_layer_sizes=(450), random_state = 1)
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
        feature_dict[feature_names[i]] = model.coef_[0][i]
    sorted_feature_dict = sorted(feature_dict.items(), key=operator.itemgetter(1),reverse=True)
    # print feature_dict
    # print sorted_feature_dict
    with open(output_filename, 'w') as report_file:
        for i in range(len(sorted_feature_dict)):
            report_file.write(sorted_feature_dict[i][0] + '\t' + str(sorted_feature_dict[i][1]) + '\n')

    pprint(sorted_feature_dict[:7])
    pprint(sorted_feature_dict[-7:])

def main():
    results_filename = 'inputs/results.json';
    title_filenames = [
        'inputs/titles/dev_analyst.txt',
        'inputs/titles/ent_cloud_arch.txt',
        'inputs/titles/finance.txt',
        'inputs/titles/it_exec.txt',
        'inputs/titles/it_in_lob.txt',
        'inputs/titles/it_ops.txt',
        'inputs/titles/marketing.txt',
        'inputs/titles/cross_lob_exec.txt'
    ]
    ######################## fetch data ###################
    # fetch_results_from_es(title_filenames, results_filename)
    person_type = get_persona_type(title_filenames)

    # determine which products we want to use in our model
    products_to_use = get_top_products('inputs/results.json', 50)

    # build model
    model = get_model_from_results_file(title_filenames, results_filename, person_type, products_to_use, .3, balanced_training=False, balanced_test=False)

    # get feature names from products.txt
    products_lookup = {}
    with open('inputs/products.txt', 'r') as f:
        for row in f:
            line = row.split('\t')
            products_lookup[int(line[0])] = line[1].strip()
    feature_names = [str(product_id) + '\t' + products_lookup[product_id] for product_id in products_to_use]




    ##### other stuff #####

    # get_summary_data_from_single_title_input_file('cloud_arch_titles.txt')
    # get_summary_data_from_single_title_input_file('it_security_titles.txt')

    # get metrics
    # all_prod_dict = get_counts_by_product(results_filename)
    # with open('results.json') as f:
    #     total_count = sum(1 for _ in f)


if __name__ == "__main__":
    main()


