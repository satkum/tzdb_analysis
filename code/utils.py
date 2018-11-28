from __future__ import division
from pprint import pprint
import numpy as np
from os import listdir
from os.path import isfile, join
from datetime import datetime, date, timedelta
import sys, calendar, operator, pickle
import matplotlib.pyplot as plt
import re


releaseDataFName = "./data/releaseDates.pkl"

def parserLatlon(s):
    p = re.compile(r'\+|\-')
    string = s[1:]
    index = p.search(string).span()[1]
    raw_lat = int(s[:index])
    raw_lon = int(s[index:])

    if raw_lat < 10000 and raw_lat > -10000:
        divisor = 100
    else:
        divisor = 10000
    lat = raw_lat / divisor
    lon = raw_lon / divisor

    return (lat, lon)

def getZoneGeos(zonetab = "./data/tz_data_extracted/tzdata2018e/zone1970.tab"):
    lines = 0
    geoZones = {}
    with open(zonetab, 'r') as f:
        for l in f:
            if l.startswith('#'):
                continue
            parts = l.split('\t')
            lat, lon = parserLatlon(parts[1])
            zname = parts[2].strip()
            geoZones[zname] = (lat, lon)

    return geoZones

def plotCDF(data1, lbl, style = None):
    sorted_data1 = np.sort(np.asarray(data1))
    x1 = []
    y1 = []

    y = 0
    for x in sorted_data1:
        x1.extend([x, x])
        y1.append(y)
        y += 1.0 / len(data1)
        y1.append(y)

    if style is None:
        plt.plot(x1, y1, label=lbl)
    else:
        plt.plot(x1, y1, label=lbl, linestyle=style, linewidth=3)


def checkFuturePastUpdates(ranges, releaseDate):
    past = False
    future = False
    overlap = False
    futureDays = None
    overlappingDays = None

    if releaseDate is None:
        return (past, future, overlap, futureDays, overlappingDays)

    strictlyPast = []
    strictlyFuture = []
    overlapping = []
    for idx, item in enumerate(ranges):
        start = item[0]
        end = item[1]

        try:
            if end < releaseDate:
                strictlyPast.append((start,end))
            elif start > releaseDate:
                strictlyFuture.append((start, end))
            else:
                overlapping.append((start,end))
        except Exception as e:
            if start == 0 and end == datetime(9999, 1, 1, 0, 0):
                # This is a change that affects all time
                return (False, False, True, None, None)
            print(e)
            pprint(ranges)
            print(releaseDate)
            return None

    if len(strictlyPast) > 0:
        past = True
    if len(strictlyFuture) > 0:
        future = True
        delta = strictlyFuture[0][0] - releaseDate
        futureDays = delta.days
    if len(overlapping) > 0:
        overlap = True
        delta = overlapping[0][0] - releaseDate
        overlappingDays = delta.days
        if len(overlapping) > 1:
            print("> 1 overlapping")


        # if end > releaseDate:
        #     future = True
        #     if not daysSet:
        #         delta = end - releaseDate
        #         days = delta.days
        #         daysSet = True
        # else:
        #     past = True

    # print(strictlyFuture)
    # print(strictlyPast)
    # print(overlapping)

    # print(past)
    # print(future)

    return (past, future, overlap, futureDays, overlappingDays)

def checkForChanges(years1, ruleNames1, offsets1,
                    years2, ruleNames2, offsets2, relTS):

    dstChanged = False
    tzChanged = False

    # print("+++++++++++++")
    # pprint(years1)
    # pprint(years2)

    ranges = []
    # For each rule line in new zone info, check with applicable rule
    # line in old zone info
    try:
        for i, year in enumerate(years2):
            changed = False
            j = 0
            while (years1[j] < year):
                j += 1
                if j == len(years1) and years1[j-1] < year:
                    # We've reached the end of list one
                    # but found no applicable year so treat this
                    # as applicable year
                    print("update added a new year range")
                    # pprint(years1)
                    # pprint(years2)
                    j -= 1
                    break


            if ruleNames2[i] != ruleNames1[j]:
                dstChanged = True
                changed = True
                # print("1:DST changed: {0} <> {1}".format(
                #                                          ruleNames1[j],
                #                                          ruleNames2[i]))

            if offsets2[i] != offsets1[j]:
                tzChanged = True
                changed = True
                # print("2:TZ changed")

            if changed:
                # Something changed, note the year range
                if i == 0:
                    start = 0
                else:
                    start = years2[i-1]

                end = year

                if dstChanged and tzChanged:
                    reason = 'b'
                elif dstChanged:
                    reason = 'd'
                elif tzChanged:
                    reason = 't'

                ranges.append((start,end,reason,relTS))

                # print("Changed: [{0} - {1}]".format(start, end))
    except Exception as e:
        print("Error: {0}".format(e))
        print("Set1: {0}".format(z1))
        pprint(z1Lines)
        pprint(years1)
        pprint(ruleNames1)
        pprint(offsets1)
        print("Set2: {0}".format(z2))
        pprint(z2Lines)
        pprint(years2)
        pprint(ruleNames2)
        pprint(offsets2)
        exit()

    # if ranges != []:
    #         print("Set1")
    #         pprint(years1)
    #         pprint(ruleNames1)
    #         pprint(offsets1)
    #         print("Set2")
    #         pprint(years2)
    #         pprint(ruleNames2)
    #         pprint(offsets2)
    #         print("ranges")
    #         pprint(ranges)

    return (dstChanged, tzChanged, ranges)

def compareZoneData(z1, z1Lines, rules1, z2, z2Lines, rules2, relTS):
    years1, ruleNames1, offsets1, ts1 = processZoneDetails(z1, z1Lines,
                                                           rules1, True)
    years2, ruleNames2, offsets2, ts2 = processZoneDetails(z2, z2Lines,
                                                           rules2, True)

    # pprint(ts1)
    # pprint(years1)
    # pprint(ts2)
    # pprint(years2)

    dstChanged = False
    tzChanged = False
    dataRemoved = False
    ranges = None

    z1RuleNames = set(ruleNames1)
    z2RuleNames = set(ruleNames2)
    z1RuleLines = []
    for r in z1RuleNames:
        if r in rules1:
            for rLine in rules1[r]:
                # Use split to eliminate whitespace char changes
                # we don't want to count those changes
                # hence,r ules1[r].split()
                parts = rLine.split('#')[0].split()
                z1RuleLines.append(parts)

    z2RuleLines = []
    for r in z2RuleNames:
        if r in rules2:
            for rLine in rules2[r]:
                # Use split to eliminate whitespace char changes
                # we don't want to count those changes
                # hence,r ules1[r].split()
                parts = rLine.split('#')[0].split()
                z2RuleLines.append(parts)

    # print("Rules 1")
    # pprint(z1RuleLines)
    # print("Rules 2")
    # pprint(z2RuleLines)
    # if the rule Lines had changed, then it is a dst update
    if (z1RuleLines != z2RuleLines):
        dstChanged = True

    dstChangedDetected, tzChangedDetected, ranges = checkForChanges(ts1,
     ruleNames1, offsets1, ts2, ruleNames2, offsets2, relTS)

    if tzChangedDetected:
        tzChanged = True
    if dstChangedDetected:
        dstChanged = True

    if (not dstChangedDetected and not tzChangedDetected):
        #Year ranges cound have been removed
        # print("Calling reverse")
        dstRemoved, tzRemoved, ranges = checkForChanges(ts2, ruleNames2, offsets2, ts1, ruleNames1, offsets1, relTS)

        if dstRemoved or tzRemoved:
            dataRemoved = True
            dstChanged = dstRemoved
            tzChanged = tzRemoved



    # Edge case, only the applicable year was changed
    if len(years1) == len(years2) and years1 != years2:
        tzChanged = True

    results = {}
    results['dstChanged'] = dstChanged
    results['tzChanged'] = tzChanged
    results['dataRemoved'] = dataRemoved
    results['ranges'] = ranges
    fp = checkFuturePastUpdates(ranges, relTS)
    if fp is None:
        pprint((z1, z1Lines, z2, z2Lines))
        exit()
    results['futurePast'] = fp

    # print("in compare")
    # print(results)

    return results


def getParsedRules(rules):
    parsedRules = {}
    for ruleName in rules.keys():
        parsedRules[ruleName] = []
        ruleLines = rules[ruleName]
        for line in ruleLines:
            parts = line.split()
            start = int(parts[2])
            end = parts[3]
            if end == 'only':
                end = start
            elif end == 'max':
                end = 10000
            else:
                end = int(end)
            parsedRules[ruleName].append([start, end])

    return parsedRules

def getRegionNames():
    regions = ['africa', 'antarctica', 'asia', 'australasia', 'europe', 'northamerica', 'southamerica']
    return regions

def getReleaseNames(tzDir, mailDir):
    names = []
    for tdir in listdir(tzDir):
        parts = tdir.split('tzdata')
        n = parts[1]
        if (len(n) < 5):
            n = '19' + n
        if 'beta' in n:
            continue
        names.append([n, tdir])

    releaseDetails = getReleaseDates(tzDir, mailDir)

    for n in names:
        dirName = n[1]
        if dirName not in releaseDetails:
            release_ts = None
        else:
            release_ts = releaseDetails[dirName][1]

        n.append(release_ts)

    sortedNames = sorted(names, key=operator.itemgetter(0))
    return sortedNames

def findOccurences(s, ch):
    return [i for i, letter in enumerate(s) if letter == ch]

def getParts(string):
    q = findOccurences(string, '"')
    newString = string
    if len(q) == 2:
        newString = string[:q[0]] + string[q[0]:q[1]].replace(' ', '_') + string[q[1]:]
    return newString.split()

def getMonth(monthStr):
    return datetime.strptime(monthStr, "%b").month

def getTS(year, monthStr="Jan", day=1, hr=0, mn=0, sec=0):
    if monthStr is None:
        monthStr= "Jan"

    if day is None:
        day = 1

    month = getMonth(monthStr)
    ts = datetime(year, month, day, hr, mn, sec)
    return ts


def getDay(dayStr, monthStr, year):
    dayToNum = {'Mon': 0, 'Tue': 1, 'Wed': 2,
                'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}

    month = getMonth(monthStr)
    year = int(year)
    lastDay = calendar.monthrange(year, month)[1]
    lastDate = date(year, month, lastDay)
    if 'last' in dayStr:
        dayName = dayStr.split('last')[1]
        targetDay = dayToNum[dayName]
        candiDate = lastDate # Ha ha
        while(candiDate.weekday() != targetDay):
            candiDate -= timedelta(days=1)

        return candiDate.day
    elif '>=' in dayStr:
        parts = dayStr.split('>=')
        dayName = parts[0]
        limitDay = int(parts[1])
        targetDay = dayToNum[dayName]
        candiDate = date(year, month, limitDay)
        while(candiDate.weekday() != targetDay):
            candiDate += timedelta(days=1)

        return candiDate.day
    elif '<=' in dayStr:
        parts = dayStr.split('<=')
        dayName = parts[0]
        limitDay = int(parts[1])
        targetDay = dayToNum[dayName]
        candiDate = date(year, month, limitDay)
        while(candiDate.weekday() != targetDay):
            candiDate -= timedelta(days=1)
        return candiDate.day
    else:
        return int(dayStr)


def processZoneDetails(zoneName, zoneLines, rules, parseTS=False):

    years = []
    ruleNames = []
    offsets = []
    timestamps = []
    zoneInfo = [z.split('#')[0] for z in zoneLines if len(z.split('#')[0].split()) != 0]
    if len(zoneInfo) == 0:
        if parseTS:
            return ([], [], [], [])
        else:
            return ([], [], [])
    if len(zoneInfo) == 1:
        parts = getParts(zoneInfo[0])
        ruleNames.append(parts[3])
        offsets.append(parts[2])
        if len(parts) > 5:
            year = int(parts[5])
        else:
            # The zone line is applicable for max years
            year = 9999
        if len(parts) > 6:
            month = parts[6]
        else:
            month = None
        if len(parts) > 7:
            day = getDay(parts[7], month, year)
        else:
            day = None

        years.append(year)
        timestamps.append(getTS(year, month, day))

        if parseTS:
            return (years, ruleNames, offsets, timestamps)
        else:
            return (years, ruleNames, offsets)

    firstline = zoneInfo[0]
    parts = getParts(firstline)
    # print("first line")
    # print(parts)
    try:

        ruleNames.append(parts[3])
        offsets.append(parts[2])
        if len(parts) < 6:
            year = 9999  # big value for 'max' year
        else:
            year = int(parts[5])

        if len(parts) > 6:
            month = parts[6]
        else:
            month = None

        if len(parts) > 7:
            day = getDay(parts[7], month, year)
        else:
            day = None

        years.append(year)
        timestamps.append(getTS(year, month, day))
    except Exception as e:
        print("===== ERROR1 : {0} =====".format(e))
        print(parts)
        print(len(parts))
        pprint(zoneInfo)
        exit()

    # print("other lines")
    for line in zoneInfo[1:]:
        parts = getParts(line)

        # print(parts)
        if len(parts) < 3:
            print("Suspect empty line: {0}".format(zoneName))
            continue
        try:
            offsets.append(parts[0])
            ruleNames.append(parts[1])
            if len(parts) < 4:
                year = 9999  # big value for 'max' year
            else:
                year = int(parts[3])

            if len(parts) > 4:
                month = parts[4]
            else:
                month = None

            if len(parts) > 5:
                day = getDay(parts[5], month, year)
            else:
                day =  None

            years.append(year)
            timestamps.append(getTS(year, month, day))
        except Exception as e:
            print("===== ERROR2 : {0} =====".format(e))
            print(parts)
            pprint(zoneInfo)
            exit()

    # pprint(years)
    # pprint(ruleNames)

    # pprint(rules['US'])
    # pprint(rules['Chicago'])

    if parseTS:
        return (years, ruleNames, offsets, timestamps)
    else:
        return (years, ruleNames, offsets)

def getParsedRules(rules):
    parsedRules = {}
    for ruleName in rules.keys():
        parsedRules[ruleName] = []
        ruleLines = rules[ruleName]
        for line in ruleLines:
            parts = line.split()
            start = int(parts[2])
            end = parts[3]
            if end == 'only':
                end = start
            elif end == 'max':
                end = 10000
            else:
                end = int(end)
            parsedRules[ruleName].append([start, end])

    return parsedRules


def parseFile(filename):
    regionNum = 0
    zoneStart = False
    zones = {}
    rules = {}
    zoneName = ""
    newRegion = False
    with open(filename, 'r', encoding='latin-1') as f:
        for line in f:
            if newRegion:
                newRegion = False
            if line.startswith("###"):
                regionNum += 1
                newRegion = True
            # process zone and rule lines
            if line.startswith("Zone"):
                zoneStart = True
                try:
                    zoneName = line.split()[1]
                except Exception as e:
                    if False:
                        print(e)

                zones[zoneName] = []

            elif line.startswith("#"):
                continue
            elif (line.startswith("Rule") or
                  line.startswith("Link") or
                  line == "" or
                  line == "\n"):
                zoneStart = False

            if zoneStart:
                zones[zoneName].append(line)

            if line.startswith("Rule"):
                ruleName = line.split()[1]

                if ruleName not in rules:
                    rules[ruleName] = []

                rules[ruleName].append(line)

    return zones, rules

def saveReleaseDates(tzDir, mailDir):
    tsFormatStr = "%a %b %d %H:%M:%S %Z %Y"
    releaseNames = listdir(tzDir)
    onlyfiles = [f for f in listdir(mailDir) if isfile(join(mailDir, f))]
    suspects = ['1999i', '2008e', '2010k', '2013d', '2013e', '2012a', '2014g', '2018b', '2018e', '2018a', '2017b']


    # Record all mail subject lines that include release names
    # and the timestamps
    releaseMails = {}
    for fname in onlyfiles:
        with open(join(mailDir, fname), 'rb') as f:
            monthlyMsgs = pickle.load(f)

            for mid, m in monthlyMsgs.items():
                subject = m['subject']
                for releaseName in releaseNames:
                    partName = releaseName.split('tzdata')[1]
                    if releaseName in subject or partName in subject:
                        ts = datetime.strptime(m['timestamp'], tsFormatStr)
                        if releaseName in releaseMails:
                            ots = releaseMails[releaseName][1]
                            if ts < ots and (m['sender'] == 'Paul Eggert' or 'lson' in m['sender']):
                                releaseMails[releaseName] = (m, ts)
                        else:
                            releaseMails[releaseName] = (m, ts)

    misses = []
    for r in releaseNames:
        if r not in releaseMails:
            partName = r.split('tzdata')[1]
            misses.append(partName)

    manual_check = misses + suspects

    manual_ts = ['Mon Jul 26 15:09:45 UTC 2010','Thu Mar 23 07:11:46 UTC 2017',
     'Fri May  4 00:22:20 UTC 2018', 'Thu Mar  1 17:54:48 UTC 2012',
     'Fri Sep 20 16:17:08 UTC 2013', 'Sat Aug 30 18:08:36 UTC 2014']
    manual = {}
    for fname in onlyfiles:
        with open(join(mailDir, fname), 'rb') as f:
            monthlyMsgs = pickle.load(f)

            for mid, m in monthlyMsgs.items():
                subject = m['subject']
                ts = datetime.strptime(m['timestamp'], tsFormatStr)
                for name in manual_check:
                    relName = 'tzdata' + name
                    if name in subject:
                        if name == '2008e' and 'Olson' in m['sender']:
                            releaseMails[relName] = (m, ts)
                        elif m['timestamp'] in manual_ts :
                            releaseMails[relName] = (m, ts)

    # print("Candidate msgs : {0}".format(len(releaseMails.keys())))
    # print("Num. release : {0}".format(len(releaseNames)))


    rNameFile = open(releaseDataFName, 'wb')
    pickle.dump(releaseMails, rNameFile, pickle.HIGHEST_PROTOCOL)
    rNameFile.close()

    print("Release dates saved to: {0}".format(releaseDataFName))


def getReleaseDates(tzDir, mailDir):

    if not isfile(releaseDataFName):
        saveReleaseDates(tzDir, mailDir)

    f = open(releaseDataFName, 'rb')
    releaseDates = pickle.load(f)
    f.close()

    return releaseDates

def main():
    usecase = sys.argv[1]

    if usecase == 'print':
        fname = sys.argv[2]
        zname = sys.argv[3]
        zones, rules = parseFile(fname)
        pprint(zones[zname])
        years, ruleNames, offsets = processZoneDetails(zname, zones[zname], rules)
        pprint(years)
        pprint(ruleNames)
        pprint(offsets)
        if len(sys.argv) == 5:
            pprint(rules[sys.argv[4]])

    elif usecase == 'compare':
        file1 = sys.argv[2]
        file2 = sys.argv[3]
        tzDir = sys.argv[4]
        mailDir = sys.argv[5]
        relName = sys.argv[6]
        zoneNames = sys.argv[7].split(',')

        zones1, rules1 = parseFile(file1)
        zones2, rules2 = parseFile(file2)

        releaseDates = getReleaseDates(tzDir, mailDir)

        # for i, (r, val) in enumerate(releaseDates.items()):
        #     print("{0} , {1}".format(r,val[1]))
        names = getReleaseNames(tzDir, mailDir)
        # pprint(names[:10])
        releaseDetails = getReleaseDates(tzDir, mailDir)
        # print("-----------")
        # pprint(list(releaseDetails.values())[:3])
        relTS = None
        for n in names:
            if n[0] == relName:
                relTS = n[2]

        print("RelTS")
        print(relTS)

        for zname in zoneNames:
            results = compareZoneData(zname, zones1[zname], rules1, zname, zones2[zname], rules2, relTS)
            print(zname)
            pprint(results)


        # print(results['ranges'])
        pprint(checkFuturePastUpdates(results['ranges'], relTS))
        # pprint(names)

    elif usecase == 'getDay':
        condstr = sys.argv[2]
        monthStr = sys.argv[3]
        year = int(sys.argv[4])
        print(getDay(condstr, monthStr, year))

    else:
        print("Use case string not valid")


if __name__ == "__main__":
    main()

