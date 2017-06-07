from build_title_classifier_inputs import *
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn import linear_model
import operator

def get_summary_data_from_single_title_input_file(title_input_filename):
    fetch_results_from_es(title_input_filename)
    dict, count = get_product_hits_by_title('results_999999999.json')
    return dict, count

def get_model_from_results_file(results_filename, positive_title_set_filename, products_to_use, test_r, balanced_training=False, balanced_test=False):
    # build Positive Title Set
    positive_title_set = []
    with open(positive_title_set_filename, 'r') as f:
        for row in f:
            positive_title_set.append(row.strip())

    X, y, testX, testY = build_matrix('results.json', positive_title_set, products_to_use, test_r, balanced_training,
                                      balanced_test)
    x = pd.DataFrame(X, columns=products_to_use)
    # print x
    Y = pd.DataFrame(y, columns=['job_title'])
    model = LogisticRegression()
    model = model.fit(x, Y)

    predicted = model.predict(testX)
    print metrics.confusion_matrix(testY, predicted)
    print metrics.accuracy_score(testY, predicted)
    print model.intercept_

    return model


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

    results_filename = 'results.json';
    title_filenames = [
        'inputs/titles/dev_analyst.txt'
        'inputs/titles/ent_cloud_arch.txt'
        'inputs/titles/finance.txt'
        'inputs/titles/it_exec.txt'
        'inputs/titles/it_in_lob.txt'
        'inputs/titles/it_ops.txt'
        'inputs/titles/marketing.txt'
    ]

    # build results.json from ElasticSearch
    fetch_results_from_es(title_filenames, results_filename)

    # determine which products we want to use in our model
    products_to_use = get_top_products('results.json', 100)

    # build model
    model = get_model_from_results_file(results_filename, 'inputs/titles/marketing.txt', products_to_use, .3, balanced_training=False, balanced_test=False)

    # get feature names from products.txt
    products_lookup = {}
    with open('inputs/products.txt', 'r') as f:
        for row in f:
            line = row.split('\t')
            products_lookup[int(line[0])] = line[1].strip()
    feature_names = [str(product_id) + '\t' + products_lookup[product_id] for product_id in products_to_use]

    # write coefficients to data/lgcoef.txt
    # write_coefficients_to_file(model, feature_names, 'outputs/lg_coef2.txt')




    ##### other stuff #####

    # get_summary_data_from_single_title_input_file('cloud_arch_titles.txt')
    # get_summary_data_from_single_title_input_file('it_security_titles.txt')

    # get metrics
    # all_prod_dict = get_counts_by_product(results_filename)
    # with open('results.json') as f:
    #     total_count = sum(1 for _ in f)

if __name__ == "__main__":
    main()


