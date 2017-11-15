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

for n in range(1, 14):
    conversationsFile = open(str(n) + 'dayConversations.txt', 'w')
    lineNumber = 0
    numberOfSets = 0
    statesCaptured = []
    for line in postsFile:
        postArray = line.split('\t')
        postDate = getDate(postArray[0])
        postID = postArray[1]
        print('working on post ' + postID + ', ' + str(n) + ' days')
        postLabel = labelMap[postID]
        postUser = postArray[2]
        # see if we've already built a conversation set for this user
        # beginning on this day, and skip it if so
        if (postUser + ' ' + postDate.isoformat()) in statesCaptured:
            continue
        # if not, record the new user on this day
        statesCaptured.append(postUser + ' ' + postDate.isoformat())
        # string to append text of replies to this user as we find them
        replyText = ''
        # increment this variable to look at posts beyond the target user post
        searchDistance = 1
        repliesFound = 0
        # iterate through all subsequent posts for the next n days looking for replies
        while(True):
            potentialReply = postsFile[lineNumber + searchDistance].split('\t')
            if (getDate(potentialReply[0]) - postDate).days > n:
                break
            if potentialReply[2] == postUser:
                searchDistance += 1
                continue
            if postUser in potentialReply[3]:
                repliesFound += 1
                replyText = replyText + ' ' + potentialReply[4][:-1]
            searchDistance += 1
        # only write a line to the file if we actually found a conversation
        if repliesFound > 0:
            numberOfSets += 1
            # still need to find the target user's next post and append that label on here too
            conversationsFile.write(postID + '\t' + postLabel + '\t' + replyText + '\n')
        lineNumber += 1
    conversationsFile.write('number of sets = ' + str(numberOfSets))
    conversationsFile.close()

postsFile.close()
