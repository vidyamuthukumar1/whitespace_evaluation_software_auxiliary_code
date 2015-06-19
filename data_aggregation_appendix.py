import data_aggregation
from evaluate_multiple_assignments import *

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
import os
import numpy

def not_function(latitude, longitude, latitude_index, longitude_index, current_value):
    return 1 - current_value

def subtraction_function(this_value, other_value):
    return this_value - other_value

def median_function(latitude, longitude, latitude_index, longitude_index, list_of_values_in_order):
    return numpy.median(list_of_values_in_order)



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

"""Load submaps."""
def load_submaps(buffersize):
    with open("stamps_with_buffer=%dkm.pkl"%buffersize, 'r') as f:
        stamps = pickle.load(f)

    return stamps

buffers = [0, 1, 4, 11]
submaps = {}

for buffersize in buffers:
    submaps[buffersize] = load_submaps(buffersize)


submaps_ws = {'fixed': {'cochannel': submaps[11], 'adjchannel': submaps[1]}, 'portable': {'cochannel': submaps[4], 'adjacent': []}}
submaps_tv = submaps[0]

#Because submaps by default have 1 for whitespace and 0 for excluded areas. For TV submaps, we want this the other way round.
for submap_tv in submaps_tv.values():
    submap_tv[1].update_all_values_via_function(not_function)


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



#Plot for figure 5
"""considered_bandplan_fig_5 = 14



repack_assignment_fig_5 = Assignment(AssignmentType.repack, QuantityToPlot.tv,
                                         region, region_map_spec, plmrs_exclusions_map, ruleset,
                                         tv_channel_list, submaps_tv,
                                         considered_bandplan_fig_5, repack = Repack(RepackType.C, 99))
repack_assignment_fig_5.set_region(all_fids_considered_in_auction)
repack_map_fig_5 = repack_assignment_fig_5.load_statistical_data(StatisticalMetricToPlot.median)



chopofftop_assignment_fig_5 = Assignment(AssignmentType.chopofftop, QuantityToPlot.tv,
                                         region, region_map_spec, plmrs_exclusions_map, ruleset,
                                         tv_channel_list, submaps_tv,
                                         considered_bandplan_fig_5)
chopofftop_assignment_fig_5.set_region(all_fids_considered_in_auction)
chopofftop_map_fig_5 = chopofftop_assignment_fig_5.fetch_data()
loss_map_repack_fig_5 = original_tv_map.combine_datamaps_with_function(repack_map_fig_5, subtraction_function)
loss_map_chopofftop_fig_5 = original_tv_map.combine_datamaps_with_function(chopofftop_map_fig_5, subtraction_function)

for i in range(400):
    for j in range(600):
        if loss_map_repack_fig_5.get_value_by_index(i, j) == 0:
            loss_map_repack_fig_5.set_value_by_index(i, j, -1)
        if loss_map_chopofftop_fig_5.get_value_by_index(i, j) == 0:
            loss_map_chopofftop_fig_5.set_value_by_index(i, j, -1)


map1 = data_aggregation.plot_map_from_datamap2D(loss_map_repack_fig_5, region_map, cmin = 0, cmax = 15, set_below_zero_color = '0.90', colorbar_ticks = range(16), colorbar_label = "TV Channels Lost")

map1.blocking_show()
map2 = data_aggregation.plot_map_from_datamap2D(loss_map_chopofftop_fig_5, region_map, cmin = 0, cmax = 15, set_below_zero_color = '0.90', colorbar_ticks = range(16), colorbar_label = "TV Channels Lost")
map2.blocking_show()"""

#Plot for figure 7
"""image_plots = {}
for b in [7, 14, 22, 25]:
    repack_assignment_fig_6 = Assignment(AssignmentType.repack, QuantityToPlot.tv,
                                         region, region_map_spec, plmrs_exclusions_map, ruleset,
                                         tvws_channel_list, submaps_tv,
                                         b,
                                         repack = Repack(RepackType.C, 0))
    repack_assignment_fig_6.set_region(all_fids_considered_in_auction)

    image_plots[b] = data_aggregation.plot_tadpole_for_given_bandplan(repack_assignment_fig_6, original_assignment_tv, population_map, 100, all_fids_considered_in_auction)
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
    #plt.colorbar()
    plt.tick_params(labelsize = 24)
    plt.xlabel("Current # Of TV Channels", fontsize = 30)
    plt.ylabel("Average # Of TV Channels \n After Efficient Reallocation", fontsize = 30)
    #plt.show()
    #plt.colorbar()
    image_plots[b].savefig("data/For Kate - Washington/icc_appendix_fig4_final_%dchannelsremoved.png"%b)"""

#Plot for figure 8
"""fids_with_domain_size = {}

with open(os.path.join("data", "FromVijay", "Domain data for repacker - Ref to binData (formatted for Vidya).csv"), 'r') as f:
    reader = csv.reader(f)
    ind = 0
    for row in reader:
        ind = ind + 1
        if ind == 1:
            continue
        fids_with_domain_size[row[0]] = []
        for i in range(1, len(row)):
            fids_with_domain_size[row[0]].append(int(row[i]))

        fids_with_domain_size[row[0]] = sum(fids_with_domain_size[row[0]]) - 1

plt.hist(fids_with_domain_size.values(), bins = 50, log = True)
plt.xlabel("Domain size")
plt.ylabel("Number of stations")
plt.show()"""

"""population_map_map = data_aggregation.plot_map_from_datamap2D(population_map, region_map, transformation = "log", use_colorbar = False, cmin = 0, cmax = 6)
population_map_map.blocking_show()"""


def overlap_indicator_function(this_value, other_value):
    if this_value != 0:
        return this_value
    if other_value > 1:
        return other_value
    else:
        return 0

def set_zero_to_inf(latitude, longitude, latitude_index, longitude_index, current_value):
    if current_value == 0:
        return numpy.inf
    return current_value


"""for s in submaps_tv.values():
    if s[0] == 'circular':
        s[1].mutable_matrix = 0.6 * s[1].mutable_matrix

original_assignment_tv = Assignment(AssignmentType.original, QuantityToPlot.tv,
                                    region, region_map_spec, plmrs_exclusions_map, ruleset,
                                    tv_channel_list, submaps_tv,
                                    0)"""



original_tv_map = original_assignment_tv.make_data()

overlap_indicator_map = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)
overlap_indicator_map.reset_all_values(0)

for c in tv_channel_list:
    overlap_indicator_map = overlap_indicator_map.combine_datamaps_with_function(original_tv_map.get_layer(c), overlap_indicator_function)

overlap_indicator_map.update_all_values_via_function(set_zero_to_inf)

overlap_indicator_picture = data_aggregation.plot_map_from_datamap2D(overlap_indicator_map, region_map, use_colorbar = False, cmin = 0, cmax = 2)
overlap_indicator_picture.blocking_show()



