from evaluate_multiple_assignments import *
from west.region_united_states import RegionUnitedStates
from west.ruleset_fcc2012 import RulesetFcc2012
from west.boundary import BoundaryContinentalUnitedStates, BoundaryContinentalUnitedStatesWithStateBoundaries
import west.data_management
import data_management_vidya
import west.device

import protected_entities_tv_stations_vidya

import pickle
import numpy
import os
import csv
"""The entire contents of this file is something like a main function. We are using all the functions from evaluate_multiple_assignments."""

"""Define region, as well as ruleset."""

def not_function(latitude, longitude, latitude_index, longitude_index, current_value):
    return 1 - current_value



region = RegionUnitedStates()
ruleset = RulesetFcc2012()
all_fids_considered_in_auction = []
with open("all_facility_ids_considered_in_auction.csv", 'rU') as f:
    reader = csv.reader(f)
    for row in reader:
        all_fids_considered_in_auction.append(row[0])


#Hack-y, done because location within boundary does not work with BoundaryContinentalUnitedStates.
boundary = BoundaryContinentalUnitedStatesWithStateBoundaries()
region._boundary = boundary


"""Define set of valid TVWS (and TV) channels."""
tvws_channel_list = region.get_tvws_channel_list()

#Hack-y, done because channels 3 and 4 are being counted as WS (although this is not confirmed yet.)
tvws_channel_list.append(3)
tvws_channel_list.append(4)
tvws_channel_list = sorted(tvws_channel_list)

tv_channel_list = copy(tvws_channel_list)


"""Load submaps."""
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


"""Define all fundamental data maps that will be used."""
datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
is_in_region_map_spec = west.data_management.SpecificationRegionMap(BoundaryContinentalUnitedStates, datamap_spec)
is_in_region_map = is_in_region_map_spec.fetch_data()
population_map_spec = west.data_management.SpecificationPopulationMap(is_in_region_map_spec, west.population.PopulationData)
population_map = population_map_spec.fetch_data()
zero_map = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(is_in_region_map)
zero_map.reset_all_values(0)
plmrs_exclusions_map_spec = data_management_vidya.SpecificationPLMRSMap(is_in_region_map_spec, region, ruleset)
plmrs_exclusions_map = plmrs_exclusions_map_spec.fetch_data()

"""plmrs_file_path = "data/plmrs_exclusions_map.pcl"
if os.path.isfile(plmrs_file_path):
    plmrs_exclusions_map = west.data_map.DataMap3D.from_pickle(plmrs_file_path)
else:
    plmrs_exclusions_map = createPLMRSExclusionsMap(region, tvws_channel_list, is_in_region_map, ruleset)
    plmrs_exclusions_map.to_pickle(plmrs_file_path)"""


"""Define tunable parameters (device specifications, assignment types, etc)"""

device_specification = DeviceSpecification.portable
if device_specification == DeviceSpecification.fixed:
    device = west.device.Device(0, 30, 1) #Fixed, HAAT = 30, has geolocation.
else:
    device = west.device.Device(1, 30, 1)

plmrs_exclusions_applied = PLMRSExclusions.plmrs_applied
whitespace_evaluation_type = WhitespaceEvaluationType.total
quantity_to_evaluate = QuantityToPlot.whitespace

if quantity_to_evaluate == QuantityToPlot.whitespace:
    pareto_filename = "pareto_curve_data_ws_portable.csv"
elif quantity_to_evaluate == QuantityToPlot.tv:
    pareto_filename = "pareto_curve_data_tv.csv"
else:
    raise ValueError("Invalid quantity to evaluate entered. Please check input.")


set_of_bandplans = range(1, 38)
num_repacks_considered = 100
assignment_type = AssignmentType.chopofftop


create_pareto_data = True
"""with open(os.path.join("data", "pareto_curve_data_tv.csv"), 'w') as f:
    writer = csv.writer(f)
    writer.writerow([])"""
update_old_entries = True


"""Some miscellaneous functions."""
def median_function(latitude, longitude, latitude_index, longitude_index, list_of_values_in_order):
    return numpy.median(list_of_values_in_order)

def stddev_function(latitude, longitude, latitude_index, longitude_index, list_of_values_in_order):
    return numpy.std(list_of_values_in_order)

def mean_function(latitude, longitude, latitude_index, longitude_index, list_of_values_in_order):
    return numpy.mean(list_of_values_in_order)


"""Performing actual whitespace and TV evaluation."""


if assignment_type == AssignmentType.original:
    assignment = Assignment(assignment_type, quantity_to_evaluate,
                            region, is_in_region_map_spec, plmrs_exclusions_map, ruleset,
                            tv_channel_list, submaps_ws,
                            0, device = device, device_specification = device_specification, whitespace_evaluation_type = whitespace_evaluation_type,
                            plmrs_indicator= plmrs_exclusions_applied)
    assignment.set_region(all_fids_considered_in_auction)
    #Evaluating whitespace/TV map
    if update_old_entries:
        total_map = assignment.make_data()
    else:
        total_map = assignment.fetch_data()
    cdf = west.data_manipulation.calculate_cdf_from_datamap2d(total_map, population_map, is_in_region_map)
    if create_pareto_data:
        assignment.write_entry_to_pareto_file(pareto_filename, cdf[2], cdf[3])


if assignment_type == AssignmentType.repack:

    for n in set_of_bandplans:
        all_maps = west.data_map.DataMap3D.from_DataMap2D(is_in_region_map, range(num_repacks_considered))
        for i in range(num_repacks_considered):
            repack = Repack(RepackType.C, i)
            assignment = Assignment(assignment_type, quantity_to_evaluate,
                                    region, is_in_region_map_spec, plmrs_exclusions_map, ruleset,
                                    tv_channel_list, submaps_ws,
                                    n, repack = repack, device = device, device_specification = device_specification, whitespace_evaluation_type = whitespace_evaluation_type,
                                    plmrs_indicator = plmrs_exclusions_applied)
            assignment.set_region(all_fids_considered_in_auction)

            #Evaluating map
            if update_old_entries:
                all_maps.set_layer(i, assignment.make_data())
            else:
                all_maps.set_layer(i, assignment.fetch_data())


            if create_pareto_data:
                cdf = west.data_manipulation.calculate_cdf_from_datamap2d(all_maps.get_layer(i), population_map, is_in_region_map)
                assignment.write_entry_to_pareto_file(pareto_filename, cdf[2], cdf[3])

        median_map = all_maps.combine_values_elementwise_across_layers_using_function(median_function)
        mean_map = all_maps.combine_values_elementwise_across_layers_using_function(mean_function)
        stddev_map = all_maps.combine_values_elementwise_across_layers_using_function(stddev_function)
        median_map.to_pickle(os.path.join("data", assignment.subdirectory, "".join([assignment.to_string(), "_median.pcl"])))
        mean_map.to_pickle(os.path.join("data", assignment.subdirectory, "".join([assignment.to_string(), "_mean.pcl"])))
        stddev_map.to_pickle(os.path.join("data", assignment.subdirectory, "".join([assignment.to_string(), "_stddev.pcl"])))

if assignment_type == AssignmentType.chopofftop:

    for n in set_of_bandplans:
        assignment = Assignment(assignment_type, quantity_to_evaluate,
                                region, is_in_region_map_spec, plmrs_exclusions_map, ruleset,
                                tv_channel_list, submaps_ws,
                                n, device = device, device_specification = device_specification, whitespace_evaluation_type = whitespace_evaluation_type,
                                plmrs_indicator = plmrs_exclusions_applied)

        assignment.set_region(all_fids_considered_in_auction)

        #Evaluating map
        if update_old_entries:
            total_map = assignment.make_data()
        else:
            total_map = assignment.fetch_data()
        if create_pareto_data:
            cdf = west.data_manipulation.calculate_cdf_from_datamap2d(total_map, population_map, is_in_region_map)
            assignment.write_entry_to_pareto_file(pareto_filename, cdf[2], cdf[3])





"""To-dos:
Proofread all code.
Run.
"""







