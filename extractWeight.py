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

def print_top(n, coefficients, feature_names):
    weights = coefficients[0, :].toarray()
    weights = weights.tolist()
    weights = weights[0]
    weights = np.array(weights)
    top = np.argsort(weights)[:n]
    length = len(top)
    for i in range(0, length):
        index = top[i]
        f_n = feature_names[index]
        w = coefficients[0,index]
        print(f_n + "  ==  " + str(w))
    return

def print_flr(n, coefficients, feature_names):
    weights = coefficients[0, :].toarray()
    weights = weights.tolist()
    weights = weights[0]
    weights = np.array(weights)
    top = np.argsort(weights)[n:]
    length = len(top)
    for i in range(0, length):
        index = top[i]
        f_n = feature_names[index]
        w = coefficients[0,index]
        print(f_n + "  ==  " + str(w))
    return



# read in id_label_body
with open('./withExtraFeatures/' + '14dayConversations.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    file = list(reader)

labels, posts, extra_features = extract_all(file)

# extract tf-idf from from data
extractor = sklearn.feature_extraction.text.TfidfVectorizer(
    min_df=4,
    use_idf=True,
    smooth_idf=True,
    sublinear_tf=True,
    norm='l2',
    analyzer='word',
    ngram_range=(1,1)
)
tfidf = extractor.fit_transform(posts)

# append extra features to tfidf
feature = sparse.hstack((tfidf, extra_features))

# train and test a classifier; in this case, we use a linear SVM
cl = sklearn.svm.SVC(kernel='linear')
cl.fit(feature, labels)

# get the weights from classifier
coefficients = cl.coef_

# make corresponding feature name
feature_names = extractor.get_feature_names()
n_extra_features = len(extra_features[0])
for i in range(1, n_extra_features + 1):
    feature_names.append('#extra_' + str(i) + '#')

# get index for top 50
print('\n' + "50 features with highest weight: ")
print_flr(-50, coefficients, feature_names)

# get index for floor 50
print('\n' + "50 features with lowest weight: ")
print_top(50, coefficients, feature_names)