import sys
from utils import *
from pprint import pprint
import operator
import pickle

zoneErrors = {}

def compareFiles(file1, file2, relTS):
    zones1, rules1 = parseFile(file1)
    zones2, rules2 = parseFile(file2)

    zoneResultsDict = {}

    oldZones = set(zones1.keys())
    newZones = set(zones2.keys())

    zonesAdded = len(newZones - oldZones)
    zonesRemoved = len(oldZones - newZones)

    zoneNames = oldZones.intersection(newZones)

    for zname in zoneNames:
        results = compareZoneData(zname, zones1[zname], rules1, zname, zones2[zname], rules2, relTS)
        zoneResultsDict[zname] = results

    return (zoneResultsDict, zonesAdded, zonesRemoved, oldZones, newZones)

def compareReleases(dir1, dir2, relTS):
    regions = getRegionNames()

    releaseResults = {}
    for reg in regions:
        file1 = dir1 + '/' + reg
        file2 = dir2 + '/' + reg
        # print("comparing files \n{0}\n{1}".format(file1, file2))
        results = compareFiles(file1, file2, relTS)
        releaseResults[reg] = results

    return releaseResults

def getZoneUpdateData(tzDir, mailDir, outFileName):
    sortedDirs = getReleaseNames(tzDir, mailDir)
    releaseDetails = getReleaseDates(tzDir, mailDir)


    relResults = {}
    # range(0, len(sortedDirs) - 1)
    print("Comparing releases...")
    for i in range(0, len(sortedDirs) - 1):
        dir1 = tzDir + '/' + sortedDirs[i][1]
        dir2 = tzDir + '/' + sortedDirs[i+1][1]
        relName = sortedDirs[i+1][1]
        if relName not in releaseDetails:
            relTS = None
        else:
            relTS = releaseDetails[relName][1]

        # print("comparing \n{0}\n{1}".format(dir1, dir2))
        results = compareReleases(dir1, dir2, relTS)
        relResults[sortedDirs[i+1][0]] = results

    outFile = open(outFileName, 'wb')
    pickle.dump(relResults, outFile, pickle.HIGHEST_PROTOCOL)
    outFile.close()
    print("Processed data written to file %s" % outFileName)
    f = open(outFileName, 'rb')
    rel = pickle.load(f)
    # print(rel.keys())
    # print(len(rel.keys()))
    # print(list(rel.values())[0]['northamerica'])


def main():
    tzDir = sys.argv[1]
    mailDir = sys.argv[2]
    outFile = sys.argv[3]
    getZoneUpdateData(tzDir, mailDir, outFile)

if __name__ == "__main__":
    main()
