import hashlib
import itertools
import json
import random
import string
import time
import xml.etree.ElementTree as trees
from concurrent import futures

import requests

from database import *

ex = futures.ThreadPoolExecutor(max_workers=1000)

key = input("Enter a KeyWord: ").lower().strip()

randomint = random.randrange(100)

databasekey = "_".join(key.split()) + str(randomint)
print(databasekey)
createdatabase(databasekey)

prefix = []
postfix = []
prepostfix = []
querylist = []
prefixedlist = []
finished_list = []  # The Finished list with all the containing keywords scraped from google.com
blacklist = []  # This is the list of blacklisted words!
unique_list = []
fixed_list = []
fixed_list_words = []

f = open('prepostfixfile.txt', 'r+')
data1 = f.read()
prepostfix = data1.split("\n")
print(prepostfix)
f.close()

f = open('blacklistfile.txt', 'r+')
data4 = f.read()
some_list = data4.split("\n")
for item in some_list:
    blacklist.append(item.lower())
print(blacklist)
f.close()

f = open('prefixfile.txt', 'r+')
data2 = f.read()
prefix = data2.split("\n")
print(prefix)
f.close()

f = open('postfixfile.txt', 'r+')
data3 = f.read()
postfix = data3.split("\n")
print(postfix)
f.close()

success = 0
failed = 0


def prepostfunc():  # generating a new list from the newly scraped data
    pureletters = []
    for rp in range(1, 4):
        pureletters.extend([''.join(i) for i in itertools.product(string.ascii_lowercase, repeat=rp)])
    #pureletters=["a"]
    for item_letter in pureletters:
        string1 = key.replace(" ", "+") + "+" + item_letter
        prefixedlist.append(string1)
        string2 = item_letter + "+" + key.replace(" ", "+")
        prefixedlist.append(string2)
        string3 = item_letter + "+" + key.replace(" ", "+") + "+" + item_letter
        prefixedlist.append(string3)


def createrequest(indexposition):
    global success
    global failed

    targrturl = "http://suggestqueries.google.com/complete/search?output=toolbar&hl=en&q=" + prefixedlist[
        indexposition]  # adding the value in the list to the url

    headers = {'User-Agent': randomagent()}

    http_proxy = ""
    https_proxy = ""

    proxyDict = {
        "http": http_proxy,
        #"https": https_proxy
    }

    # params = {
    # 	'access_key': 'f5f73b3a835269b617e8b46731b5616e',
    # 	'url': targrturl
    # }

    try:
        rq = requests.get(targrturl, headers=headers, proxies=proxyDict)
        print('Response HTTP Status Code: {status_code}'.format(status_code=rq.status_code))

        if rq.status_code == 200:
            success += 1

            tree = trees.fromstring(rq.text)
            print("request successful :)")

            for child in tree.iter('suggestion'):
                if child.attrib['data'] not in blacklist:
                    finished_list.append(child.attrib['data'])  # Putting the keywords in the list of data
                    uploaddata(child.attrib['data'], 0, databasekey, child.attrib['data'].split(),
                               prefixedlist[indexposition], 0, rq.elapsed.total_seconds())
    except Exception as e:
        failed += 1
        print("request failed: attempting to restart")


def is_thread_completed(fn):
    if fn.cancelled():
        print('Thread cancelled successfully - ignore')
    elif fn.done():
        error = fn.exception()
        if error:
            print('error returned: {}'.format(error))
        else:
            result = fn.result()
            if result:
                print('value returned: {}'.format(result))


def threadingfunction(prefixed_list):  # A function that will send multiple request at once so that we can scrape faster
    for x in range(len(prefixed_list)):
        time.sleep(0.4)
        conc = ex.submit(createrequest, x)
        conc.add_done_callback(is_thread_completed)


def list_broker(list_d):
    new_list = []
    # y = keyword_parsing(list_c)

    for items in list_d:
        for brokenitems in items.split():
            new_list.append(brokenitems)
    return sorted(new_list)


def removeduplicates(uniquewords):
    local_list = []
    for i in uniquewords:
        if i not in local_list:
            local_list.append(i)
    return sorted(local_list)


def checkforblacklist(uniquewords):
    local_list = []
    for item in uniquewords:
        if item not in blacklist:
            local_list.append(item)
    return local_list


def difference(uniquelist, finishedlist):
    local_list = []
    if len(unique_list) == 0:
        return finishedlist
    else:
        for i in finishedlist:
            if i not in uniquelist:
                local_list.append(i)
        return local_list


def differencewords(querylist, wordslist):
    local_list = []

    for y in wordslist:
        if y not in querylist:
            local_list.append(y)
    return local_list


def checkdifference(uniquelist, finishedlist):
    uniquelist.sort()
    finishedlist.sort()

    print("checking difference")

    if uniquelist == finishedlist:
        print("its true")
        return True
    else:
        print("its false")
        return False


def isascii(s):
    if len(s) == len(s.encode()):
        return True
    else:
        return False


def special(s):
    if any(not c.isalnum() for c in s):
        return True
    else:
        return False


def randomagent():
    user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
    ]

    return user_agent_list[random.randrange(len(user_agent_list))]
