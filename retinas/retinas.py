from collections import defaultdict
import matplotlib.pyplot as plt
import csv


def import_from_data_file(unique_id):
    with open(data_source, 'r') as source:
        csvfile = csv.reader(source)
        for line in csvfile:
            binary = line[6]
            if unique_id == line[0].strip():
                row_els = [word.lower().strip() for word in line[8].split(' ')]
                return binary, row_els
            else:
                continue
    print "URL NOT FOUND IN SOURCE FILE"
    return 0, []


def import_words_fingerprints(file):
    wf_dict = {}
    fr = open(file, 'r')
    for line in fr.readlines():
        ls = line.strip().split(',')
        word = ls[0]
        index = ls[1:]
        wf_dict[word] = index
    return wf_dict


def word_counts(x_l, x_u, y_l, y_u):
    for id in range(265, 266):
        idx_stack_count = defaultdict(int)
        unique_id = str(id)
        all_count = 0
        # print unique_id
        binary, words = import_from_data_file(unique_id)
        # print words
        word_fp = import_words_fingerprints(word_fingerprints)
        for wd in words:
            try:
                # print wd
                count = 0
                idx = word_fp[wd]
                for i in range(0, len(idx), 2):
                    # print idx[i], idx[i+1]
                    if x_l <= int(idx[i]) <= x_u:
                        # print idx[i]
                        if y_l <= int(idx[i+1]) <= y_u:
                            # print wd
                            count += 1
                # print all_count
                all_count += count
            except:
                pass
                # print wd, 'not in the vocabulary!'
        return all_count


def plot_retinas_for_each_wd():
    for id in range(265, 266):
        idx_stack_count = defaultdict(int)
        unique_id = str(id)
        print unique_id
        binary, words = import_from_data_file(unique_id)
        print words
        word_fp = import_words_fingerprints(word_fingerprints)
        for wd in words:
            try:
                arrx = []
                arry = []
                idx = word_fp[wd]
                for i in range(0, len(idx), 2):
                    arrx.append(idx[i])
                    arry.append(idx[i + 1])
                    pair = (idx[i], idx[i + 1])
                    idx_stack_count[pair] += 1
                fig = plt.figure(figsize=(14, 14))
                ax = fig.add_subplot(1, 1, 1)
                ax.scatter(arrx, arry)
                plt.axis([0, 128, 0, 128])
                plt.grid()
                plt.title("unique_word: {}".format(wd))
                plt.savefig(
                    "/Users/gracezhou/PycharmProjects/data_ops/medical_mrd/data/fingerprints/words/{}.png".format(wd))
                # time.sleep(5)
                plt.clf()
            except:
                # pass
                print wd, 'not in the vocabulary!'
    return unique_id, idx_stack_count


def plot_fp(threshold):
    arrx = []
    arry = []
    id, idx_hp = plot_retinas_for_each_wd()
    index = idx_hp.keys()
    for pair in index:
        arrx.append(pair[0])
        arry.append(pair[1])

        fig = plt.figure(figsize=(14, 14))
        ax = fig.add_subplot(1, 1, 1)
        ax.scatter(arrx, arry)
        plt.axis([0, 128, 0, 128])
        plt.grid()
        plt.title("unique_id: {}".format(id))
        plt.savefig(
            "/Users/gracezhou/PycharmProjects/data_ops/medical_mrd/data/fingerprints/docs/{}_full_fp.png".format(
                id))
    x = []
    y = []
    for key in idx_hp.keys():
        if idx_hp[key] > threshold:
            x.append(key[0])
            y.append(key[1])
    fig = plt.figure(figsize=(14, 14))
    ax = fig.add_subplot(1, 1, 1)
    ax.scatter(x, y)
    plt.axis([0, 128, 0, 128])
    plt.grid()
    plt.title("unique_id: {}".format(id))
    plt.savefig(
        "/Users/gracezhou/PycharmProjects/data_ops/medical_mrd/data/fingerprints/docs/{}_fp.png".format(id))


if __name__ == "__main__":
    data_source = '/Users/gracezhou/PycharmProjects/data_ops/medical_mrd/data/medical_docs_with_id.csv'
    word_fingerprints = '/Users/gracezhou/PycharmProjects/data_ops/medical_mrd/data/word_fingerprints.csv'
    threshold = 5
    # plot_fp(threshold)
    all_count = word_counts(0, 20, 0, 20)
    print all_count

    print "DONE"


