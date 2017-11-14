# This program constructs the post-reply sets for parameter N = 1 to n

from datetime import date, timedelta

postsFile = open('posts.txt', 'r').readlines()

def getDate(inputStr):
    postYear = inputStr[0:4]
    postMonth = inputStr[5:7]
    postDay = inputStr[8:10]
    return date(int(postYear), int(postMonth), int(postDay))

for n in range(1, 15):
    print('opening ' + str(n) + 'daysReplies.txt')
    repliesFile = open(str(n) + 'daysReplies.txt', 'w')
    lineNumber = 0
    for line in postsFile:
        postArray = line.split('\t')
        postDate = getDate(postArray[0])
        postID = postArray[1]
        print('working on post ' + postID)
        # need to still get post label based on the ID...
        postUser = postArray[2]
        # string to append text of replies to this user as we find them
        replyText = ''

        searchDistance = 1
        reachedHorizon = False
        repliesFound = 0
        while(not reachedHorizon):
            potentialReply = postsFile[lineNumber + searchDistance].split('\t')
            print('...checking post ' + potentialReply[1])
            if (getDate(potentialReply[0]) - postDate).days > n:
                print('......past ' + str(n) + ' days')
                reachedHorizon = True
            if potentialReply[2] == postUser:
                searchDistance += 1
                continue
            if postUser in potentialReply[3]:
                print('......found reply')
                repliesFound += 1
                replyText = replyText + ' ' + potentialReply[4]
            searchDistance += 1
        if repliesFound > 0:
            repliesFile.write(postID + '\t' + replyText + '\n')
            print(postID + '\t' + replyText)
        lineNumber += 1
    repliesFile.close()

postsFile.close()
