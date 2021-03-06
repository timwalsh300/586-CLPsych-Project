# This program constructs the conversation sets for parameter N = 1 to 14

from datetime import date, timedelta
import re

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
    # this will contain 'postUser date': [postLabel, replyText, nextPostLabel, numReplies, numModReplies]
    # where postLabel is 'flagged' if any post on that date was 'flagged', and
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
        # check if this post is by a moderator, and if so skip building a conversation set on it;
        # assume that moderators are not users of interest and just flood the data with greenToGreen cases
        if postArray[5] == 'T\n':
            lineNumber += 1
            continue
        postDate = getDate(postArray[0])
        postID = postArray[1]
        if postID in labelMap:
            postLabel = labelMap[postID]
        else:
            postLabel = '?'
        postUser = postArray[2]
        userState = postUser + ' ' + postDate.isoformat()
        # see if we've already built a conversation set for this user
        # beginning on this day, and skip it if so, but increment the label
        if userState in conversationSets:
            if postLabel == 'green':
                conversationSets[userState][5] += 1
            elif postLabel == 'flagged':
                conversationSets[userState][6] += 1
            lineNumber += 1
            continue
        else: # if not, record the new user on this day
            if postLabel == 'flagged':
                conversationSets[userState] = ['?', '', '?', 0, 0, 0, 1]
            else: # postLabel == 'green' or '?'
                conversationSets[userState] = ['?', '', '?', 0, 0, 1, 0]
        # string to append text of replies to this user as we find them
        replyText = ''
        numReplies = 0
        numModReplies = 0
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
                replyText = replyText + ' ' + potentialReply[4]
                numReplies += 1
                if potentialReply[5] == 'T\n':
                    numModReplies += 1
            searchDistance += 1
        conversationSets[userState][1] = replyText
        conversationSets[userState][3] = numReplies
        conversationSets[userState][4] = numModReplies
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
    conversationsFile = open(str(n) + 'dayConversations.txt', 'w')
    greenToFlagged = 0
    greenToFlaggedNoReplies = 0
    flaggedToFlagged = 0
    flaggedToFlaggedNoReplies = 0
    flaggedToGreen = 0
    flaggedToGreenNoReplies = 0
    greenToGreen = 0
    greenToGreenNoReplies = 0
    noRepliesFound = 0
    for key, value in conversationSets.items():
        keyArray = key.split(' ')
        if (value[6] / (value[5] + value[6])) >= 0.5:
            initialStateLabel = 'flagged'
        else:
            initialStateLabel = 'green'
        if initialStateLabel == 'green' and value[2] == 'flagged':
            greenToFlagged += 1
            if value[1] == '':
                greenToFlaggedNoReplies += 1
        if initialStateLabel == 'flagged' and value[2] == 'flagged':
            flaggedToFlagged += 1
            if value[1] == '':
                flaggedToFlaggedNoReplies += 1
        if initialStateLabel == 'flagged' and value[2] == 'green':
            flaggedToGreen += 1
            if value[1] == '':
                flaggedToGreenNoReplies += 1
        if initialStateLabel == 'green' and value[2] == 'green':
            greenToGreen += 1
            if value[1] == '':
                greenToGreenNoReplies += 1
        # only write to the file if we found a nextPostLabel
        if value[2] != '?':
            if value[1] != '':
                conversationsFile.write(initialStateLabel + '\t' + value[1] + '\t' + value[2] + '\t' + str(value[3]) + '\t' + str(value[4]) + '\n')
            else:
                # intentionally keeping the cases where we found no replies
                conversationsFile.write(initialStateLabel + '\t...noRepliesFound...\t' + value[2] + '\t' + str(value[3]) + '\t' + str(value[4]) + '\n')
                noRepliesFound += 1
    print('\tgreen to flagged: ' + str(greenToFlagged))
    print('\t\tno replies: ' + str(100 * (greenToFlaggedNoReplies / greenToFlagged)) + '%')
    print('\tflagged to flagged: ' + str(flaggedToFlagged))
    print('\t\tno replies: ' + str(100 * (flaggedToFlaggedNoReplies / flaggedToFlagged)) + '%')
    print('\tflagged to green: ' + str(flaggedToGreen))
    print('\t\tno replies: ' + str(100 * (flaggedToGreenNoReplies / flaggedToGreen)) + '%')
    print('\tgreen to green: ' + str(greenToGreen))
    print('\t\tno replies: ' + str(100 * (greenToGreenNoReplies / greenToGreen)) + '%')
    print('\tno replies found: ' + str(noRepliesFound))
    conversationsFile.close()
