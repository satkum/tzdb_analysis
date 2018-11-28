from urllib.request import urlopen
from bs4 import BeautifulSoup
import pickle
import sys


def getMonthName(monthSuffix):
    return monthSuffix.split('/')[0]


def processMessage(url, monthPart, msgSuffix):
    msgpageLink = url + monthPart + '/' + msgSuffix
    msgpage = None
    msgsoup = None
    try:
        msgpage = urlopen(msgpageLink).read()
        msgsoup = BeautifulSoup(msgpage, 'html.parser')
    except Exception as e:
        print("Error: {0}".format(e))
    msg = {}
    body_text = ""
    msg['subject'] = msgsoup.body.find('h1').text
    msg['timestamp'] = msgsoup.body.find('i').text
    msg['sender'] = msgsoup.body.find('b').text
    msg['email'] = msgsoup.body.find('a').text
    try:
        body_text = msgsoup.body.find('pre').text
    except Exception as e:
        # print(e)
        # print(msgsoup.body)
        # print("=======")
        if msgsoup.body.find('pre') is None:
            print("Empty body")
            body_text = ""
        else:
            raise
    return (msg, body_text)


def processMonth(url, monthSuffix, outputDir):
    monthPart = getMonthName(monthSuffix)
    print("Month {0}".format(monthPart))
    monthpage = None
    monthsoup = None
    try:
        monthpage = urlopen(url + monthSuffix).read()
        monthsoup = BeautifulSoup(monthpage, 'html.parser')
    except Exception as e:
        print("Error: {0}".format(e))

    items = monthsoup.find_all('ul')[1]
    msgLinks = [m for m in items.find_all('a') if len(m.text) > 1]
    print("# of messages : {0}".format(len(msgLinks)))
    fname = outputDir + "/" + monthPart
    headerFname = fname + ".header"
    bodyFname = fname + ".body"
    monthlyMsgHeaders = {}
    monthlyMsgBodys = {}
    headerFile = open(headerFname, 'wb')
    bodyFile = open(bodyFname, 'wb')

    for link in msgLinks:
        msgSuffix = link['href']
        msg, body_text = processMessage(url, monthPart, msgSuffix)
        msgId = msgSuffix.split(".")[0]
        monthlyMsgHeaders[msgId] = msg
        monthlyMsgBodys[msgId] = body_text

    pickle.dump(monthlyMsgHeaders, headerFile, pickle.HIGHEST_PROTOCOL)
    pickle.dump(monthlyMsgBodys, bodyFile, pickle.HIGHEST_PROTOCOL)

    bodyFile.close()
    headerFile.close()

    # with open(bodyFname, 'rb') as f:
    #     contents = pickle.load(f)

    # print(contents)
    # print("================")
    # print(monthlyMsgBodys)


def main(outputDir, startMonthIndex=1, exitAfterOne=False):
    print("Starting download from index: {0}".format(startMonthIndex))
    url = 'https://mm.icann.org/pipermail/tz/'
    page = urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')
    rows = soup.table.find_all('tr')
    for index, r in enumerate(rows[startMonthIndex:]):
        cols = r.find_all('td')
        monthSuffix = cols[1].find_all('a')[3]['href']
        print("Index: {0}".format(index + startMonthIndex))
        processMonth(url, monthSuffix, outputDir)
        if (exitAfterOne):
            print("Exiting after one month processing")
            exit()


if __name__ == "__main__":
    outputDir = sys.argv[1]
    # optional month to start, useful when restarting after crash
    index = 1
    exitAfterOne = False
    if len(sys.argv) > 3:
        index = int(sys.argv[2])
        if (sys.argv[3] == "true"):
            exitAfterOne = True
    main(outputDir, index, exitAfterOne)
