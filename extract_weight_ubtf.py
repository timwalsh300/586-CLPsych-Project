import csv
import numpy as np
import scipy.sparse as sparse
import sklearn.model_selection
import sklearn.metrics
import sklearn.svm
import sklearn.feature_extraction

import cutils

# read in id_label_body
with open('./con/' + '14dayConversations.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    file = list(reader)

labels, posts, extra_features = cutils.extract_all(file)

# extract tf-idf from from data
extractor = sklearn.feature_extraction.text.TfidfVectorizer(
    min_df=4,
    use_idf=True,
    smooth_idf=True,
    sublinear_tf=True,
    norm='l2',
    analyzer='word',
    ngram_range=(1,3)
)
tfidf = extractor.fit_transform(posts)

# append extra features to tfidf
features = sparse.hstack((tfidf, extra_features))

# train and test a classifier; in this case, we use a linear SVM
cl = sklearn.svm.SVC(kernel='linear')
cl.fit(features, labels)

# get the weights from classifier
coefficients = cl.coef_

# make corresponding feature name
feature_names = extractor.get_feature_names()
n_extra_features = len(extra_features[0])
for i in range(1, n_extra_features + 1):
    feature_names.append('#extra_' + str(i) + '#')

# print weights and tfidf for top weighted features
print('\n' + 'Weights for extra features: ')
e_n = len(feature_names)
e_1 = e_n - n_extra_features
for i in range(e_1, e_n):
    print('extra ' + str(i - e_1 + 1) + ': ' + str(coefficients[0,i]))

# print terms with highest weights
print('\n' + '50 features with highest weight: ')
cutils.print_flr(-50, coefficients, feature_names)

# print terms with lowest weights
print('\n' + '50 features with lowest weight: ')
cutils.print_top(50, coefficients, feature_names)

