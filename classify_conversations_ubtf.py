import csv
import numpy as np
import scipy.sparse as sparse
import sklearn.model_selection
import sklearn.metrics
import sklearn.svm
import sklearn.feature_extraction
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer

import cutils

for n in range(1, 15):
    with open('./con/' + str(n) + 'dayConversations.txt') as f:
        reader = csv.reader(f, delimiter='\t')
        file = list(reader)

    labels, posts, extra_features = cutils.extract_all(file)

    # set up cross fold validation
    folds = sklearn.model_selection.StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=None
    )

    # initialize precision, recall, F1 scores, and accuracy across folds
    k_p, k_r, k_f1, k_acc = [], [], [], []

    # k folds
    for i, (train, test) in enumerate(folds.split(posts, labels), start=1):
        # print('Fold {:,}...'.format(i))

        # split training and test data
        labels_train, labels_test = labels[train], labels[test]
        posts_train, posts_test = posts[train], posts[test]
        extra_features_train, extra_features_test = extra_features[train], extra_features[test]

        # extract tf-idf
        ## initialize extractor
        extractor = sklearn.feature_extraction.text.TfidfVectorizer(
            min_df=4,
            use_idf=True,
            smooth_idf=True,
            sublinear_tf=True,
            norm='l2',
            analyzer=cutils.LemmaTokenizer(),
            ngram_range=(1,1)
        )
        ## extract tf-idf weights from training and test set, weights are only learned/fitted on training set
        tfidf_train = extractor.fit_transform(posts_train)
        tfidf_test = extractor.transform(posts_test)

        # stack extra features to tfidf
        feature_train = sparse.hstack((tfidf_train, extra_features_train))
        feature_test = sparse.hstack((tfidf_test, extra_features_test))

        # train and test a classifier; in this case, we use a linear SVM
        cl = sklearn.svm.SVC(kernel='linear', probability=True)
        cl.fit(feature_train, labels_train)
        labels_pred_proba = cl.predict_proba(feature_test)
        labels_pred = cutils.round_up(labels_pred_proba)

        # save for test set (one of the folds) true labels, predicted labels, and body
        tpb = np.vstack((labels_test, labels_pred, labels_pred_proba[:,1], posts_test))
        tpb = tpb.transpose()
        tpb_list = tpb.tolist()
        file_name = 'ccon_ubtf_day_' + str(n) + '_fold_' + str(i) + '.tsv'
        with open(file_name, 'w') as file:
            for row in tpb_list:
                line = row[0] + '\t' + row[1] + '\t' + row[2] + '\t' + row[3] + '\n'
                file.write(line)
        file.close()

        # get accuracy, precision, recall, and F1 score on this fold
        acc = sklearn.metrics.accuracy_score(labels_test, labels_pred)
        p, r, f1, _ = sklearn.metrics.precision_recall_fscore_support(labels_test, labels_pred)

        # save to calculate average performance across folds
        k_p.append(np.average(p))
        k_r.append(np.average(r))
        k_f1.append(np.average(f1))
        k_acc.append(acc)

    # print performance
    k_p, k_r, k_f1, k_acc = map(np.mean, (k_p, k_r, k_f1, k_acc))
    print(str(n) + ' day conversations: ')
    print(
        '\tPrecision: {:2.2%}\n\tRecall: {:2.2%}\n\tF Score: {:2.2%}\n\tAccuracy: {:2.2%}\n'
        ''.format(k_p, k_r, k_f1, k_acc)
    )