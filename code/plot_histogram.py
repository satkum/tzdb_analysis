from __future__ import division
from utils import *
import matplotlib.pyplot as plt
plt.style.use('ggplot')
plt.rcParams['axes.facecolor']='w'
import sys
from pprint import pprint
import numpy as np
from pytz import country_timezones, country_names
import operator


def calculateRuleHist(start, end, ruleName, rules, hist):
    if ruleName == '-':
        return

    if ruleName not in rules:
        # This is a fixed amount of time for DST. E.g 1:00
        # Just count the start year in the histogram
        hist[start] = hist.get(start, 0) + 1
        return

    for l in rules[ruleName]:
        ruleStartYear = l[0]
        if ruleStartYear >= start and ruleStartYear < end:
            hist[ruleStartYear] = hist.get(ruleStartYear, 0) + 1


def getZoneHist(zoneName, zones, rules):
    parsedRules = getParsedRules(rules)
    years, ruleNames, offsets = processZoneDetails(
        zoneName, zones[zoneName], rules)

    if years == [] and ruleNames == [] and offsets == []:
        print("Empty zone line - Deal with this later")
        return {}

    histogram = {}
    for i in range(0, len(years) - 1):
        start = years[i]
        end = years[i + 1]
        applicableRule = ruleNames[i + 1]

        # offsetChange = 0
        if offsets[i] != offsets[i + 1]:
            # offsetChange = 1
            histogram[start] = histogram.get(start, 0) + 1

        calculateRuleHist(start, end, applicableRule, parsedRules, histogram)

    return histogram


def plotZoneHist(zones, rules, factor, fname):
    zoneHistograms = {}
    yearZones = {}
    names = zones.keys()
    for n in names:
        hist = getZoneHist(n, zones, rules)
        for year, count in hist.items():
            zoneHistograms[year] = zoneHistograms.get(year, 0) + count
            if year in yearZones:
                yearZones[year].append((n, count))
            else:
                yearZones[year] = [(n, count)]

    x = sorted(zoneHistograms.keys())
    y = [zoneHistograms[i] for i in x]
    fig = plt.gcf()
    fig.set_size_inches(9, 5)
    fig.tight_layout()
    plt.grid(True)
    plt.xlabel("Years", fontsize=16)
    plt.ylabel("No. of rules going into effect", fontsize=16)
    plt.plot(x, y, label="No. of rule changes", color='tan', alpha=0.1)

    avgY = np.mean(y) + (factor * np.std(y))
    plt.plot(x, [avgY] * len(y), label="Threshold (Mean + 1 STD)",
             color='gray', linestyle='--')
    textX = []
    textY = []
    for i in range(0, len(y)):
        if y[i] > avgY:
            textX.append(x[i])
            textY.append(y[i])

    # This annotation is specific to North America, please disable when
    # plotting data for other regions.

    annotate_text = ["World War I   ",
                     "World War II  ",
                     "  World War II",
                     "Uniform Time \nAct",
                     "Oil Embargo     \n(Energy Crisis)      ",
                     "Federal Fire\n  Prevention Act   ",
                     "Energy Policy  \nAct   ",
                    ]
    aligns = ["right","right","left", "center", "right", "center", "right"]
    verticals = ["top", "top","top","bottom","bottom","bottom","top"]
    adjust = [0,0,0,1,0,3,0]
    xadjust = [0,0,0,-6,5,5,0]
    for i in range(0, len(textX)):
        plt.text(textX[i] + xadjust[i], textY[i] + adjust[i],annotate_text[i],
                 horizontalalignment=aligns[i],
                 multialignment='center',
                 verticalalignment=verticals[i],
                 size='medium',
                 color='black',
                 weight='medium',
                 style='italic')
        plt.plot(textX[i], textY[i], 'ro')

    timezone_country = {}
    for countrycode in country_timezones:
        timezones = country_timezones[countrycode]
        for timezone in timezones:
            timezone_country[timezone] = countrycode

    print("Data for section 3.3")
    print("---------------------")
    print("Countries with rule changes during years that exceed the threshold no. of rule changes")
    print("(Format - 'country' : no. of rule changes for the year)")
    print("---------------------")
    for year in textX:
        countries = {}
        print("== {0} - No. of rules changes: {1} == ".format(year, zoneHistograms[year]))
        for zone in yearZones[year]:
            if zone[0] not in timezone_country:
                countries[zone[0]] = countries.get(zone[0], 0) + zone[1]
            else:
                cname = country_names[timezone_country[zone[0]]]
                countries[cname] = countries.get(cname, 0) + zone[1]

        pprint(countries)

    plt.legend(loc='upper right', bbox_to_anchor=(0.515, 1.00),
               fancybox=False, ncol=1)
    plt.legend(frameon=False)
    plt.setp(plt.gca().get_legend().get_texts(), fontsize='14')
    ax = plt.gca()
    ax.spines['bottom'].set_color('lightgray')
    ax.spines['left'].set_color('lightgray')
    plt.xticks(size=11)
    plt.yticks(size=11)

    plt.savefig("plots/Figure_6_histogram_of_rule_changes_{0}.eps".format(fname),
                bbox_inches='tight', format="eps", dpi=1000)


if __name__ == "__main__":
    fname = sys.argv[1]
    zones, rules = parseFile(fname)

    # Set threshold factor to 1 (i.e) mean + 1 STD
    factor = 1
    fn = fname.split('/')[-1]
    plotZoneHist(zones, rules, factor, fn)
