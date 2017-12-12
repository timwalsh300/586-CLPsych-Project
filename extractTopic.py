import csv
import re
from nltk.corpus import stopwords
from gensim import corpora
from gensim.models import ldamulticore



# read in bodyTextOnly.txt
with open('./bodyTextOnly.txt') as f:
    reader = csv.reader(f, delimiter='\t')
    id_body = list(reader)

# separate out post
posts = [row[1] for row in id_body]


# extract topic from posts with lda

## make dictionary
stop_words = set(stopwords.words('english'))
words = [[word for word in re.split('\W+', post.lower()) if word not in stop_words] for post in posts]
dictionary = corpora.Dictionary(words)

## make dictionary
corpus = [dictionary.doc2bow(word) for word in words]

## initialize lda model
lda = ldamulticore.LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=20
)

## print topics
topics = lda.print_topics(num_words=15, num_topics=-1)
for topic in topics: print(topic)