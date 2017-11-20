# This program constructs conversation "snapshots" where we just look at two consecutive
# posts by a target user, and capture the by-name replies that occur between them,
# generally agnostic of the timing

from datetime import date, timedelta

# this gets Arman's predicted labels for each post
labelsFile = open('labels.txt', 'r')
labelMap = {}
for line in labelsFile:
    lineArray = line.split('\t')
    label = ''
    if lineArray[1] == 'green\n':
        label = 'green'
    # the binary green/flagged accuracy is like 98%, so we'll use that
    elif lineArray[1] == 'amber\n' or lineArray[1] == 'red\n' or lineArray[1] == 'crisis\n':
        label = 'flagged'
    labelMap[lineArray[0]] = label
labelsFile.close()

# this contains the dataset after stage 1 preprocessing (combinePosts.py)
postsFile = open('posts.txt', 'r').readlines()

# this function helps parse the forum date-time stamps into Python date objects
def getDate(inputStr):
    postYear = inputStr[0:4]
    postMonth = inputStr[5:7]
    postDay = inputStr[8:10]
    return date(int(postYear), int(postMonth), int(postDay))

# this will contain 'postUser date': [postLabel, replyText, nextPostLabel]
# where postLabel is 'flagged' if any post on that date was 'flagged', and
# nextPostLabel is the label of the user's next post after n days
conversationSets = {}
lineNumber = 0
for line in postsFile:
        if lineNumber == 62543:
            # stop when we get here (21 days before the end of the dataset) to make sure
            # we don't run off the end of the dataset while looking for replies and next posts
            break
        postArray = line.split('\t')
        postDate = getDate(postArray[0])
        postID = postArray[1]
        if postID in labelMap:
            postLabel = labelMap[postID]
        else:
            postLabel = '?'
        postUser = postArray[2]
        userState = postUser + ' ' + postID
        conversationSets[userState] = [postLabel, '', '?']
        # string to append text of replies to this user as we find them
        replyText = ''
        # increment this variable to look at posts beyond the target user post
        searchDistance = 1
        # iterate through all subsequent posts for by-name replies and the user's next post
        while(True):
            potentialReply = postsFile[lineNumber + searchDistance].split('\t')
            if (getDate(potentialReply[0]) - postDate).days > 21:
                break
            if potentialReply[2] == postUser:
                if potentialReply[1] in labelMap:
                    conversationSets[userState][2] = labelMap[potentialReply[1]]
                break
            if postUser in potentialReply[3]:
                replyText = replyText + ' ' + potentialReply[4][:-1]
            searchDistance += 1
        conversationSets[userState][1] = replyText
        lineNumber += 1
conversationsFile = open('conversationSnapshots.txt', 'w')
for key, value in conversationSets.items():
    keyArray = key.split(' ')
    # only write to the file if we found replies and a nextPostLabel
    if value[1] != '' and value[2] != '?':
        conversationsFile.write(value[0] + '\t' + value[1] + '\t' + value[2] + '\n')
conversationsFile.close()
