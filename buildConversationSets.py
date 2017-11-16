# This program constructs the conversation sets for parameter N = 1 to n

from datetime import date, timedelta

labelsFile = open('labels.txt', 'r')
labelMap = {}
for line in labelsFile:
    lineArray = line.split('\t')
    label = ''
    if lineArray[1] == 'green\n':
        label = 'green'
    elif lineArray[1] == 'amber\n' or lineArray[1] == 'red\n' or lineArray[1] == 'crisis\n':
        label = 'flagged'
    labelMap[lineArray[0]] = label
labelsFile.close()

postsFile = open('posts.txt', 'r').readlines()

def getDate(inputStr):
    postYear = inputStr[0:4]
    postMonth = inputStr[5:7]
    postDay = inputStr[8:10]
    return date(int(postYear), int(postMonth), int(postDay))

for n in range(1, 15):
    # this will contain 'postUser date': [postLabel, replyText, nextPostLabel]
    # where postLabel is 'flagged' if any post on that date was 'flagged', and
    # nextPostLabel is the label of the user's next post after n days
    conversationSets = {}
    print('working on ' + str(n) + '-day conversations')
    lineNumber = 0
    for line in postsFile:
        if lineNumber == 63064:
            # stop when we get here (14 days before the end of the dataset) to make sure
            # we don't run off the end of the dataset while looking for replies
            break
        postArray = line.split('\t')
        postDate = getDate(postArray[0])
        postID = postArray[1]
        if postID in labelMap:
            postLabel = labelMap[postID]
        else:
            postLabel = '?'
        postUser = postArray[2]
        userState = postUser + ' ' + postDate.isoformat()
        # see if we've already built a conversation set for this user
        # beginning on this day, and skip it if so, but elevate label if appropriate
        if userState in conversationSets:
            if conversationSets[userState][0] == 'green' and postLabel == 'flagged':
                conversationSets[userState][0] = 'flagged'
            lineNumber += 1
            continue
        else: # if not, record the new user on this day
            conversationSets[userState] = [postLabel, ' ', 'dummyLabel']
        # string to append text of replies to this user as we find them
        replyText = ''
        # increment this variable to look at posts beyond the target user post
        searchDistance = 1
        # iterate through all subsequent posts for the next n days looking for replies
        while(True):
            potentialReply = postsFile[lineNumber + searchDistance].split('\t')
            if (getDate(potentialReply[0]) - postDate).days > n:
                break
            if potentialReply[2] == postUser:
                searchDistance += 1
                continue
            if postUser in potentialReply[3]:
                replyText = replyText + ' ' + potentialReply[4][:-1]
            searchDistance += 1
        # still need to find the target user's next post and append that label on here too
        conversationSets[userState][1] = replyText
        lineNumber += 1
    conversationsFile = open(str(n) + 'dayConversations.txt', 'w')
    for key, value in conversationSets.items():
        keyArray = key.split(' ')
        # only write to the file if we found reply text and a nextPostLabel
        if value[1] != '': # and value[2] != '?':
            conversationsFile.write(keyArray[0] + '\t' + keyArray[1] + '\t' + value[0] + '\t' + value[1] + '\t' + value[2] + '\n')
    conversationsFile.close()
