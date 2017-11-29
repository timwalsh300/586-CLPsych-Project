import csv

for i in range(1, 14):

    # read in conversations
    with open( str(i) + 'dayConversations-thresholdInitialState.txt' ) as convs:
        reader = csv.reader(convs, delimiter='\t')
        label_conv_label = list(reader)

    # for each
    lc = []
    for lcl in label_conv_label:
        if lcl[0] == 'flagged':
            lc_0 = []
            if lcl[2] == 'green':
                lc_0.append("1")
                lc_0.append(lcl[1])
            else:
                lc_0.append("0")
                lc_0.append(lcl[1])
            lc.append(lc_0)

    # save as tab
    with open( str(i) + 'dayConv-thresholdInitialState.txt', 'w' ) as file:
        file.writelines('\t'.join(line) + '\n' for line in lc)