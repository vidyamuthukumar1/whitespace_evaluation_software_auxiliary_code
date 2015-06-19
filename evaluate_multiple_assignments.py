from west.custom_logging import getModuleLogger
import west.data_map
import west.data_manipulation
import west.protected_entities_tv_stations
import west.helpers

import protected_entities_tv_stations_vidya


import os
import csv
import numpy
from copy import copy
from enum import Enum



"""
Class definitions
"""

class Assignment(west.data_management.Specification):

    def __init__(self, assignment_type, quantity_to_evaluate,
                 region, region_map_spec, plmrs_exclusions_map, ruleset,
                 channel_list, submaps,
                 num_channels_removed = 0, device = None, device_specification = None, plmrs_indicator = None, whitespace_evaluation_type = None, repack = None, test_index = None):

        #Type checking
        self.log = getModuleLogger(self)
        self._expect_of_type(region_map_spec, west.data_management.SpecificationRegionMap)
        self._expect_of_type(region, west.data_management.Region)
        self._expect_of_type(assignment_type, AssignmentType)
        self._expect_of_type(quantity_to_evaluate, QuantityToPlot)
        self._expect_of_type(plmrs_exclusions_map, west.data_map.DataMap3D)
        self._expect_of_type(ruleset, west.data_management.Ruleset)
        if quantity_to_evaluate == QuantityToPlot.whitespace:
            self._expect_of_type(device, west.device.Device)
            self._expect_of_type(device_specification, DeviceSpecification)
            self._expect_of_type(plmrs_indicator, PLMRSExclusions)
            self._expect_of_type(whitespace_evaluation_type, WhitespaceEvaluationType)

        #Store data
        self.region_map_spec = region_map_spec
        self.bandplan = num_channels_removed
        self.channel_list = channel_list
        self._convert_to_class_and_object("type", assignment_type)
        self._convert_to_class_and_object("quantity_to_evaluate", quantity_to_evaluate)
        self._convert_to_class_and_object("region", region)
        self._convert_to_class_and_object("plmrs_map", plmrs_exclusions_map)
        self._convert_to_class_and_object("ruleset", ruleset)
        self._convert_to_class_and_object("submaps", submaps)
        if quantity_to_evaluate == QuantityToPlot.whitespace:
            self._convert_to_class_and_object("device", device)
            self._convert_to_class_and_object("device_specification", device_specification)
            self._convert_to_class_and_object("plmrs_indicator", plmrs_indicator)
            self._convert_to_class_and_object("whitespace_evaluation_type", whitespace_evaluation_type)
            self.set_ws_channel_subset()

        if repack is not None:
            self._convert_to_class_and_object("repack", repack)

        if assignment_type == AssignmentType.test:
            self.test_index = test_index




    def to_string(self):
        if self.type_object == AssignmentType.original:
            string = "".join(["original", self.quantity_to_evaluate_object.name, "map"])
        elif self.type_object == AssignmentType.repack:
            string = "".join([str(self.bandplan), self.repack_object.filename, str(self.repack_object.index)])
        elif self.type_object == AssignmentType.chopofftop:
            string = "".join([str(self.bandplan), "USStationsRemoved"])
        elif self.type_object == AssignmentType.test:
            string = "".join(["test", self.quantity_to_evaluate_object.name, "map", str(self.test_index)])

        if self.quantity_to_evaluate_object == QuantityToPlot.whitespace:
            separator = "_"
            string = "".join([string, separator, self.plmrs_indicator_object.name, separator, self.device_specification_object.name, separator, self.whitespace_evaluation_type_object.name])

        return string

    @property
    def full_directory(self):
        return os.path.join("data", self.subdirectory)

    @property
    def subdirectory(self):
        return os.path.join("".join(["Pickled Files - ", self.quantity_to_evaluate_object.name]), self.type_object.name)


    def make_data(self):

        region_map = self.region_map_spec.fetch_data()
        zero_map = west.data_map.DataMap2D.get_copy_of(region_map)
        zero_map.reset_all_values(0)
        if self.quantity_to_evaluate_object == QuantityToPlot.tv:
            datamap_3D = createTVViewershipFromAssignment(self.region_object, zero_map, self.submaps_object)
        else:
            datamap_3D = createWhitespaceFromAssignment(self.device_specification_object, self.region_object, region_map, self.submaps_object[self.device_specification_object.name])

        if self.quantity_to_evaluate_object == QuantityToPlot.whitespace and self.plmrs_indicator_object == PLMRSExclusions.plmrs_applied:
            reintegratePLMRSExclusions(datamap_3D, self.plmrs_map_object, numpy.logical_and)

        if self.quantity_to_evaluate_object == QuantityToPlot.tv:
            datamap = datamap_3D.sum_all_layers()
        else:
            datamap = datamap_3D.sum_subset_of_layers(self.get_ws_channel_subset())

        self.save_data(datamap)

        return datamap_3D         #Done for testing purposes, usually we will only return the full datamap
        #return datamap

    def set_repack_index(self, index):
        self.repack_object.index = index


    def set_ws_channel_subset(self):
        tvws_channel_list = self.region_object.get_tvws_channel_list()
        #Hack-y
        tvws_channel_list.append(3)
        tvws_channel_list.append(4)
        tvws_channel_list = sorted(tvws_channel_list)
        self._ws_channel_subset = tvws_channel_list[0:len(tvws_channel_list) - self.bandplan]


        #Would be nice if we could generalize this a little more too, i.e. remove channel 13.
        if self.whitespace_evaluation_type_object == WhitespaceEvaluationType.onlyuhf:
            for ch in self._ws_channel_subset:
                if ch <= 13:
                    self._ws_channel_subset.remove(ch)

    def get_ws_channel_subset(self):
        if self._ws_channel_subset is None:
            self.set_ws_channel_subset()
        return self._ws_channel_subset


    def get_whitespace_evaluation_parameters(self):
        """Function that returns whitespace evaluation parameters."""
        return self.device_specification_object, self.plmrs_indicator_object, self.whitespace_evaluation_type_object

    def write_entry_to_pareto_file(self, pareto_filename, mean, median):

        new_entry = [self.type_object, 'N/A', self.bandplan, 'N/A', 'N/A', mean, median]
        if self.type_object == AssignmentType.repack:
            new_entry[1] = self.repack_object.type.name
            new_entry[4] = self.repack_object.index

        if self.quantity_to_evaluate_object == QuantityToPlot.whitespace:
            new_entry[3] = self.device_specification_object.name

        entry_exists_flag = False
        updated_entries = []

        with open(os.path.join("data", pareto_filename), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0:5] == new_entry[0:5]:
                    entry_exists_flag = True
                    updated_entries.append(new_entry)
                else:
                    updated_entries.append(row)

        if not entry_exists_flag:
            updated_entries.append(new_entry)



        with open(os.path.join("data", pareto_filename), 'w') as f:
            writer = csv.writer(f)
            for entry in updated_entries:
                writer.writerow(entry)



    def pickled_statistical_map_exists(self, statistical_metric):
        if self.type_object != AssignmentType.repack:
            self.log.error("There is no 'statistical' map that can be created for this type of assignment.")

        file = os.path.join(self.full_directory, "".join([self.to_string(), "_", statistical_metric.name, ".pcl"]))

        return os.path.isfile(file)

    def set_region(self, all_fids_considered_in_auction):

        def filter_function(station):
            if station.get_channel() in range(52 - self.bandplan, 52):
                #print False
                return False
            else:
                return True
        tvstation_list = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region_object)
        tvstation_list.prune_data(all_fids_considered_in_auction) #Extremely buggy. This will need to go some day.
        print "LENGTH OF ORIGINAL:", len(tvstation_list.stations())
        if self.type_object == AssignmentType.repack:
            tvstation_list.implement_repack(self.bandplan, self.repack_object.index, self.repack_object.filename, self.channel_list)
        elif self.type_object == AssignmentType.chopofftop:

            tvstation_list.remove_entities(filter_function)
            print "AFTER CHOPPING OFF TOP, LENGTH:", len(tvstation_list.stations())
        self.region_object.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tvstation_list)
        for c in self.channel_list:
            if c >= 52 - self.bandplan:
                print "AFTER CHOPPING OFF TOP, LENGTH IN CHANNEL %d ="%c, len(self.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations_by_channel[c])
        print "AFTER CHOPPING OFF TOP, LENGTH IN REGION:", len(self.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations())



    def load_statistical_data(self, statistical_metric):
        return west.data_map.DataMap2D.from_pickle(os.path.join(self.full_directory, "".join([self.to_string(), "_", statistical_metric.name, ".pcl"])))


    def get_map(self):
        """Creates a linear-scale :class:`map.Map` with boundary outlines, a
        white background, and a colorbar. The title is automatically set
        using the Specification information but can be reset with
        :meth:`map.Map.set_title`. Returns a handle to the map object; does
        not save or show the map.
        Needs to be polished for this class"""
        datamap2d = self.fetch_data()

        region_map = self.region_map_spec.fetch_data()
        self.region_map_spec._create_obj_if_needed("boundary")
        boundary = self.region_map_spec.boundary_object

        map = datamap2d.make_map(is_in_region_map=region_map)
        map.add_boundary_outlines(boundary)
        map.add_colorbar(decimal_precision=0)
        map.set_colorbar_label("Number of channels")
        self._set_map_title(map)

        map.add_boundary_outlines(west.boundary.BoundaryContinentalUnitedStatesWithStateBoundaries())
        #new_map.set_colorbar_ticks([0, 10, 20, 30, 40, 50])
        map.set_boundary_color('k')
        map.set_boundary_linewidth(1)
        return map




class Repack(object):

    """Class that describes various parameters of the repack -- the type of reallocation, and the filename associated with that type."""

    def __init__(self, repack_type, repack_index):

        """Initializing the type and filename associated with that type."""

        self.log = getModuleLogger(self)
        self.type = repack_type
        self.index = repack_index
        if self.type == RepackType.A:
            self.filename = "UHFnewUSMinimumStationstoRemove"

        elif self.type == RepackType.Aprime:
            self.filename = "UHFAprimeMinimumStationstoRemove"

        elif self.type == RepackType.Adoubleprime:
            self.filename = "UHFAdoubleprimeMinimumStationstoRemove"

        elif self.type == RepackType.B:
            self.filename = "VHFUSMinimumStationstoRemove"

        elif self.type == RepackType.C:
            self.filename = "VHFFreeUSMinimumStationstoRemove"

        else:
            self.log.error("Invalid type of reallocation entered. Please check your class definition.")

class QuantityToPlot(Enum):
    tv = 1
    whitespace = 2

class AssignmentType(Enum):
    original = 1
    repack = 2
    chopofftop = 3
    test = 4

class RepackType(Enum):
    A = 1
    Aprime = 2
    Adoubleprime = 3
    B = 4
    C = 5

class DeviceSpecification(Enum):
    fixed = 1
    portable = 2

class PLMRSExclusions(Enum):
    plmrs_applied = 1
    plmrs_notapplied = 2

class WhitespaceEvaluationType(Enum):
    total = 1
    onlyuhf = 2

class StatisticalMetricToPlot(Enum):
    mean = 1
    median = 2
    stddev = 3



def createWhitespaceFromAssignment(device_specification, region,
                                   is_in_region_map, submaps):
    """Function which evaluates a whitespace map for a particular TV station-to-channel assignment"""

    #Note: Always make sure that the region and is_in_region_map correspond to the same boundary. Not including this here as it may take up time when we're using this function.

    tvws_channel_list = region.get_tvws_channel_list()
    #Hack-y, ideally we do not need to do this in the code.
    tvws_channel_list.append(3)
    tvws_channel_list.append(4)
    tvws_channel_list = sorted(tvws_channel_list)

    whitespace_map_3D = west.data_map.DataMap3D.from_DataMap2D(is_in_region_map, tvws_channel_list)
    applyCoChannelSubmaps(whitespace_map_3D, region, submaps['cochannel'], numpy.logical_and)
    if device_specification == DeviceSpecification.fixed:
        applyAdjChannelSubmaps(whitespace_map_3D, region, submaps['adjchannel'], numpy.logical_and)
    return whitespace_map_3D

def createTVViewershipFromAssignment(region,
                                     zero_map, submaps):
    """Function which evaluates a TV viewership map for a particular TV station-to-channel assignment"""

    tv_channel_list = region.get_channel_list()
    tv_channel_list.remove(37)

    tv_viewership_map_3D = west.data_map.DataMap3D.from_DataMap2D(zero_map, tv_channel_list)
    applyCoChannelSubmaps(tv_viewership_map_3D, region, submaps, lambda x, y: x + y)
    return tv_viewership_map_3D


def applyCoChannelSubmaps(cochannel_application_map_3D, region, submaps, combination_function):
    """Function that applies co-channel submaps to cochannel_application_map_3D according to the combination function given as input.
    cochannel_application_map_3D itself is modified."""

    tvstation_list = region.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations]
    for s in tvstation_list.stations():
        if s.get_facility_id() not in submaps.keys() or submaps[s.get_facility_id()][1] is None:
            if not region.location_is_in_region(s.get_location()):
                print "Skipping application of submap as this station is outside the bounds of the original map"
                continue
            else:
                print s.get_facility_id()
                raise ValueError("This station is supposed to have a submap associated with it. Please check if the submaps entered are correct.")
        else:
            if s.get_channel() not in cochannel_application_map_3D.get_layer_descr_list():
                print s.get_channel()
                print "Skipping application of submap as this station is not on a valid TVWS channel"
                continue
            try:
                cochannel_application_map_3D.get_layer(s.get_channel()).reintegrate_submap(submaps[s.get_facility_id()][1], combination_function)
            except ValueError:
                print "Skipping application of submap as this station is outside the bounds of the original map or submap is not comparable (latitudes or longitudes differ)"
                continue



def applyAdjChannelSubmaps(adjchannel_application_map_3D, region, submaps, combination_function):
    """Function that applies adjacent channel submaps to adjchannel_application_map_3D according to the combination function given as input.
    adjchannel_application_map_3D itself is modified."""

    tvstation_list = region.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations]
    layer_list = adjchannel_application_map_3D.get_layer_descr_list()

    for s in tvstation_list.stations():
        if s.get_facility_id() not in submaps.keys() or submaps[s.get_facility_id()][1] is None:
            if not region.location_is_in_region(s.get_location()):
                print "Skipping application of submap as this station is outside the bounds of the original map"
            else:
                raise ValueError("This station is supposed to have a submap associated with it. Please check if the submaps entered are correct.")
        else:
            #Applying submap to s.channel() + 1 ('upper incremental channel')
            if not west.helpers.channels_are_adjacent_in_frequency(region, s.get_channel(), s.get_channel() + 1):
                print s.get_channel() + 1
                print ("Skipping application of submap to upper incremental channel as channels are not adjacent in frequency")
            elif not s.get_channel() + 1 in layer_list:
                print s.get_channel() + 1
                print "Skipping application of submap to upper incremental channel as upper incremental channel is not a valid TVWS channel"
            else:
                try:
                    adjchannel_application_map_3D.get_layer(s.get_channel() + 1).reintegrate_submap(submaps[s.get_facility_id()][1], combination_function)
                except ValueError:
                    print "Skipping application of submap as this station is outside the bounds of the original map"

            #Applying submap to s.channel() - 1 ('lower incremental channel')
            if not west.helpers.channels_are_adjacent_in_frequency(region, s.get_channel(), s.get_channel() - 1):
                print s.get_channel() - 1
                print ("Skipping application of submap to lower incremental channel as channels are not adjacent in frequency")
            elif not s.get_channel() - 1 in layer_list:
                print s.get_channel() - 1
                print "Skipping application of submap to lower incremental channel as lower incremental channel is not a valid TVWS channel"
            else:
                try:
                    adjchannel_application_map_3D.get_layer(s.get_channel() - 1).reintegrate_submap(submaps[s.get_facility_id()][1], combination_function)
                except ValueError:
                    print "Skipping application of submap as this station is outside the bounds of the original map or submap is not comparable (latitudes or longitudes differ)"



def reintegratePLMRSExclusions(whitespace_map_3D, plmrs_exclusions_map, combination_function):
    """Function that reintegrates a PLMRS exclusions map into whitespace_map_3D according to the combination function given as input.
    whitespace_map_3D itself is modified."""

    whitespace_map_3D.raise_error_if_datamaps_are_incomparable(plmrs_exclusions_map)

    for channel in whitespace_map_3D.get_layer_descr_list():
        whitespace_map_3D.get_layer(channel).reintegrate_submap(plmrs_exclusions_map.get_layer(channel), combination_function)

















