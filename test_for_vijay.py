import csv
import numpy
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.lines as mlines
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

def get_heat_map(csvfilename):

    csvfile = "".join([csvfilename, ".csv"])


    heatmaplists = []
    with open(os.path.join("data", "FromVijay", csvfile), 'r') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            count = count + 1
            if count == 1:
                continue
            for i in range(len(row)):
                row[i] = int(row[i])
            heatmaplists.append(row)

    heatmaplists = sorted(heatmaplists)
    xlen = len(heatmaplists)
    ylen = len(heatmaplists[0]) - 1
    heatmap = numpy.zeros((xlen, ylen))
    for i in range(xlen):
        for j in range(ylen):
            heatmap[i][j] = heatmaplists[i][j + 1]



    fig = plt.figure()
    ax = fig.add_subplot(111)
    c_map = cm.Greys
    c_map.set_over('w')
    #c_map.set_under('b')
    img = ax.imshow(heatmap, cmap = c_map, vmin = 0, vmax = 1, interpolation = 'nearest', aspect = 'auto')
    #plt.gca().invert_yaxis() If you want.
    plt.xlabel("Xlabel")
    #plt.xticks([0, 10, 20, 30, 40, 50])
    plt.ylabel("Ylabel")
    fig.colorbar(img)
    #plt.yticks([0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200])
    plt.savefig(os.path.join("data", "For Vijay", "".join([csvfilename, ".png"])))

def get_bar_chart_by_column(csvfilename):
    csvfile = "".join([csvfilename, ".csv"])
    sumcols = {}
    with open(os.path.join("data", "FromVijay", csvfile), 'r') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            count = count + 1
            if count == 1:
                channelindexes = row[2:]
                print (channelindexes)
                for c in channelindexes:
                    c = int(c)
                    sumcols[c] = 0
                continue
            for i in range(2, len(row)):
                row[i] = int(row[i])
                sumcols[i] = sumcols[i] + row[i]

    print sumcols.values()

    plt.figure(figsize = (9, 5))

    plt.bar(sumcols.keys(), sumcols.values(), linewidth = 0)
    plt.bar(sumcols.keys()[12:19], sumcols.values()[12:19], color = 'r', linewidth = 0)
    plt.xlabel("Channel number")
    plt.ylabel("Number of stations")
    plt.xlim(0, 50)
    plt.show()

def get_bar_chart_by_row(csvfilename):
    csvfile = "".join([csvfilename, ".csv"])
    sumrows = {}
    with open(os.path.join("data", "FromVijay", csvfile), 'r') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            count = count + 1
            if count == 1:
                continue
            sumrows[row[0]] = -1
            for i in range(1, len(row)):
                sumrows[row[0]] = sumrows[row[0]] + int(row[i])
    print (sumrows.values())
    if 1 in sumrows.values():
        print "1 is present"
    if 10 in sumrows.values():
        print "10 is present"
    plt.figure(figsize = (9, 5))
    plt.hist(sumrows.values(), bins = 50, log = True, edgecolor = 'white' )
    plt.xlabel("Domain size")
    plt.ylabel("Number of stations")
    plt.show()














