# This program collects some user metadata to help with our analysis

import os
import xml.etree.ElementTree as ET

# this gets Arman's predicted labels for each post
labelsFile = open('labels.txt', 'r')
labelMap = {}
for line in labelsFile:
    lineArray = line.split('\t')
    label = ''
    if lineArray[1] == 'green\n':
        label = 'green'
    # the binary green/flagged accuracy is 93%, so we'll use that
    elif lineArray[1] == 'amber\n' or lineArray[1] == 'red\n' or lineArray[1] == 'crisis\n':
        label = 'flagged'
    labelMap[lineArray[0]] = label
labelsFile.close()

# create a list of all the moderator ID numbers to reference later when we filter
ranks = open('author_rankings.tsv', 'r').readlines()
modsList = []
for line in ranks:
    lineTokens = line.split('\t')
    if 'Mod' in lineTokens[1] or 'Crew' in lineTokens[1] or 'Staff' in lineTokens[1]:
        modsList.append(lineTokens[0])

# this holds (username, [posts, flaggedPosts, moderatorBoolean])
loginsList = {}
totalPosts = 0
totalFlagged = 0
# process all the individual post XML files and create a single text file with user data
for dirName, subdirList, fileList in os.walk('posts'):
    for fname in fileList:
        tree = ET.parse('posts/' + fname)
        response = tree.getroot()
        if response.get('status') == 'error':
            continue
        message = response[0]
        id = message.find('id').text
        if id is None:
            continue
        if id in labelMap:
            postLabel = labelMap[id]
        else:
            postLabel = '?'
        authorID = message.find('author').get('href')[10:]
        if authorID in modsList:
            modBoolean = 'T'
        else:
            modBoolean = 'F'
        login = message.find('author')[0].text
        if login not in loginsList:
            if login in modsList:
                loginsList[login] = [0, 0, 'T']
            else:
                loginsList[login] = [0, 0, 'F']
        loginsList[login][0] += 1
        totalPosts += 1
        if postLabel == 'flagged':
            loginsList[login][1] += 1
            totalFlagged += 1

loginsFile = open('logins.txt', 'w')
loginsFile.write('total posts = ' + str(totalPosts) + '\n')
loginsFile.write('total flagged = ' + str(totalFlagged) + '\n')
loginsFile.write(str(100 * (totalFlagged / totalPosts)) + '% flagged\n')
for key, value in loginsList.items():
    loginsFile.write(key + '\tmod = ' + value[2] + '\tposts = ' + str(value[0]) + '\tflagged = ' + str(value[1]) + '\t' + str(100 * (value[1]/value[0])) + '%\n')
loginsFile.close()
