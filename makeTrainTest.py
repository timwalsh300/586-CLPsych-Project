import csv

# read in file with posts as id_posts pairs
with open('./bodyTextOnly.txt') as posts:
    reader = csv.reader(posts, delimiter="\t")
    id_posts = list(reader)

# turn id from string to number,
for id_post in id_posts:
    id_post[0] = int(id_post[0])

# read in file with labels as id_label pairs
with open('./labels.tsv') as labels:
    reader = csv.reader(labels, delimiter="\t")
    id_labels = list(reader)

# turn the label into binary, green = 0, else = 1
for id_label in id_labels:
    id_label[0] = int(id_label[0])
    if id_label[1] == 'green':
        id_label[1] = 0
    else:
        id_label[1] = 1

# add id_posts into a dictionary
d = {}
for id_post in id_posts:
    d.setdefault(id_post[0], id_post[1])

# iterate through examples
for id_label in id_labels:
    id_label[2] = d[id_label[0]]
    id_label[0] = str(id_label[0])
    id_label[1] = str(id_label[1])

# save as tab
with open('idLabelBody.txt', 'w') as file:
    file.writelines('\t'.join(line) + '\n' for line in id_labels)