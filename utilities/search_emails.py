import sys
from os import listdir
from os.path import isfile, join
import pickle
import operator
from pprint import pprint


def getMsgStats(dirPath, error_words, max_matches = 20):
    onlyfiles = [f for f in listdir(dirPath) if isfile(join(dirPath, f))]
    emailCounts = {}
    counter = 0
    pcounter = 0
    #nci_emails = set()
    # error_words = ["error", "bug", "correction",
    #                 "work around", "mistake", "wrong", "crash", "issue"]
    # error_words = ['games', 'ramadan', 'game', 'festival', 'cup', 'olympics']
    # error_words = ['server', "mail server", "mailing list"]
    for fname in onlyfiles:
        print(fname)
        with open(join(dirPath, fname), 'rb') as f:
            monthlyMsgs = pickle.load(f)
            for mid, m in monthlyMsgs.items():
                # emailId = m['email']
                # print(emailId)
                if pcounter >= max_matches:
                    print("{0} matches found".format(max_matches))
                    exit()
                try:
                    # domain = emailId.split(' ')[2]
                    # if "nci.nih.gov" in domain:
                    #     nci_emails.add(emailId)
                    # if "apple" in domain:
                    #     print(m['subject'])
                    for w in error_words:
                        if w in m['subject'].lower():
                            print(m['subject'])
                            pcounter += 1

                    # emailCounts[domain] = emailCounts.get(domain, 0) + 1
                except Exception:
                    # print("ERROR Id : {0}".format(emailId))
                    counter += 1

    sorted_domains = sorted(emailCounts.items(), key=operator.itemgetter(1), reverse=True)
    # print(sorted_domains)
    # for item in sorted_domains:
    #     if item[1] < 50:
    #         break
    #     print("{0} => {1}".format(item[0], item[1]))

    # print("Fin val {0}".format(len(emailCounts.keys())))
    # print(nci_emails)

def processBodyText(dirPath, error_words, max_matches = 20):
    onlyfiles = [f for f in listdir(dirPath) if isfile(join(dirPath, f))]
    emailCounts = {}
    counter = 0
    pcounter = 0
    nci_emails = set()
    # error_words = ["error", "bug", "correction",
    #                 "work around", "mistake", "wrong", "crash", "issue"]
    # error_words = ['games', 'ramadan', 'game', 'festival', 'cup', 'footbal']
    for fname in onlyfiles:
        print(fname)
        with open(join(dirPath, fname), 'rb') as f:
            monthlyMsgs = pickle.load(f)
            for mid, m in monthlyMsgs.items():
                # emailId = m['email']
                # print(emailId)
                if pcounter >= max_matches:
                    print("{0} matches found".format(max_matches))
                    exit()
                try:
                    # domain = emailId.split(' ')[2]
                    # if "nci.nih.gov" in domain:
                    #     nci_emails.add(emailId)
                    # if "apple" in domain:
                    #     print(m['subject'])
                    for w in error_words:
                        if w in m.lower():
                            pprint(m)
                            print("===================================")
                            pcounter += 1

                    # emailCounts[domain] = emailCounts.get(domain, 0) + 1
                except Exception:
                    # print("ERROR Id : {0}".format(emailId))
                    counter += 1

def main():
    dirPath = sys.argv[1]
    ptype = sys.argv[2]
    print(dirPath)

    keywords = sys.argv[3].split(",")
    max_matches = 20

    if len(sys.argv) > 4:
        max_matches = int(sys.argv[4])
        print("Will only print {0} matches:".format(max_matches))

    if ptype == "body":
        processBodyText(dirPath, keywords, max_matches)
    elif ptype == "subject":
        # search subject lines
        getMsgStats(dirPath, keywords, max_matches)


if __name__ == "__main__":
    main()
