# This program is the first step of transforming the original CLPysch dataset
# into the form that we need to start creating post-reply sets

import os
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

loginsList = []
loginsFile = open('logins.txt', 'w')
postsList = []
postsFile = open('posts.txt', 'w')

# normalize and cleanup tokens that could be usernames
def parseUsername(input):
        inputLower = input.lower()
        inputLowerClean = re.sub(r'[^a-z0-9]', '', inputLower)
        return inputLowerClean

# create a list to check against as we extract usernames from text
for dirName, subdirList, fileList in os.walk('posts'):
    for fname in fileList:
        tree = ET.parse('posts/' + fname)
        response = tree.getroot()
        if response.get('status') == 'error':
            continue
        message = response[0]
        login = message.find('author')[0].text
        # deal crudely with the case of login names that include spaces...
        # looking at the list of names, it appears that this won't produce duplicates
        simplifiedLogin = parseUsername(login.split()[0])
        if simplifiedLogin not in loginsList:
            loginsList.append(simplifiedLogin)
loginsList.sort()
for line in loginsList:
    loginsFile.write(line + '\n')
loginsFile.close()

# process all the individual post XML files and create a single text file
# in the format that will be easier for us to process in the next step
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
        time = message.find('post_time').text
        login = message.find('author')[0].text
        simplifiedLogin = parseUsername(login.split()[0])
        rawBody = message.find('body').text

        # handle some posts in the dataset that are inexplicably blank
        if rawBody is None:
            continue

        # extract usernames from the post body
        htmlRemovedBody = BeautifulSoup(rawBody).text
        quotedUsers = ' '
        htmlRemovedBodyTokens = htmlRemovedBody.split()
        lastToken = ''
        for token in htmlRemovedBodyTokens:
            if lastToken == 'Hi' or lastToken == 'hi' or lastToken == 'Hello' or lastToken == 'hello' or lastToken == 'Hey' or lastToken == 'hey':
                    if parseUsername(token) in loginsList:
                        quotedUsers = quotedUsers + parseUsername(token) + ' '
                    lastToken = token
                    continue
            if token.startswith('wrote:'):
                    if parseUsername(lastToken) in loginsList:
                        quotedUsers = quotedUsers + parseUsername(lastToken) + ' '
                    lastToken = token
                    continue
            if token.startswith('@'):
                    if parseUsername(token) in loginsList:
                        quotedUsers = quotedUsers + parseUsername(token) + ' '
                    lastToken = token
                    continue
            lastToken = token

        # clean up post body text
        quotesRemovedBody = re.sub(r"<BLOCKQUOTE(.*?)>(.*?)</BLOCKQUOTE>", '', rawBody, 0, re.S)
        htmlRemovedQuotesRemovedBody = BeautifulSoup(quotesRemovedBody).text
        htmlRemovedQuotesRemovedBodyTokens = htmlRemovedQuotesRemovedBody.split()
        finalTextBody = ' '.join(htmlRemovedQuotesRemovedBodyTokens)

        # put it all together
        postString = time + '\t' + id + '\t' + simplifiedLogin + '\t[' + quotedUsers + ']\t' + finalTextBody
        postsList.append(postString)

postsList.sort()
for line in postsList:
    postsFile.write(line + '\n')
postsFile.close()
