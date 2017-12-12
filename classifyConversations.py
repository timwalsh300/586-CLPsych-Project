import csv
import numpy as np
import scipy.sparse as sparse
import sklearn.model_selection
import sklearn.metrics
import sklearn.svm
import sklearn.feature_extraction

def extract_initial_flagged(file):
    # pick those are initially flagged
    initial_flagged = [row for row in file if row[0] == 'flagged']
    # label according to the final label, if green as True, stays flagged as False
    for row in initial_flagged:
        if row[2] == 'green': row[2] = 1
        else: row[2] = 0
    # turn into numpy array
    initial_flagged = np.array(initial_flagged)
    # split post, label, extra features
    posts = initial_flagged[:, 1]
    labels = initial_flagged[:, 2]
    labels = labels.astype(np.int)
    extra_features = initial_flagged[:, 3:]
    extra_features = extra_features.astype(np.float32)
    return labels, posts, extra_features

def extract_initial_green(file):
    # pick those are initially green
    initial_green = [row for row in file if row[0] == 'green']
    # label according to the final label, if flagged as True, stays green as False
    for row in initial_green:
        if row[2] == 'flagged': row[2] = 1
        else: row[2] = 0
    # turn into numpy array
    initial_green = np.array(initial_green)
    # split post, label, extra features
    posts = initial_green[:, 1]
    labels = initial_green[:, 2]
    labels = labels.astype(np.int)
    extra_features = initial_green[:, 3:]
    extra_features = extra_features.astype(np.float32)
    return labels, posts, extra_features

def cat_to_int(cat):
    for i in range(0, len(cat)):
        if cat[i] == 'flagged':
            cat[i] = 1
        else:
            cat[i] = 0
    return cat

def extract_all(file):
    # turn into numpy array
    file = np.array(file)
    # split
    initials = file[:,0]
    initials = cat_to_int(initials)[:,None]
    posts = file[:,1]
    labels = file[:,2]
    labels = cat_to_int(labels)
    labels = labels.astype(np.int)
    extra_features = file[:,3:]
    extra_features = np.hstack((initials, extra_features))
    extra_features = extra_features.astype(np.float32)
    return labels, posts, extra_features

for n in range(1, 15):
    with open('./stopwordsRemoved/' + str(n) + 'dayConversations.txt') as f:
        reader = csv.reader(f, delimiter='\t')
        file = list(reader)

    labels, posts, extra_features = extract_all(file)

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
            analyzer='word',
            ngram_range=(1,3)
        )
        ## extract tf-idf weights from training and test set, weights are only learned/fitted on training set
        tfidf_train = extractor.fit_transform(posts_train)
        tfidf_test = extractor.transform(posts_test)

        # stack extra features to tfidf
        feature_train = sparse.hstack((tfidf_train, extra_features_train))
        feature_test = sparse.hstack((tfidf_test, extra_features_test))

        # train and test a classifier; in this case, we use a linear SVM
        cl = sklearn.svm.SVC(kernel='linear')
        cl.fit(feature_train, labels_train)
        labels_pred = cl.predict(feature_test)

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