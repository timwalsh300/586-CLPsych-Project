import csv
import re
from operator import add
from nltk.corpus import stopwords
from gensim import corpora
from gensim.models import ldamulticore
import matplotlib.pyplot as plt
import numpy as np

def reorder(original, order):
    reordered = [0.0] * len(original)
    for ind in enumerate(order):
        reordered[ind[0]] = original[ind[1]]
    return reordered

def load_stop_words():
    with open('./largeStopList.txt') as l:
        stop_list = l.readlines()
    stop_list = [word.rstrip() for word in stop_list if word.rstrip() != '']
    return stop_list


# read in bodyTextOnly.txt
with open('./SomethingsNotRightTextOnly.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    id_body = list(reader)

# separate out post
posts = [row[1] for row in id_body]


# build topic model base on posts

## make dictionary
# stop_words = set(stopwords.words('english'))
stop_words = load_stop_words()
words = [[word for word in re.split('\W+', post.lower()) if (word not in stop_words and word != "")] for post in posts]
dictionary = corpora.Dictionary(words)

## build corpus
corpus = [dictionary.doc2bow(word) for word in words if word != ""]

## initialize lda model
lda = ldamulticore.LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=40
)

## print topics
topics = lda.print_topics(num_words=10, num_topics=-1)
# for topic in topics:
#     print(topic)
#     print()


# label small set of conversation sets, print topic distribution for each
## read in selectedConvs.txt
with open('./14dayConversations.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    convSets = list(reader)
## separate out conversations
# convs = [row[1] for row in convSets]
## initialize the container for the distribution
sum_distribution_flagged = [0.0] * lda.num_topics
sum_distribution_green = [0.0] * lda.num_topics
## get topic distribution of each conversation, and aggregate the distribution
for convSet in convSets:
    conv = convSet[1]
    words = [word for word in re.split('\W+', conv.lower())]
    bow = dictionary.doc2bow(words)
    doc_topics = lda.get_document_topics(bow) # doc_topics here is a list of tuple (id for topic, probability)
    doc_topics_distribution = [0.0] * lda.num_topics # initialize document topic distribution
    for t in doc_topics:
        index = t[0]
        distribution = t[1]
        doc_topics_distribution[index] = distribution
    if ( convSet[0] == 'green' ):
        sum_distribution_green = list(map(add, sum_distribution_green, doc_topics_distribution))
    else:
        sum_distribution_flagged = list(map(add, sum_distribution_flagged, doc_topics_distribution))
## plot sum of distribution
sum_distribution = list(map(add, sum_distribution_green, sum_distribution_flagged))
order = np.argsort(sum_distribution)
# reorder
overall = reorder(sum_distribution, order)
green = reorder(sum_distribution_green, order)
flagged = reorder(sum_distribution_flagged, order)
# plot
plt.figure(figsize=(12, 3)) # create figure
# plot overall with blue
plt.subplot(131)
plt.plot(overall, 'b')
# plot green with green
plt.subplot(132)
plt.plot(green, 'g')
# plot flagged with red
plt.subplot(133)
plt.plot(flagged, 'r')

plt.show()