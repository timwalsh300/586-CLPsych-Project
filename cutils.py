import numpy as np
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer

class LemmaTokenizer(object):
    def __init__(self):
        self.wnl = WordNetLemmatizer()
    def __call__(self, doc):
        return [self.wnl.lemmatize(t) for t in word_tokenize(doc)]

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

def cat_to_boolean(cat):
    for i in range(0, len(cat)):
        if cat[i] == 'flagged':
            cat[i] = True
        else:
            cat[i] = False
    return cat

def round_up(probas):
    labels = [0] * len(probas)
    for i in range(len(probas)):
        if probas[i][0] > probas[i][1]:
            labels[i] = 0
        else:
            labels[i] = 1
    return labels

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