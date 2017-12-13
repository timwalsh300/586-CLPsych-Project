# This program extracts and cleans all the post body text from posts on the
# SomethingsNotRight sub-forum so we can train a topic model

import os
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

postsList = []
postsFile = open('SomethingsNotRightTextOnly.txt', 'w')

# process all the individual post XML files and create a single text file
for dirName, subdirList, fileList in os.walk('posts'):
    for fname in fileList:
        tree = ET.parse('posts/' + fname)
        response = tree.getroot()
        if response.get('status') == 'error':
            continue
        message = response[0]
        board = message.find('board').get('href')
        if board != '/boards/id/Something_Not_Right':
            continue
        id = message.find('id').text
        if id is None:
            continue
        rawBody = message.find('body').text

        # handle some posts in the dataset that are inexplicably blank
        if rawBody is None:
            continue

        # clean up post body text
        quotesRemovedBody = re.sub(r"<BLOCKQUOTE(.*?)>(.*?)</BLOCKQUOTE>", '', rawBody, 0, re.S)
        htmlRemovedQuotesRemovedBody = BeautifulSoup(quotesRemovedBody).text
        htmlRemovedQuotesRemovedBodyTokens = htmlRemovedQuotesRemovedBody.split()
        finalTextBody = ' '.join(htmlRemovedQuotesRemovedBodyTokens)

        # put it all together
        postString = id + '\t' + finalTextBody
        postsList.append(postString)

for line in postsList:
    postsFile.write(line + '\n')
postsFile.close()
