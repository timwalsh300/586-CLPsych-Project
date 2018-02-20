# This program constructs the conversation sets for parameter N = 1 to 14

from datetime import date, timedelta
import re
from textblob import TextBlob
from nltk import word_tokenize
from nltk.corpus import stopwords
stops = set(stopwords.words('english'))

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

# this gets Arman's confidence values for each label
confidenceFile = open('confidence.tsv', 'r')
confidenceMap = {}
for line in confidenceFile:
    lineArray = line.split('\t')
    confidenceMap[lineArray[0]] = float(lineArray[1])
confidenceFile.close()

# grab some user metadata from here
metaData = open('userMetadata.txt', 'r').readlines()
userRiskLevels = {}
for line in metaData:
    lineTokens = line.split('\t')
    userRiskLevels[lineTokens[0]] = float(lineTokens[4])

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
    # this will contain 'postUser date': [postLabel, replyText, nextPostLabel, numReplies, numModReplies, targetUserPosts, replyPosterRiskAvg, replyPolarity, replySubjectivity]
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
        if postArray[5] == 'T':
            lineNumber += 1
            continue
        # check if this post is in the "Turning negatives into positives" thread and if so,
        # ignore it because Arman's system generates a lot of false flags on those posts
        if postArray[7] == 'T\n':
            lineNumber += 1
            continue
        postDate = getDate(postArray[0])
        postID = postArray[1]
        postLabel = ''
        # only start a conversation set using this post if we have a high confidence label for it
        if postID in labelMap and postID in confidenceMap:
            if confidenceMap[postID] >= 0.7:
                postLabel = labelMap[postID]
            else:
                lineNumber += 1
                continue
        else:
            lineNumber += 1
            continue
        postUser = postArray[2]
        postFullUser = postArray[6][:-1]
        userState = postUser + ' ' + postDate.isoformat()
        # see if we've already built a conversation set for this user
        # beginning on this day, and skip it if so, but elevate label if appropriate
        if userState in conversationSets:
            if conversationSets[userState][0] == 'green' and postLabel == 'flagged':
                conversationSets[userState][0] = 'flagged'
            lineNumber += 1
            continue
        else: # if not, record the new user on this day
            conversationSets[userState] = [postLabel, '', '?', 0, 0, 0, 0.07, 0.0, 0.5]
        # string to append text of replies to this user as we find them
        # for error analysis, put in the post ID that gave us initial state
        replyText = ''
        numReplies = 0
        numModReplies = 0
        # this captures the activity level of the target user over the N day period
        targetUserPosts = 0
        # sum up risk levels of reply posters (based on % of their posts that are flagged)
        replyPosterRisk = 0
        # increment this variable to look at posts beyond the target user post
        searchDistance = 1
        # iterate through all subsequent posts for the next n days looking for replies
        while(True):
            potentialReply = postsFile[lineNumber + searchDistance].split('\t')
            if (getDate(potentialReply[0]) - postDate).days > n:
                break
            if potentialReply[2] == postUser:
                targetUserPosts += 1
                searchDistance += 1
                continue
            if postUser in potentialReply[3]:
                replyText = replyText + ' ' + potentialReply[2] + ' ' + potentialReply[4]
                numReplies += 1
                if potentialReply[2] in userRiskLevels:
                    replyPosterRisk += userRiskLevels[potentialReply[2]]
                else:
                    # give it the % for the forum as a whole to be neutral
                    replyPosterRisk += 0.07
                if potentialReply[5] == 'T':
                    numModReplies += 1
            searchDistance += 1
        replyText1 = re.sub(postFullUser, '', replyText, 0, re.S)
        replyText2 = re.sub(postUser, '', replyText1, 0, re.S)
        blob = TextBlob(replyText2)
        conversationSets[userState][3] = numReplies
        conversationSets[userState][4] = numModReplies
        conversationSets[userState][5] = targetUserPosts
        if numReplies > 0:
            conversationSets[userState][6] = replyPosterRisk / numReplies
            conversationSets[userState][7] = blob.sentiment.polarity
            conversationSets[userState][8] = blob.sentiment.subjectivity
        replyTextList = [i for i in word_tokenize(replyText2.lower()) if i not in stops]
        conversationSets[userState][1] = ' '.join(replyTextList)
        # find the user's posts between days N to N+7 and make the conversationSet
        # end-state flagged if any post is flagged
        searchDistance = 1
        while(True):
            potentialNextPost = postsFile[lineNumber + searchDistance].split('\t')
            # if we're in the next post window
            if (getDate(potentialNextPost[0]) - postDate).days > n:
               # if it's the target user and the post isn't in "Turning negatives into positives"
               if potentialNextPost[2] == postUser and potentialNextPost[7] == 'F\n':
                    # if we have Arman's label for this post, capture it
                    if potentialNextPost[1] in labelMap and potentialNextPost[1] in confidenceMap:
                        # the following line was for error analysis
                        # conversationSets[userState][1] += ' ' + str(potentialNextPost[1])
                        # get the first label found, whatever it is
                        if conversationSets[userState][2] == '?':
                            # but only if the label is high confidence
                            if confidenceMap[potentialNextPost[1]] >= 0.9:
                                conversationSets[userState][2] = labelMap[potentialNextPost[1]]
                        # update the end-state label if we find a flagged post later
                        elif conversationSets[userState][2] == 'green' and labelMap[potentialNextPost[1]] == 'flagged':
                            if confidenceMap[potentialNextPost[1]] >= 0.70:
                                conversationSets[userState][2] = 'flagged'
            # stop searching after a week
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
        if value[0] == 'green' and value[2] == 'flagged':
            greenToFlagged += 1
            if value[1] == '':
                greenToFlaggedNoReplies += 1
        if value[0] == 'flagged' and value[2] == 'flagged':
            flaggedToFlagged += 1
            if value[1] == '':
                flaggedToFlaggedNoReplies += 1
        if value[0] == 'flagged' and value[2] == 'green':
            flaggedToGreen += 1
            if value[1] == '':
                flaggedToGreenNoReplies += 1
        if value[0] == 'green' and value[2] == 'green':
            greenToGreen += 1
            if value[1] == '':
                greenToGreenNoReplies += 1
        # only write to the file if we found a nextPostLabel
        if value[2] != '?':
            if value[3] > 0:
                conversationsFile.write(value[0] + '\t' + value[1] + '\t' + value[2] + '\t' + str(value[3]) + '\t' + str(value[4]) + '\t' + str(value[5]) + '\t' + str(value[6]) + '\t' + str(value[7]) + '\t' + str(value[8]) + '\n')
            else:
                # throw away cases where we found no replies
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
