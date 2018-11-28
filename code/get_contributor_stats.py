import sys
from os import listdir
from os.path import isfile, join
import pickle
import numpy as np
# import operator
from pprint import pprint
from datetime import datetime
import matplotlib.pyplot as plt
plt.style.use('ggplot')
plt.rcParams['axes.facecolor']='w'
from utils import *

def getMsgStats(dirPath, tzDir):
    onlyfiles = [f for f in listdir(dirPath) if isfile(join(dirPath, f))]
    authStats = {}
    msgStats = []
    monthly_volunteer_count = {}
    monthly_msg_count = {}

    for fname in onlyfiles:

        volunteers = set()
        with open(join(dirPath, fname), 'rb') as f:
            monthlyMsgs = pickle.load(f)
            numMsgs = len(monthlyMsgs.keys())
            for mid, m in monthlyMsgs.items():

                sender = m['sender']
                volunteers.add(sender)
                authStats[sender] = authStats.get(sender, 0) + 1

        msgStats.append(numMsgs)


        monthStr = '01-' + fname.split('.')[0]
        dateObj = datetime.strptime(monthStr, "%d-%Y-%B").date()
        monthly_volunteer_count[dateObj] = len(volunteers)
        monthly_msg_count[dateObj] = numMsgs

    numAuths = len(authStats.keys())

    print("Stats for Section 3.2")
    print("-----------------------")

    print("No. of months: {0}".format(len(onlyfiles)))
    print("Total no. of msgs: {0}, Avg. msgs/month: {1}".format(np.sum(msgStats),
                                                         np.mean(msgStats)))
    print("No. of unique contributors: {0}".format(numAuths))

    sorted_months = sorted(monthly_volunteer_count.keys())
    volunteer_counts = [monthly_volunteer_count[m] for m in sorted_months]
    email_counts = [monthly_msg_count[m] for m in sorted_months]

    fig = plt.gcf()
    fig.set_size_inches(6, 3)

    counts = list(authStats.values())
    meanMails = np.sum(msgStats) / numAuths

    morethanOne = [c for c in counts if c > meanMails]
    s_counts = sorted(counts, reverse=True)

    plt.ylabel('CDF', fontsize=18)
    plt.xlabel("No. of e-mails", fontsize=18)
    plotCDF(counts, "E-mails from all contributors")
    plotCDF(morethanOne, "E-mails from frequent contributors", ':')
    plt.legend(loc='best', fancybox=False, ncol=1)
    plt.legend(frameon=False)
    plt.setp(plt.gca().get_legend().get_texts(), fontsize='14')
    ax = plt.gca()
    ax.spines['bottom'].set_color('lightgray')
    ax.spines['left'].set_color('lightgray')
    plt.xticks(size=14)
    plt.yticks(size=14)
    plt.savefig("plots/Figure_5_cdf_emails_sent.eps",
                bbox_inches='tight', format="eps", dpi=1000)

    releaseMails = getReleaseDates(tzDir, dirPath)

    plt.clf()

    fig = plt.gcf()
    fig.set_size_inches(8, 4)
    plt.grid(True)
    plt.xlabel('Time (year)', fontsize=16)
    plt.ylabel("Count", fontsize=16)
    plt.plot(sorted_months, email_counts,
             label="Monthly emails",
             linestyle=':')
    plt.plot(sorted_months, volunteer_counts,
             label="Monthly unique contributors")

    release_ts = []
    for k,i in releaseMails.items():
        release_ts.append(i[1])

    yvals = [0] * len(release_ts)

    plt.legend(loc='best', fancybox=False, ncol=1)
    plt.legend(frameon=False)
    plt.setp(plt.gca().get_legend().get_texts(), fontsize='14')
    ax = plt.gca()
    ax.spines['bottom'].set_color('lightgray')
    ax.spines['left'].set_color('lightgray')
    plt.xticks(size=11)
    plt.yticks(size=11)

    plt.savefig("plots/Figure_4_monthly_unique_contributors_emails.eps",
                bbox_inches='tight', format="eps", dpi=1000)

def main():
    dirPath = sys.argv[1]
    tzDir = sys.argv[2]

    getMsgStats(dirPath, tzDir)



if __name__ == "__main__":
    main()
