# This program constructs the conversation sets for parameter N = 1 to n

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

# iterate through all the posts and potential replies for each value of N days
for n in range(1, 15):
    # this will contain 'postUser date': [postLabel, replyText, nextPostLabel]
    # where postLabel is the label of the user's last post in a given day, and
    # nextPostLabel is the label of the user's next post after n days
    conversationSets = {}
    print('working on ' + str(n) + '-day conversations')
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
        userState = postUser + ' ' + postDate.isoformat()
        # see if we've already built a conversation set for this user
        # beginning on this day, and skip it if so, but update the initial state label
        if userState in conversationSets:
            conversationSets[userState][0] = postLabel
            lineNumber += 1
            continue
        else: # if not, record the new user on this day
            conversationSets[userState] = [postLabel, '', '?']
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
        conversationSets[userState][1] = replyText
        # find the user's next reply after N days and get that label
        searchDistance = 1
        while(True):
            potentialNextPost = postsFile[lineNumber + searchDistance].split('\t')
            if (getDate(potentialNextPost[0]) - postDate).days > n:
                if potentialNextPost[2] == postUser:
                    if potentialNextPost[1] in labelMap:
                        conversationSets[userState][2] = labelMap[potentialNextPost[1]]
                        break
            # give up on the search for the next post if it's been more than a week
            if (getDate(potentialNextPost[0]) - postDate).days > n + 7:
                break
            searchDistance += 1
        lineNumber += 1
    # write the results for this value of N to a file
    conversationsFile = open(str(n) + 'dayConversations-finalPostInitialState.txt', 'w')
    greenToFlagged = 0
    flaggedToFlagged = 0
    flaggedToGreen = 0
    greenToGreen = 0
    noRepliesFound = 0
    for key, value in conversationSets.items():
        keyArray = key.split(' ')
        if value[0] == 'green' and value[2] == 'flagged':
            greenToFlagged += 1
        if value[0] == 'flagged' and value[2] == 'flagged':
            flaggedToFlagged += 1
        if value[0] == 'flagged' and value[2] == 'green':
            flaggedToGreen += 1
        if value[0] == 'green' and value[2] == 'green':
            greenToGreen += 1
        # only write to the file if we found a nextPostLabel
        if value[2] != '?':
            if value[1] != '':
                conversationsFile.write(value[0] + '\t' + value[1] + '\t' + value[2] + '\n')
            else:
                # intentionally keeping the cases where we found no replies
                conversationsFile.write(value[0] + '\t...noRepliesFound...\t' + value[2] + '\n')
                noRepliesFound += 1
    print('green to flagged: ' + str(greenToFlagged))
    print('flagged to flagged: ' + str(flaggedToFlagged))
    print('flagged to green: ' + str(flaggedToGreen))
    print('green to green: ' + str(greenToGreen))
    print('no replies found: ' + str(noRepliesFound))
    conversationsFile.close()
