import numpy
import os
import csv
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


numremoved = []
Cdata = []
Adata = []
Aprimedata = []
Bdata = []
Adata_penn = []
choppedoffthetopdata = []
choppedoffthetopdata_perchannel = []
choppedoffthetopdata_greedy = []
owned = []
affiliates = []

with open(os.path.join("data", "FromVijay", "choppedoffthetop_removedstationlist.csv"), 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        numremoved.append(int(row[0]))
        choppedoffthetopdata.append(int(row[1]))

for i in range(len(choppedoffthetopdata)):
    if i == 0:
        choppedoffthetopdata_perchannel.append(choppedoffthetopdata[i])
    else:
        choppedoffthetopdata_perchannel.append(choppedoffthetopdata[i] - choppedoffthetopdata[i - 1])

sortedchoppedoffthetopdata_perchannel = sorted(choppedoffthetopdata_perchannel)
sum = 0
for i in range(len(sortedchoppedoffthetopdata_perchannel)):
    sum = sum + sortedchoppedoffthetopdata_perchannel[i]
    choppedoffthetopdata_greedy.append(sum/2173.0)
    choppedoffthetopdata[i] = choppedoffthetopdata[i]/2173.0

with open(os.path.join("data", "FromVijay", "CASEC-new-USMinimumStationstoRemove.csv"), 'rU') as f:
    reader = csv.reader(f)
    for row in reader:
        Cdata.append(int(row[1])/2173.0)

with open(os.path.join("data", "FromVijay", "CASEBUSMinimumStationstoRemove.csv"), 'rU') as f:
    reader = csv.reader(f)
    for row in reader:
        Bdata.append(int(row[1])/2173.0)

with open(os.path.join("data", "FromVijay", "CASEAUSMinimumStationstoRemove.csv"), 'rU') as f:
    reader = csv.reader(f)
    for row in reader:
        Adata.append(int(row[1])/2173.0)
        if int(row[0]) in [10, 12, 13, 14, 19, 20]:
            print (row[4])
            Adata_penn.append(int(row[4])/2173.0)

with open(os.path.join("data", "FromVijay", "APrimeMinimumStationstoRemove.csv"), 'rU') as f:
    reader = csv.reader(f)
    for row in reader:
        Aprimedata.append(int(row[1])/2173.0)


with open(os.path.join("data", "FromVijay", "OwnedNBMinimumStationstoRemove.csv"), 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        owned.append(int(row[1]))

with open(os.path.join("data", "FromVijay", "AffiliatesNBMinimumStationstoRemove.csv"), 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        affiliates.append(int(row[1]))

fig = plt.figure(figsize = (8, 5))

plt.plot(numremoved[0:37], Cdata[0:15] + Cdata[16:], 'b', lw = 3)
plt.plot(numremoved[0:37], Bdata[0:15] + Bdata[16:], 'g', lw = 3)
plt.plot(numremoved[0:37], Adata[0:15] + Adata[16:], 'c', lw = 3)
plt.plot(numremoved[0:37], Aprimedata[0:15] + Aprimedata[16:], 'k', lw = 3)

#plt.plot([10, 12, 13, 14, 18, 19], Adata_penn, 'ko')
plt.plot(numremoved[0:37], choppedoffthetopdata[0:15] + choppedoffthetopdata[16:], 'r', lw = 3)
#plt.plot(numremoved[0:37], choppedoffthetopdata_greedy[1:], 'c', lw = 3)
#plt.plot(range(12), Cdata[0:12], 'k')
#plt.plot(range(12), owned, 'k--', lw = 1)
#plt.plot(range(3), affiliates, 'k*', markersize = 10)
plt.xlabel("Spectrum Clearing Target (Channels)", fontsize = 15)
plt.ylabel("Minimum Fraction of Stations Removed", fontsize = 15)
plt.grid(b=True, color = '0.65', which = 'both', linestyle = '--')
plt.ylim(0, 1)
#plt.xlim(0, 12)
#plt.ylim(0, 100)


blueline = mlines.Line2D([], [], color = 'blue', lw = 3, label = "Repack: Case C")
redline = mlines.Line2D([], [], color = 'red', lw = 3, label = "Naive Reallocation")
greenline = mlines.Line2D([], [], color = 'green', lw = 3, label = "Repack: Case B")
#magentaline = mlines.Line2D([], [], color  = 'magenta', lw = 3, label = "Removing Non-Affiliate Stations (Repacking)")
cyanline = mlines.Line2D([], [], color = 'teal', lw = 3, label = "Repack: Case A")
blackline = mlines.Line2D([], [], color = 'black', label = "Removing Any Stations")
blackdashline = mlines.Line2D([], [], color = 'black', linestyle = '--', label = 'Removing Non-Major Stations')
blackstarline = mlines.Line2D([], [], color = 'black', marker = '*', markersize = 10, label = "Removing Non-Affiliate Stations")

plt.legend(handles = [blueline, redline, greenline, cyanline], fontsize = 10.5)
#plt.legend(loc = 2, handles = [blackline, blackdashline, blackstarline])

#plt.figtext(0.52, 0.34, "Efficient Clearing Method", color = 'blue', fontsize = 15, rotation = 25)
#plt.figtext(0.40, 0.60, "Naive Clearing Method", color = 'red', fontsize = 15, rotation = 30)
#plt.figtext(0.39, 0.61, "Naive Clearing Method with Flexibility", color = 'teal', fontsize = 15, rotation = 30)
plt.show()

#plt.savefig(os.path.join("data", "Miscellaneous Plots", "stationsremovedvschannelsremoved_final.png"))