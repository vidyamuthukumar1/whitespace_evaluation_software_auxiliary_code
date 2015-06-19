import csv
import numpy
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.lines as mlines
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

def create_fidmappedtoband_csv():
    import west.region_united_states
    import protected_entities_tv_stations_vidya

    testreg = west.region_united_states.RegionUnitedStates()
    good_facility_ids = []
    with open(os.path.join("data", "FromVijay", "C-All free", "C-15ChannelsRemoved", "15VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            good_facility_ids.append(row[0])

    tvstationlist = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(testreg)
    tvstationlist.prune_data(good_facility_ids)

    with open(os.path.join("data", "FromVijay", "fids_mapped_to_band.csv"), 'w') as f:
        writer = csv.writer(f)
        for s in tvstationlist.stations():
            if s.get_channel() < 7:
                band = 'LV'
            elif s.get_channel() < 14:
                band = 'HV'
            else:
                band = 'U'
            writer.writerow([s.get_facility_id(), band])



def make_plot(csvfilename, domainfilename, max_val, num_channels_cleared, segregate_bands = True, white_bg=False, black_bg=False, gray=False, show_colorbar=False):

    csvfile = "".join([csvfilename, ".csv"])
    domainfile = "".join([domainfilename, ".csv"])


    if segregate_bands:
        fids_mapped_to_band = {}
        with open(os.path.join("data", "FromVijay", "fids_mapped_to_band.csv"), 'r') as g:
            reader = csv.reader(g)
            for row in reader:
                fids_mapped_to_band[row[0]] = row[1]
        heatmaplists = {'LV': [], 'HV': [], 'U': []}
        with open(csvfile, 'r') as f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                count = count + 1
                if count == 1:
                    continue
                for i in range(len(row)):
                    row[i] = int(row[i])
                heatmaplists[fids_mapped_to_band[str(row[0])]].append(row)


        heatmaps = {}
        ylen = len(heatmaplists['LV'][0]) - 1
        for k in heatmaplists.keys():
            heatmaplists[k] = sorted(heatmaplists[k])
            xlen = len(heatmaplists[k])
            heatmaps[k] = numpy.zeros((xlen, ylen))
            for i in range(xlen):
                for j in range(ylen):
                    heatmaps[k][i][j] = heatmaplists[k][i][j + 1]

        domainlists = {'LV': [], 'HV': [], 'U': []}
        with open(domainfile, 'r') as f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                count = count + 1
                if count == 1:
                    continue
                for i in range(len(row)):
                    row[i] = int(row[i])
                domainlists[fids_mapped_to_band[str(row[0])]].append(row)

        domainmaps = {}
        for k in domainlists.keys():
            xlen = len(domainlists[k])
            domainmaps[k]  = numpy.zeros((xlen, ylen))
            for i in range(xlen):
                for j in range(ylen):
                    domainmaps[k][i][j] = domainlists[k][i][j + 1]

        for k in heatmaps.keys():
            xlen = len(domainlists[k])
            for i in range(xlen):
                for j in range(ylen):
                    if domainmaps[k][i][j] == 0:
                        heatmaps[k][i][j] = max_val + 1

        gapmatrix = numpy.ones((25, ylen)) * numpy.inf


        heatmapoverall = numpy.concatenate([heatmaps['LV'], gapmatrix, heatmaps['HV'], gapmatrix, heatmaps['U']])

        fig = plt.figure()
        ax = fig.add_subplot(111)
        #ax = [fig.add_subplot(311), fig.add_subplot(312), fig.add_subplot(313)]
        c_map = cm.jet
        if gray:
            c_map = cm.Greys
            heatmap = 1-heatmap
        if white_bg:
            c_map.set_over('w')
        if black_bg:
            c_map.set_under('0.75')
            c_map.set_over('k')
        #c_map.set_under('b')
        count = 0
        ax.imshow(heatmapoverall, cmap = c_map, vmin = 0.1, vmax = max_val, interpolation = 'nearest', aspect = 'auto')
        ax.set_xlabel("Channel number")
        ax.set_yticks([25, 350, 1500])
        ax.set_yticklabels(["Low VHF", "High VHF", "UHF"])
        ax.set_xticks([0, 10, 20, 30, 40, 50])
        ax.set_xticklabels(['R', 10, 20, 30, 40, 50])
        """for k in heatmaps.keys():
            ax[count].imshow(heatmaps[k], cmap = c_map, vmin = 0.1, vmax = max_val, interpolation = 'nearest', aspect = 'auto')
            count = count + 1"""
        #plt.gca().invert_yaxis() If you want.
        """ax[2].set_xlabel("Channel number")
        for count in range(3):
            ax[count].set_xticks([0, 10, 20, 30, 40, 50])
            ax[count].set_xticklabels(['H', 10, 20, 30, 40, 50])
        #plt.xticks([0, 10, 20, 30, 40, 50])
        ax[0].set_ylabel("Stations")
        ax[0].set_yticks([])
        ax[1].set_yticks([])
        ax[2].set_yticks([])"""
        if show_colorbar:
            fig.colorbar(img)
        #plt.yticks([0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200])


    else:
        heatmaplists = []
        with open(csvfile, 'r') as f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                count = count + 1
                if count == 1:
                    continue
                for i in range(len(row)):
                    row[i] = int(row[i])
                heatmaplists.append(row)

        domainlists = []
        with open(domainfile, 'r') as f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                count = count + 1
                if count == 1:
                    continue
                for i in range(len(row)):
                    row[i] = int(row[i])
                domainlists.append(row)

        ylen = len(heatmaplists[0]) - 1
        heatmaplists = sorted(heatmaplists)
        xlen = len(heatmaplists)
        heatmaps = numpy.zeros((xlen, ylen))
        for i in range(xlen):
            for j in range(ylen):
                heatmaps[i][j] = heatmaplists[i][j + 1]


        xdlen = len(domainlists)
        domainmaps = numpy.zeros((xdlen, ylen))
        for i in range(xdlen):
            for j in range(ylen):
                domainmaps[i][j] = domainlists[i][j + 1]

        for i in range(min(xdlen, xlen)):
            for j in range(ylen):
                if domainmaps[i][j] == 0:
                    heatmaps[i][j] = max_val + 1
                if j > 52 - num_channels_cleared:
                    heatmaps[i][j] = numpy.inf

        fig = plt.figure()
        ax = fig.add_subplot(111)
        #ax = [fig.add_subplot(311), fig.add_subplot(312), fig.add_subplot(313)]
        c_map = cm.jet
        if gray:
            c_map = cm.Greys
            heatmap = 1-heatmaps
        if white_bg:
            c_map.set_over('w')
        if black_bg:
            c_map.set_under('0.75')
            c_map.set_over('k')
        #c_map.set_under('b')
        count = 0
        img = ax.imshow(heatmaps, cmap = c_map, vmin = 0.1, vmax = max_val, interpolation = 'nearest', aspect = 'auto')
        ax.set_xlabel("Channel number")
        ax.set_yticks([])
        ax.set_ylabel("Stations")
        ax.set_xticks([0, 10, 20, 30, 40, 50])
        ax.set_xticklabels(['R', 10, 20, 30, 40, 50])
        """for k in heatmaps.keys():
            ax[count].imshow(heatmaps[k], cmap = c_map, vmin = 0.1, vmax = max_val, interpolation = 'nearest', aspect = 'auto')
            count = count + 1"""
        #plt.gca().invert_yaxis() If you want.
        """ax[2].set_xlabel("Channel number")
        for count in range(3):
            ax[count].set_xticks([0, 10, 20, 30, 40, 50])
            ax[count].set_xticklabels(['H', 10, 20, 30, 40, 50])
        #plt.xticks([0, 10, 20, 30, 40, 50])
        ax[0].set_ylabel("Stations")
        ax[0].set_yticks([])
        ax[1].set_yticks([])
        ax[2].set_yticks([])"""
        if show_colorbar:
            fig.colorbar(img)
        #plt.yticks([0, 200, 400, 600, 800, 1000, 1200, 1400, 1600, 1800, 2000, 2200])
        #plt.savefig("".join([csvfilename, ".png"]), dpi = 1500)
    #plt.savefig("".join([csvfilename, ".png"]), dpi = 1500)
    plt.show()



def compare_with_penn_data_plots(csvfilename, domainfilename, max_val):
    csvfile = "".join([csvfilename, '.csv'])

    num_of_instances_deleted = {}
    reversedictdeleted = {}

    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            count = count + 1
            if count == 1:
                continue
            num_of_instances_deleted[row[0]] = int(row[1])
            reversedictdeleted[int(row[1])] = row[0]

    domainfile = "".join([domainfilename, ".csv"])
    sumrows = {}
    with open(domainfile, 'r') as f:
        reader = csv.reader(f)
        count = 0
        for row in reader:
            count = count + 1
            if count == 1:
                continue
            sumrows[row[0]] = -1
            for i in range(1, len(row)):
                sumrows[row[0]] = sumrows[row[0]] + int(row[i])

    num_of_instances_deleted_sorted = sorted(num_of_instances_deleted.values(), reverse = True)
    fids_sorted = []
    domain_sizes_sorted = []
    for n in num_of_instances_deleted_sorted:
        domain_sizes_sorted.append(sumrows[reversedictdeleted[n]])
        fids_sorted.append(reversedictdeleted[n])

    return [numpy.array(num_of_instances_deleted_sorted)/float(max_val), fids_sorted]










# Original data: 1 = in domain; 0 = not in domain
# Colors: black = not in domain; white = in domain
#make_plot("Domain data for repacker - Ref to binData (formatted for Vidya)", max_val=1, gray=True, show_colorbar=False)

filename1 = os.path.join("data", "FromVijay", "0_assignments-stationshuffle-channelshuffle")
filename2 = os.path.join("data", "FromVijay", "0_assignments-stationshuffle-nochannelshuffle")
files = [os.path.join("data", "FromVijay", "C-0_channels_removed-stationshuffle-channelshuffle_assignments"), os.path.join("data", "FromVijay", "C-0_channels_removed-stationshuffle-nochannelshuffle_assignments"),
         os.path.join("data", "FromVijay", "A-14_channels_removed-nostationshuffle-nochannelshuffle_assignments"), os.path.join("data", "FromVijay", "A-14_channels_removed-stationshuffle-channelshuffle_assignments"),
         os.path.join("data", "FromVijay", "A-14_channels_removed-stationshuffle-channelshuffle_assignments -- 20 samples"),
         os.path.join("data", "FromVijay", "A-14_channels_removed-stationshuffle-channelshuffle_last50_assignments"),
         os.path.join("data", "FromVijay", "A-14_channels_removed-stationshuffle-channelshuffle_first50_assignments")]

filename3 = os.path.join("data", "FromVijay", "Domain data for repacker - Ref to binData (formatted for Vidya)")

#create_fidmappedtoband_csv()

count = 0
num2_sorted = []
for filename in files:
    if count < 2:
        segregate = True
        n = 0
    else:
        segregate = False
        n = 14
    #make_plot(filename, filename3, max_val=100, num_channels_cleared = 14, black_bg=True, segregate_bands = segregate)
    if count  == 5:
        [num1_sorted, fids_sorted] = compare_with_penn_data_plots(filename, filename3, max_val = 1)
    if count == 6:
        num2 = {}
        with open("".join([filename, ".csv"]), 'r') as f:
            reader = csv.reader(f)
            count = 0
            for row in reader:
                count = count + 1
                if count == 1:
                    continue
                num2[row[0]] = int(row[1])

        for f in fids_sorted:
            num2_sorted.append(num2[f])


    count = count + 1

plt.plot(range(1675), num1_sorted, 'b')
plt.plot(range(1675), num2_sorted, 'r')
plt.show()
