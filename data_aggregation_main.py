import data_aggregation
from data_management_vidya import SpecificationPLMRSMap
from evaluate_multiple_assignments import *

from west.region_united_states import RegionUnitedStates
from west.ruleset_fcc2012 import RulesetFcc2012
from west.data_management import SpecificationDataMap, SpecificationRegionMap, SpecificationPopulationMap
from west.boundary import BoundaryContinentalUnitedStates, BoundaryContinentalUnitedStatesWithStateBoundaries
from west.device import Device
import west.population

import matplotlib.cm
import matplotlib.pyplot as plt
import pickle
import numpy

def not_function(latitude, longitude, latitude_index, longitude_index, current_value):
    return 1 - current_value

def set_zero_to_inf(latitude, longitude, latitude_index, longitude_index, current_value):
    if current_value == 0:
        return numpy.inf
    return current_value

def subtraction_function(this_value, other_value):
    return this_value - other_value


region = RegionUnitedStates()
region._boundary = BoundaryContinentalUnitedStatesWithStateBoundaries()
ruleset = RulesetFcc2012()
all_fids_considered_in_auction = []
with open("all_facility_ids_considered_in_auction.csv", 'rU') as f:
    reader = csv.reader(f)
    for row in reader:
        all_fids_considered_in_auction.append(row[0])


datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
region_map_spec = west.data_management.SpecificationRegionMap(BoundaryContinentalUnitedStates, datamap_spec)
region_map = region_map_spec.fetch_data()
population_map_spec = west.data_management.SpecificationPopulationMap(region_map_spec, west.population.PopulationData)
population_map = population_map_spec.fetch_data()
zero_map = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(region_map)
zero_map.reset_all_values(0)
plmrs_exclusions_map_spec = SpecificationPLMRSMap(region_map_spec, region, ruleset)
plmrs_exclusions_map = plmrs_exclusions_map_spec.fetch_data()

tv_channel_list = range(2, 37) + range(38, 52)
tvws_channel_list = range(2, 37) + range(38, 52)

def load_submaps(buffersize):
    with open("stamps_with_buffer=%dkm.pkl"%buffersize, 'r') as f:
        stamps = pickle.load(f)

    return stamps

buffers = [0, 1.8, 4, 14.3]
submaps = {}

for buffersize in buffers:
    submaps[buffersize] = load_submaps(buffersize)


submaps_ws = {'fixed': {'cochannel': submaps[14.3], 'adjchannel': submaps[1.8]}, 'portable': {'cochannel': submaps[4], 'adjacent': []}}
submaps_tv = submaps[0]

#Because submaps by default have 1 for whitespace and 0 for excluded areas. For TV submaps, we want this the other way round.
for submap_tv in submaps_tv.values():
    submap_tv[1].update_all_values_via_function(not_function)



fcc_bandplans = [7, 14, 22, 25] #Actually 21, 24
original_assignment_tv = Assignment(AssignmentType.original, QuantityToPlot.tv,
                                    region, region_map_spec, plmrs_exclusions_map, ruleset,
                                    tv_channel_list, submaps_tv,
                                    0)
original_tv_map = original_assignment_tv.fetch_data()

original_assignment_ws_portable = Assignment(AssignmentType.original, QuantityToPlot.whitespace,
                                    region, region_map_spec, plmrs_exclusions_map, ruleset,
                                    tvws_channel_list, submaps_ws,
                                    0, device_specification = DeviceSpecification.portable, device = Device(1, 30, 1), plmrs_indicator = PLMRSExclusions.plmrs_applied, whitespace_evaluation_type = WhitespaceEvaluationType.total)
original_portable_ws_map = original_assignment_ws_portable.fetch_data()

original_assignment_ws_fixed = Assignment(AssignmentType.original, QuantityToPlot.whitespace,
                                          region, region_map_spec, plmrs_exclusions_map, ruleset,
                                          tvws_channel_list, submaps_ws,
                                          0, device_specification = DeviceSpecification.fixed, device = Device(0, 30, 1), plmrs_indicator = PLMRSExclusions.plmrs_applied, whitespace_evaluation_type = WhitespaceEvaluationType.total)
original_fixed_ws_map = original_assignment_ws_fixed.fetch_data()

original_assignment_ws_fixed.set_region(all_fids_considered_in_auction)
"""original_ws_map_3D = original_assignment_ws_fixed.make_data()

for ch in tvws_channel_list:
    map = data_aggregation.plot_map_from_datamap2D(original_ws_map_3D.get_layer(ch), region_map, use_colorbar = False, cmin = 0, cmax = 1)
    map.blocking_show()"""



"""region_map_plot = data_aggregation.plot_map_from_datamap2D(region_map, region_map, use_colorbar = False, cmin = 0, cmax = 1)
region_map_plot.blocking_show()"""

"""plmrs_map_total = plmrs_exclusions_map.sum_all_layers()

def fifty_minus_original(latitude, longitude, latitude_index, longitude_index, current_value):
    return 49 - current_value

def make_zero_inf(latitude, longitude, latitude_index, longitude_index, current_value):
    if current_value == 0:
        return numpy.inf
    return current_value
plmrs_map_total.update_all_values_via_function(fifty_minus_original)
plmrs_map_total.update_all_values_via_function(make_zero_inf)
plmrs_map = data_aggregation.plot_map_from_datamap2D(plmrs_map_total, region_map, colorbar_label = "PLMRS-Affected Channels", colorbar_ticks = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], cmin = 0, cmax = 10)
plmrs_map.blocking_show()"""

#Plot fig. 3
"""considered_bandplan_fig_3 = fcc_bandplans[1]
repack_assignment_fig_3 = Assignment(AssignmentType.repack, QuantityToPlot.tv,
                                     region, region_map_spec, plmrs_exclusions_map, ruleset,
                                     tv_channel_list, submaps_tv,
                                     considered_bandplan_fig_3, repack = Repack(RepackType.C, 99))
repack_map_fig_3 = repack_assignment_fig_3.load_statistical_data(StatisticalMetricToPlot.median)

chopofftop_assignment_fig_3 = Assignment(AssignmentType.chopofftop, QuantityToPlot.tv,
                                         region, region_map_spec, plmrs_exclusions_map, ruleset,
                                         tv_channel_list, submaps_tv,
                                         considered_bandplan_fig_3)
chopofftop_assignment_fig_3.set_region(all_fids_considered_in_auction)
chopofftop_map_fig_3 = chopofftop_assignment_fig_3.make_data()
loss_map_repack_fig_3 = original_tv_map.combine_datamaps_with_function(repack_map_fig_3, subtraction_function)
loss_map_chopofftop_fig_3 = original_tv_map.combine_datamaps_with_function(chopofftop_map_fig_3, subtraction_function)
fig_3 = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)

for i in range(400):
    for j in range(600):
        if loss_map_repack_fig_3.get_value_by_index(i, j) == 0 and loss_map_chopofftop_fig_3.get_value_by_index(i, j) == 0:
            fig_3.set_value_by_index(i, j, -1)
        elif loss_map_repack_fig_3.get_value_by_index(i, j) != 0 and loss_map_chopofftop_fig_3.get_value_by_index(i, j) == 0:
            fig_3.set_value_by_index(i, j, 1)
        elif loss_map_repack_fig_3.get_value_by_index(i, j) == 0 and loss_map_chopofftop_fig_3.get_value_by_index(i, j) != 0:
            fig_3.set_value_by_index(i, j, 0.3)
        else:
            fig_3.set_value_by_index(i, j, 2.0)

cmap = matplotlib.cm.gist_rainbow
cmap.set_under('0.90')
cmap.set_over('w')
cmap.set_bad('w')

fig_3_map = data_aggregation.plot_map_from_datamap2D(fig_3, region_map, use_colorbar = False, colormap = cmap, cmin = 0, cmax = 2.6)

fig_3_map.blocking_show()"""

#Plot fig. 4
"""fig_4 = matplotlib.pyplot.figure()
#ax_full = fig_4.add_subplot(111)
ax_fixed = fig_4.add_subplot(211)
ax_portable = fig_4.add_subplot(212)
colors = {7: 'blue', 14: 'green', 22: 'red', 25: 'magenta'}
original_plot_portable = data_aggregation.get_ccdf_from_datamap2D(original_portable_ws_map, region_map, population_map)
ax_portable.plot(original_plot_portable[0], original_plot_portable[1], 'k')
original_plot_fixed = data_aggregation.get_ccdf_from_datamap2D(original_fixed_ws_map, region_map, population_map)
ax_fixed.plot(original_plot_fixed[0], original_plot_fixed[1], 'k')
repack_plot_portable = {}
repack_plot_fixed = {}
for b in fcc_bandplans:
    repack_assignment = Assignment(AssignmentType.repack, QuantityToPlot.whitespace,
                                   region, region_map_spec, plmrs_exclusions_map, ruleset,
                                   tvws_channel_list, submaps_ws,
                                   b, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, whitespace_evaluation_type = WhitespaceEvaluationType.total, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                   repack = Repack(RepackType.C, 99))
    repack_datamap = repack_assignment.load_statistical_data(StatisticalMetricToPlot.median)
    repack_plot_portable[b] = data_aggregation.get_ccdf_from_datamap2D(repack_datamap, region_map, population_map)
    ax_portable.plot(repack_plot_portable[b][0], repack_plot_portable[b][1], color = colors[b])

    repack_assignment_fixed = Assignment(AssignmentType.repack, QuantityToPlot.whitespace,
                                         region, region_map_spec, plmrs_exclusions_map, ruleset,
                                         tvws_channel_list, submaps_ws,
                                         b, device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, whitespace_evaluation_type = WhitespaceEvaluationType.total, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                         repack = Repack(RepackType.C, 99))
    repack_datamap_fixed = repack_assignment_fixed.load_statistical_data(StatisticalMetricToPlot.median)
    repack_plot_fixed[b] = data_aggregation.get_ccdf_from_datamap2D(repack_datamap_fixed, region_map, population_map)
    ax_fixed.plot(repack_plot_fixed[b][0], repack_plot_fixed[b][1], color = colors[b])
tfixed = fig_4.text(0.73, 0.83, "Fixed Devices", color = 'black')
tfixed.set_bbox(dict(facecolor = '0.75', alpha = 0.5))
tportable = fig_4.text(0.71, 0.4, "Portable Devices", color = 'black')
tportable.set_bbox(dict(facecolor = '0.75', alpha = 0.5))

#ax_full.set_xticks([])
#ax_full.set_xticklabels([])
#ax_full.set_yticklabels([])
#ax_full.set_yticks([])
#ax_full.set_ylabel("CCDF By Population")
ax_fixed.grid(True, linestyle = '--', alpha = 0.5)
ax_portable.grid(True, linestyle = '--', alpha = 0.5)
fig_4.text(0.06, 0.5, 'CCDF By Population', va = 'center', rotation = 'vertical')
ax_portable.set_xlabel("TV Whitespace (Channels)")

ax_fixed.text(13, 0.65, "Original Assignment", rotation = 330)
ax_fixed.annotate("7", xy = (10, 0.5), xytext = (12, 0.45), color = 'blue', arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3', color = 'blue'))
ax_fixed.annotate("14", xy = (9, 0.35), xytext = (11, 0.30), color = 'green', arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3', color = 'green'))
ax_fixed.annotate("21", xy = (9.5, 0.16), xytext = (9.2, 0.22), color = 'red', arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3', color = 'red'))
ax_fixed.annotate("24", xy = (7, 0.20), xytext = (6.5, 0.05), color = 'magenta', arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3', color = 'magenta'))

ax_portable.annotate("7", xy = (28, 0.4), xytext = (30, 0.37), color = 'blue', arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3', color = 'blue'))
ax_portable.annotate("14", xy = (22, 0.4), xytext = (24, 0.37), color = 'green', arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3', color = 'green'))
ax_portable.annotate("21", xy = (16, 0.4), xytext = (18, 0.37), color = 'red', arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3', color = 'red'))
ax_portable.annotate("24", xy = (10, 0.6), xytext = (9.3, 0.42), color = 'magenta', arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3', color = 'magenta'))


ax_portable.text(20, 0.85, "Original Assignment", rotation = 345)

fig_4.savefig("data/For Kate - Washington/icc_fig4_final.png")"""


#Plot fig. 5
"""considered_bandplan_fig_5 = 7
repack_assignment_fig_5 = Assignment(AssignmentType.repack, QuantityToPlot.tv,
                                     region, region_map_spec, plmrs_exclusions_map, ruleset,
                                     tvws_channel_list, submaps_tv,
                                     considered_bandplan_fig_5, device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, whitespace_evaluation_type = WhitespaceEvaluationType.total, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                     repack = Repack(RepackType.C, 99))

fig_5_datamap = repack_assignment_fig_5.load_statistical_data(StatisticalMetricToPlot.median)
fig_5_map = data_aggregation.plot_map_from_datamap2D(fig_5_datamap, region_map, colorbar_label = "TV Channels", colorbar_ticks = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50], cmin = 0, cmax = 50)
fig_5_map.blocking_show()"""


#Plot fig. 6

"""image_plots = {}
for b in fcc_bandplans:
    repack_assignment_fig_6 = Assignment(AssignmentType.repack, QuantityToPlot.whitespace,
                                         region, region_map_spec, plmrs_exclusions_map, ruleset,
                                         tvws_channel_list, submaps_ws,
                                         b, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, whitespace_evaluation_type = WhitespaceEvaluationType.total, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                         repack = Repack(RepackType.C, 0))

    image_plots[b] = data_aggregation.plot_tadpole_for_given_bandplan(repack_assignment_fig_6, original_assignment_ws_portable, population_map, 100)
    xy = range(0, 50)
    xyoffset = []
    xyub = []
    for x in xy:
        xyoffset.append(max(x - b, 0))
        xyub.append(50 - b)
    plt.plot(xy, xy, 'k')
    plt.plot(xy, xyoffset, 'k')
    plt.plot(xy, xyub, 'k')
    #plt.plot(xyub, xy, 'k')
    plt.gca().invert_yaxis()
    plt.xlim(0, 50)
    plt.ylim(0, 50)
    plt.tick_params(labelsize = 24)
    plt.xlabel("Current # Of Whitespace Channels", fontsize = 30)
    plt.ylabel("Average # Of Whitespace Channels \n After Efficient Reallocation", fontsize = 30)
    plt.show()
    #plt.colorbar()
    #image_plots[b].savefig("data/For Kate - Washington/icc_fig7_final_%dchannelsremoved.png"%b)"""



#Plot fig. 7
"""image_plots = {}
for b in fcc_bandplans:
    repack_assignment_fig_7 = Assignment(AssignmentType.repack, QuantityToPlot.whitespace,
                                         region, region_map_spec, plmrs_exclusions_map, ruleset,
                                         tvws_channel_list, submaps_ws,
                                         b, device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, whitespace_evaluation_type = WhitespaceEvaluationType.total, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                         repack = Repack(RepackType.C, 0))

    image_plots[b] = data_aggregation.plot_tadpole_for_given_bandplan(repack_assignment_fig_7, original_assignment_ws_fixed, population_map, 100)
    xy = range(0, 50)
    xyoffset = []
    xyub = []
    for x in xy:
        xyoffset.append(max(x - b, 0))
        xyub.append(50 - b)
    plt.plot(xy, xy, 'k')
    plt.plot(xy, xyoffset, 'k')
    plt.plot(xy, xyub, 'k')
    #plt.plot(xyub, xy, 'k')
    plt.gca().invert_yaxis()
    plt.xlim(0, 50)
    plt.ylim(0, 50)
    plt.tick_params(labelsize = 24)
    plt.xlabel("Current # Of Whitespace Channels", fontsize = 30)
    plt.ylabel("Average # Of Whitespace Channels \n After Efficient Reallocation", fontsize = 30)
    #plt.colorbar()
    #image_plots[b].savefig("data/For Kate - Washington/icc_fig8_final_%dchannelsremoved.png"%b)
    plt.show()"""



#Plot fig. 8
"""image_plots = {}
for b in fcc_bandplans:
    repack_assignment_fig_8 = Assignment(AssignmentType.repack, QuantityToPlot.whitespace,
                                         region, region_map_spec, plmrs_exclusions_map, ruleset,
                                         tvws_channel_list, submaps_ws,
                                         b, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, whitespace_evaluation_type = WhitespaceEvaluationType.total, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                         repack = Repack(RepackType.C, 0))

    xaxis_assignment_fig_8  = Assignment(AssignmentType.chopofftop, QuantityToPlot.whitespace,
                                         region, region_map_spec, plmrs_exclusions_map, ruleset,
                                         tvws_channel_list, submaps_ws,
                                         b, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, whitespace_evaluation_type = WhitespaceEvaluationType.total, plmrs_indicator = PLMRSExclusions.plmrs_applied)
    xaxis_assignment_fig_8.set_region(all_fids_considered_in_auction)

    image_plots[b] = data_aggregation.plot_tadpole_for_given_bandplan(repack_assignment_fig_8, xaxis_assignment_fig_8, population_map, 100)
    xy = range(0, 50)
    xyoffset = []
    xyub = []
    for x in xy:
        xyoffset.append(max(x - b, 0))
        xyub.append(50 - b)
    plt.plot(xy, xy, 'k')
    #plt.plot(xy, xyoffset, 'k')
    plt.plot(xy, xyub, 'k')
    plt.plot(xyub, xy, 'k')
    plt.gca().invert_yaxis()
    plt.xlim(0, 50)
    plt.ylim(0, 50)
    plt.tick_params(labelsize = 24)
    plt.xlabel("# Of Whitespace Channels \n After Naive Reallocation", fontsize =26)
    plt.ylabel("Average # Of Whitespace Channels \n After Efficient Reallocation", fontsize = 26)
    #plt.colorbar()
    #image_plots[b].savefig("data/For Kate - Washington/icc_fig6_final_%dchannelsremoved.png"%b)
    plt.show()"""


#Plot fig. 9
"""pareto_data_tv, pareto_data_tv_chopofftop, pareto_data_ws_fixed, pareto_data_ws_chopofftop_fixed, pareto_data_ws_portable, pareto_data_ws_chopofftop_portable, lte_data = data_aggregation.plot_pareto_curves(RepackType.C, range(1, 38), StatisticalMetricToPlot.median)
print len(lte_data), len(pareto_data_tv)
print lte_data, pareto_data_tv
plt.plot(lte_data, pareto_data_tv.values(), color = 'purple', marker = 'o')
plt.plot(lte_data, pareto_data_tv.values(), color = 'purple', lw = 2)
#plt.plot(lte_data, pareto_data_tv_chopofftop.values(), color = 'purple', linestyle = '--', lw = 2)
plt.plot(list(numpy.array(lte_data) + 6 * numpy.array(pareto_data_ws_fixed.values())), pareto_data_tv.values(), color = 'olive', marker = 'o')
plt.plot(list(numpy.array(lte_data) + 6 * numpy.array(pareto_data_ws_fixed.values())), pareto_data_tv.values(), color = 'olive', lw = 2)
plt.plot(list(numpy.array(lte_data) + 6 * numpy.array(pareto_data_ws_chopofftop_fixed.values())), pareto_data_tv_chopofftop.values(),  color = 'olive', linestyle = '--', lw = 2)
plt.plot(list(numpy.array(lte_data) + 6 * numpy.array(pareto_data_ws_portable.values())), pareto_data_tv.values(), 'r-o', lw = 2)
plt.plot(list(numpy.array(lte_data) + 6 * numpy.array(pareto_data_ws_chopofftop_portable.values())), pareto_data_tv_chopofftop.values(),  'r--', lw = 2)


plt.plot(lte_data[6], pareto_data_tv[7], 'kx', mew = 3, markersize = 8)
plt.plot(lte_data[6] + 6 * pareto_data_ws_fixed[7], pareto_data_tv[7], 'kx', mew = 3, markersize = 8)
plt.plot(lte_data[6] + 6 * pareto_data_ws_portable[7], pareto_data_tv[7], 'kx', mew = 3, markersize = 8)

plt.plot(lte_data[13], pareto_data_tv[14], 'kD', markersize = 8)
plt.plot(lte_data[13] + 6 * pareto_data_ws_fixed[14], pareto_data_tv[14], 'kD', markersize = 8)
plt.plot(lte_data[13] + 6 * pareto_data_ws_portable[14], pareto_data_tv[14], 'kD', markersize = 8)

plt.plot(lte_data[21], pareto_data_tv[22], 'k+', mew = 3, markersize = 10.5)
plt.plot(lte_data[21] + 6 * pareto_data_ws_fixed[22], pareto_data_tv[22], 'k+', mew = 3, markersize = 10.5)
plt.plot(lte_data[21] + 6 * pareto_data_ws_portable[22], pareto_data_tv[22], 'k+', mew = 3, markersize = 10.5)

plt.plot(lte_data[24], pareto_data_tv[25], 'k*', markersize = 10.5)
plt.plot(lte_data[24] + 6 * pareto_data_ws_fixed[25], pareto_data_tv[25], 'k*', markersize = 10.5)
plt.plot(lte_data[24] + 6 * pareto_data_ws_portable[25], pareto_data_tv[25], 'k*', markersize = 10.5)
plt.ylim((0, 20))
plt.xlim((0, 300))
plt.xlabel("Available Spectrum (MHz)")
plt.ylabel("Median Number Of Watchable TV Channels")
plt.grid(b=None, which='major', axis='both', linestyle = '--', alpha = 0.5)

clearline = matplotlib.lines.Line2D([], [], label = "Efficient Clearing Method", linestyle = '-', linewidth = 2, color = 'black')
dashedline = matplotlib.lines.Line2D([], [], label = "Naive Clearing Method", linestyle = '--', linewidth = 2, color = 'black')
l1 = plt.legend(handles = [clearline, dashedline])

xmarker = matplotlib.lines.Line2D([], [], label = "7", linewidth = 0, linestyle = None, marker = 'x', markersize = 8, mew = 3, color = 'black')
Dmarker = matplotlib.lines.Line2D([], [], label = "14", linewidth = 0, linestyle = None, marker = 'D', markersize = 8, color = 'black')
plusmarker = matplotlib.lines.Line2D([], [], label = "21", linewidth = 0, linestyle = None, marker = "+", markersize = 10.5, mew = 3, color = 'black')
starmarker = matplotlib.lines.Line2D([], [], label = "24", linewidth = 0, linestyle = None, marker = "*", markersize = 10.5, color = 'black')
l2 = plt.legend(loc = 3, handles = [xmarker, Dmarker, plusmarker, starmarker], handlelength = 0, numpoints = 1, title = "Number of Channels Removed")
plt.figtext(0.13, 0.73, "Cleared Spectrum", color = 'purple')
plt.figtext(0.33, 0.73, "Total Fixed WS", color = 'olive')
plt.figtext(0.62, 0.73, "Total Portable WS", color = 'red')

plt.gca().add_artist(l1)

plt.show()

#Plot fig. 10
plt.plot(6 * numpy.array(pareto_data_ws_fixed.values()), pareto_data_tv.values(),'b-o', lw = 2)
plt.plot(6 * numpy.array(pareto_data_ws_chopofftop_fixed.values()), pareto_data_tv_chopofftop.values(), 'b--', lw = 2)
plt.plot(6 * numpy.array(pareto_data_ws_portable.values()), pareto_data_tv.values(), 'g-o', lw = 2)
plt.plot(6 * numpy.array(pareto_data_ws_chopofftop_portable.values()), pareto_data_tv_chopofftop.values(), 'g--', lw = 2)
plt.plot(list(numpy.array(lte_data) + 6 * numpy.array(pareto_data_ws_portable.values())), pareto_data_tv.values(), 'r-o', lw = 2)
plt.plot(list(numpy.array(lte_data) + 6 * numpy.array(pareto_data_ws_chopofftop_portable.values())), pareto_data_tv_chopofftop.values(),  'r--', lw = 2)

plt.plot(6 * pareto_data_ws_portable[7], pareto_data_tv[7], 'kx', mew = 3, markersize = 8)
plt.plot(6 * pareto_data_ws_fixed[7], pareto_data_tv[7], 'kx', mew = 3, markersize = 8)
plt.plot(lte_data[6] + 6 * pareto_data_ws_portable[7], pareto_data_tv[7], 'kx', mew = 3, markersize = 8)

plt.plot(6 * pareto_data_ws_portable[14], pareto_data_tv[14], 'kD', markersize = 8)
plt.plot(6 * pareto_data_ws_fixed[14], pareto_data_tv[14], 'kD', markersize = 8)
plt.plot(lte_data[13] + 6 * pareto_data_ws_portable[14], pareto_data_tv[14], 'kD', markersize = 8)

plt.plot(6 * pareto_data_ws_portable[22], pareto_data_tv[22], 'k+', mew = 3, markersize = 10.5)
plt.plot(6 * pareto_data_ws_fixed[22], pareto_data_tv[22], 'k+', mew = 3, markersize = 10.5)
plt.plot(lte_data[21] + 6 * pareto_data_ws_portable[22], pareto_data_tv[22], 'k+', mew = 3, markersize = 10.5)

plt.plot(6 * pareto_data_ws_portable[25], pareto_data_tv[25], 'k*', markersize = 10.5)
plt.plot(6 * pareto_data_ws_fixed[25], pareto_data_tv[25], 'k*', markersize = 10.5)
plt.plot(lte_data[24] + 6 * pareto_data_ws_portable[25], pareto_data_tv[25], 'k*', pareto_data_tv[25], markersize = 10.5)
plt.ylim((0, 20))
plt.xlim((0, 300))
plt.xlabel("Available Spectrum (MHz)")
plt.ylabel("Median Number Of Watchable TV Channels")
plt.grid(b=None, which='major', axis='both', linestyle = '--', alpha = 0.5)
l1 = plt.legend(handles = [clearline, dashedline])
l2 = plt.legend(loc = (0.37, 0.05), handles = [xmarker, Dmarker, plusmarker, starmarker], handlelength = 0, numpoints = 1, title = "Number of Channels Removed")
plt.gca().add_artist(l1)

plt.figtext(0.23, 0.73, "Fixed TVWS", color = 'blue')
plt.figtext(0.47, 0.73, "Portable TVWS", color = 'green')
plt.figtext(0.63, 0.73, "All Mobile Spectrum", color = 'red')


plt.show()"""



def overlap_indicator_function(this_value, other_value):
    #if this_value != 0:
    #    return this_value
    if other_value > 1:
        return max(other_value, this_value)
    else:
        return this_value

def set_zero_to_inf(latitude, longitude, latitude_index, longitude_index, current_value):
    if current_value == 0:
        return numpy.inf
    return current_value


for s in submaps_tv.values():
    if s[0] == 'circular':
        s[1].mutable_matrix = 0.55 * s[1].mutable_matrix

original_assignment_tv = Assignment(AssignmentType.original, QuantityToPlot.tv,
                                    region, region_map_spec, plmrs_exclusions_map, ruleset,
                                    tv_channel_list, submaps_tv,
                                    0)



original_tv_map = original_assignment_tv.make_data()

overlap_indicator_map = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)
overlap_indicator_map.reset_all_values(0)

for c in tv_channel_list:
    overlap_indicator_map = overlap_indicator_map.combine_datamaps_with_function(original_tv_map.get_layer(c), overlap_indicator_function)

overlap_indicator_map.update_all_values_via_function(set_zero_to_inf)

overlap_indicator_picture = data_aggregation.plot_map_from_datamap2D(overlap_indicator_map, region_map, colorbar_ticks = [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4], cmin = 0, cmax = 4)
overlap_indicator_picture.blocking_show()
