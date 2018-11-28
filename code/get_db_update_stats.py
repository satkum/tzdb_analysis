from utils import *
import sys
import pickle
import operator
from pprint import pprint
from intervaltree import IntervalTree
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib import pylab
plt.style.use('ggplot')
plt.rcParams['axes.facecolor']='w'

zoneUpdateRanges = {}
zoneUpdateCounts = {}

def summarizeRelease(relDict, relName):
    regions = getRegionNames()
    totalAdded = 0
    totalRemoved = 0
    zonesUpdated = 0
    dstUpdated = 0
    tzUpdated = 0
    bothUpdated = 0

    pastDates = 0
    futureDates = 0
    overlapDates = 0
    overlapLateDays = []
    futureDeadlineDays = []

    numErrorCorrections = 0
    numExactCorrections = 0
    numOverlapCorrections = 0

    typeDict = []
    ecRanges = []


    for reg in regions:
        regResults = relDict[reg]
        added = regResults[1]
        removed = regResults[2]
        zoneResults = regResults[0]

        totalAdded += added
        totalRemoved += removed

        regionZonesUpdated = 0
        zonedst = 0
        zonetz = 0
        zoneboth = 0

        zonepast = 0
        zonefuture = 0
        zoneoverlap = 0
        futuredays = []
        overlapdays = []

        zoneErrors = 0
        exactErrors = 0
        overlapErrors = 0

        for zname, res in zoneResults.items():
            # if (zname == "Europe/Dublin"):
            #     print("Before")
            #     print(relName)
            #     if zname in zoneUpdateRanges:
            #         pprint(zoneUpdateRanges[zname])
            #     else:
            #         print("Not in interval tree")

            errorCorrection = False
            exact = False
            if res['dstChanged'] or res['tzChanged']:
                regionZonesUpdated += 1
                # This zone is updated, increment count
                zoneUpdateCounts[zname] = zoneUpdateCounts.get(zname, 0) + 1

                if zname not in zoneUpdateRanges:
                    zoneUpdateRanges[zname] = IntervalTree()

                # if zname == "Europe/Dublin":
                #     pprint("Changed : {0}".format(res['ranges']))

                for dateRange in res['ranges']:
                    start = dateRange[0]
                    if start == 0:
                        start = datetime(1, 1, 1, 0, 0, 0)
                    end = dateRange[1]
                    updateType = dateRange[2]
                    vals = zoneUpdateRanges[zname][start:end]
                    relTS = dateRange[3]
                    if len(vals) > 0:
                        errorCorrection = True
                        exact = False
                        ecRanges.append([start, end, updateType, relTS, zname, relName])
                        for v in vals:
                            if v[0] == start and v[1] == end:
                                exact = True
                        # exit()
                        typeDict.append(updateType)

                    # intersectionStart = start if

                    zoneUpdateRanges[zname][start:end] = 1


            if res['dstChanged'] and res['tzChanged']:
                zoneboth += 1
            elif res['dstChanged']:
                zonedst += 1
            elif res['tzChanged']:
                zonetz += 1

            if res['futurePast'][0]:
                zonepast += 1
            if res['futurePast'][1]:
                zonefuture += 1
            if res['futurePast'][2]:
                zoneoverlap += 1

            if res['futurePast'][3] is not None:
                futuredays.append(res['futurePast'][3])

            if res['futurePast'][4] is not None:
                overlapdays.append(res['futurePast'][4])

            # Update error counts
            if errorCorrection:
                zoneErrors += 1
                if exact:
                    exactErrors += 1
                else:
                    overlapErrors += 1


        zonesUpdated += regionZonesUpdated
        dstUpdated += zonedst
        tzUpdated += zonetz
        bothUpdated += zoneboth

        pastDates += zonepast
        futureDates += zonefuture
        overlapDates += zoneoverlap
        overlapLateDays += overlapdays
        futureDeadlineDays += futuredays
        numErrorCorrections += zoneErrors
        numExactCorrections += exactErrors
        numOverlapCorrections += overlapErrors



    results = {}
    results['added'] = totalAdded
    results['removed'] = totalRemoved
    results['zonesUpdated'] = zonesUpdated
    results['dst'] = dstUpdated
    results['tz'] = tzUpdated
    results['both'] = bothUpdated

    results['past'] = pastDates
    results['future'] = futureDates
    results['overlap'] = overlapDates
    results['deadlines'] = futureDeadlineDays
    results['late'] = overlapLateDays

    results['ec'] = numErrorCorrections
    results['ecExact'] = numExactCorrections
    results['ecOverlap'] = numOverlapCorrections

    results['typeDict'] = typeDict
    results['ecRanges'] = ecRanges

    return results

def plotUpdateType(results):
    dst_tz = [np.sum(results['dst']),
              np.sum(results['tz']),
              np.sum(results['both'])]

    labels1 = ["DST rules", "Zone rules", "Both"]

    lines_colour_cycle = [p['color'] for p in plt.rcParams['axes.prop_cycle']]
    explode = (0.05,0.05,0.05)

    past_future = [np.sum(results['past']),
            np.sum(results['future']),
            np.sum(results['overlap'])]

    labels2 = ["Past", "Future", "Both"]

    plt.clf()
    fig, axs = plt.subplots(1, 2)
    fig.set_size_inches(8, 4)
    fig.tight_layout()
    explode = [0.025, 0.025, 0.025]
    patches, texts, autotexts = axs[0].pie(dst_tz, labels=labels1,
                                           autopct='%1.1f%%', startangle=180,
                                           colors = [lines_colour_cycle[0],
                                             lines_colour_cycle[1],
                                             lines_colour_cycle[2]],
                                             explode= explode,
                                             pctdistance=0.49)
    [ _.set_fontsize(14) for _ in texts ]
    [ _.set_fontsize(12) for _ in autotexts ]
    axs[0].axis('equal')

    centre_circle = plt.Circle((0,0),0.70,fc='white')
    axs[0].add_artist(centre_circle)
    explode = [0.025, 0.025, 0.025]
    patches, texts, autotexts = axs[1].pie(past_future, labels=labels2,
                                           autopct='%1.1f%%', startangle=180,
                                           colors = [lines_colour_cycle[4],
                                                     lines_colour_cycle[5],
                                                     lines_colour_cycle[3]],
                                           explode= explode,
                                           pctdistance=0.45)
    [ _.set_fontsize(14) for _ in texts ]
    [ _.set_fontsize(12) for _ in autotexts ]
    axs[1].axis('equal')

    centre_circle = plt.Circle((0,0),0.70,fc='white')
    axs[1].add_artist(centre_circle)

    plt.savefig("plots/Figure_1_distribution_of_updates.eps",
                bbox_inches='tight', format="eps", dpi=1000)


def plotDeadlines(results):
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(6, 3)
    plt.ylabel('CDF', fontsize=18)
    plt.xlabel("No. of days", fontsize=18)
    plotCDF(results['deadlines'], "Days to actual change")

    ax = plt.gca()
    ax.spines['bottom'].set_color('lightgray')
    ax.spines['left'].set_color('lightgray')
    plt.xticks(size=14)
    plt.yticks(size=14)
    # plt.show()

    plt.savefig("plots/Figure_2_cdf_days_release_dates_future_timestamps.eps",
                bbox_inches='tight', format="eps", dpi=1000)

    # consider values only within a year
    lateDays = [l* -1 for l in results['late'] if l >= -365]
    print("No. of late days: {0}, alldelays: {1}".format(
                                                         len(lateDays),
                                                         len(results['late'])))
    plt.clf()
    fig = plt.gcf()
    fig.set_size_inches(6, 3)
    plt.ylabel('CDF', fontsize=18)
    plt.xlabel("No. of days", fontsize=18)
    plotCDF(lateDays, "Days after actual change")

    ax = plt.gca()
    ax.spines['bottom'].set_color('lightgray')
    ax.spines['left'].set_color('lightgray')
    plt.xticks(size=14)
    plt.yticks(size=14)

    plt.savefig("plots/Figure_3_cdf_days_release_dates_past_timestamps.eps",
                bbox_inches='tight', format="eps", dpi=1000)

def convert_lon_lat_points(points, tran):
    # maybe there is a better way to get long/lat into meters but this works ok
    return np.array([tran(lon,lat) for lon,lat in points])

def processUpdateFile(fname, tzDir,mailDir):
    updateFile = open(fname, 'rb')
    releaseStats = pickle.load(updateFile)
    releaseDetails = getReleaseNames(tzDir, mailDir)
    print("Stats for Section 3.1")
    print("-----------------------")
    print("Number of TZDB releases: {0}".format(len(releaseDetails)))

    # print(releaseStats.keys())
    # pprint(releaseStats[rd[0]])
    results = {}
    results['added'] = []
    results['removed'] = []
    results['zonesUpdated'] = []
    results['dst'] = []
    results['tz'] = []
    results['both'] = []

    results['past'] = []
    results['future'] = []
    results['overlap'] = []
    results['deadlines'] = []
    results['late'] = []

    results['ec'] = []
    results['ecExact'] = []
    results['ecOverlap'] = []

    results['typeDict'] = []
    results['ecRanges'] = []
    for rd in releaseDetails:
        if rd[0] not in releaseStats:
            continue
        res = summarizeRelease(releaseStats[rd[0]], rd[0])
        results['added'].append(res['added'])
        results['removed'].append(res['removed'])
        results['zonesUpdated'].append(res['zonesUpdated'])
        results['dst'].append(res['dst'])
        results['tz'].append(res['tz'])
        results['both'].append(res['both'])

        results['past'].append(res['past'])
        results['future'].append(res['future'])
        results['overlap'].append(res['overlap'])
        results['ec'].append(res['ec'])
        results['ecExact'].append(res['ecExact'])
        results['ecOverlap'].append(res['ecOverlap'])

        results['typeDict'] += res['typeDict']
        results['ecRanges'] += res['ecRanges']
        for d in res['deadlines']:
            if d != []:
                results['deadlines'].append(d)

        for l in res['late']:
            if l != []:
                results['late'].append(l)

    print("Total no. of updates: {0}. Updates to, DST Rules: {1}, Zone Rules: {2}, Both: {3}".format(
                np.sum(results['zonesUpdated']),
                np.sum(results['dst']),
                np.sum(results['tz']),
                np.sum(results['both'])
                ))

    print("No. of changes affecting, Past : {0}, Future: {1}, Both: {2}".format(
            np.sum(results['past']),
            np.sum(results['future']),
            np.sum(results['overlap'])
            ))

    plotUpdateType(results)

    plotDeadlines(results)

    print("Total no. of updates: {0}, Error corrections: {1}".format(
                                    np.sum(results['zonesUpdated']),
                                    np.sum(results['ec']),
                                                              ))

    # print("Exact EC: {0}, Overlap EC: {1}".format(
    #                                 np.sum(results['ecExact']),
    #                                 np.sum(results['ecOverlap']),
    #                                                           ))


    sortedRanges = sorted(results['ecRanges'], key = operator.itemgetter(4))

    preDate = datetime(1970, 1, 1, 0, 0, 0)

    pre1970 = []
    post1970 = []

    for f in sortedRanges:
        if f[1] < preDate:
            pre1970.append(f)
        else:
            post1970.append(f)

    print("Total no. of date ranges affted by Error corrections: %d" % len(sortedRanges))

    print(" -- No. of date ranges pre-1970: %d" % len(pre1970))

    print(" -- No. of date ranges post-1970: %d" % len(post1970))


def main():
    updateFileName = sys.argv[1]
    tzDir = sys.argv[2]
    mailDir = sys.argv[3]
    processUpdateFile(updateFileName, tzDir, mailDir)

if __name__ == "__main__":
    main()
