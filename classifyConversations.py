import csv
import numpy as np
import sklearn.model_selection
import sklearn.metrics
import sklearn.svm
import sklearn.feature_extraction

for nnn in range(1, 15):

    # read in id_label_body
    with open(str(nnn) + 'dayConv-thresholdInitialState.txt') as f:
        reader = csv.reader(f, delimiter='\t')
        l_c = list(reader)

    # turn id into int, turn label into boolean,
    # green = 0 = False, non-green = 1 = True
    for row in l_c:
        if row[0] == '1':
            row[0] = True
        else:
            row[0] = False

    # turn i_l_b into numpy array and extract labels and posts
    lc = np.array(l_c)
    labels = lc[:,0]
    posts = lc[:,1]

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
        print('Fold {:,}...'.format(i))
        # split training and test data
        posts_train, posts_test = posts[train], posts[test]
        labels_train, labels_test = labels[train], labels[test]
        # extract tf-idf; this module can also extract word ngrams see documentation at
        # http://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html
        extractor_words = sklearn.feature_extraction.text.TfidfVectorizer(
            min_df=4,
            use_idf=True,
            smooth_idf=True,
            sublinear_tf=True,
            norm='l2',
            analyzer='word'
        )
        # extract tf-idf weights from training and test data
        # you call fit_transform on the training data, so that
        # tf-idf weights are learned only on training data,
        # not on test data. The test data is only trainsformed
        posts_train = extractor_words.fit_transform(posts_train)
        posts_test = extractor_words.transform(posts_test)
        # train and test a classifier; in this case, we use a linear SVM
        cl = sklearn.svm.SVC(kernel='linear')
        cl.fit(posts_train, labels_train)
        labels_pred = cl.predict(posts_test)
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
    print("n = " + str(nnn))
    print(
        '\nPrecision: {:2.2%}\nRecall: {:2.2%}\nF Score: {:2.2%}\nAccuracy: {:2.2%}\n'
        ''.format(k_p, k_r, k_f1, k_acc)
    )
