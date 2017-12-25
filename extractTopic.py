import csv
import re
from nltk.corpus import stopwords
from gensim import corpora
from gensim.models import ldamulticore

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
words = [[word for word in re.split('\W+', post.lower()) if word not in stop_words] for post in posts]
dictionary = corpora.Dictionary(words)

## make dictionary
corpus = [dictionary.doc2bow(word) for word in words]

## initialize lda model
lda = ldamulticore.LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=10
)

## print topics
topics = lda.print_topics(num_words=10, num_topics=-1)
for topic in topics:
    print(topic)
    print()


# label small set of conversation sets, print topic distribution for each
## read in selectedConvs.txt
with open('./selectedConvSets.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    convSets = list(reader)
## separate out conversations
convs = [row[1] for row in convSets]
## get topic distribution of each conversation
for conv in convs:
    words = [word for word in re.split('\W+', conv.lower())]
    bow = dictionary.doc2bow(words)
    print( lda.get_document_topics(bow) )
