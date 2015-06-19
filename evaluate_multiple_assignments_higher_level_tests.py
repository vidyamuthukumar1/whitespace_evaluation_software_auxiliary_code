from evaluate_multiple_assignments import Assignment, Repack, QuantityToPlot, DeviceSpecification, AssignmentType, RepackType, WhitespaceEvaluationType, PLMRSExclusions
from data_management_vidya import SpecificationPLMRSMap
from west.region_united_states import RegionUnitedStates
from west.ruleset_fcc2012 import RulesetFcc2012
from west.data_management import SpecificationRegionMap, SpecificationDataMap
from west.boundary import BoundaryContinentalUnitedStates, BoundaryContinentalUnitedStatesWithStateBoundaries
from west.device import Device
import west.data_manipulation
import west.protected_entities_tv_stations
import west.helpers
import west.population

from geopy.distance import vincenty

import unittest
from copy import copy
import os
import csv
import pickle

from protected_entities_tv_stations_vidya import ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack


def load_submaps(buffersize):
    with open("stamps_with_buffer=%dkm.pkl"%buffersize, 'r') as f:
        stamps = pickle.load(f)

    return stamps

def not_function(latitude, longitude, latitude_index, longitude_index, current_value):
    return 1 - current_value


class higherLevelIntegrationTests(unittest.TestCase):

    def setUp(self):

        self.region = RegionUnitedStates()
        self.region._boundary = BoundaryContinentalUnitedStatesWithStateBoundaries()
        self.ruleset = RulesetFcc2012()
        self.tvws_channel_list = range(2, 52)
        self.tvws_channel_list.remove(37)
        self.tv_channel_list = copy(self.tvws_channel_list)

        datamap_spec = SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
        self.region_map_spec = SpecificationRegionMap(BoundaryContinentalUnitedStates, datamap_spec)
        self.region_map = self.region_map_spec.fetch_data()
        self.plmrs_exclusions_map_spec = SpecificationPLMRSMap(self.region_map_spec, self.region, self.ruleset)
        self.plmrs_exclusions_map = self.plmrs_exclusions_map_spec.fetch_data()
        self.population_map_spec = west.data_management.SpecificationPopulationMap(self.region_map_spec, west.population.PopulationData)
        self.population_map = self.population_map_spec.fetch_data()

        self.good_facility_ids = []
        with open(os.path.join("data", "FromVijay", "C-All free", "C-0channelsRemoved", "0VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                self.good_facility_ids.append(row[0])


        self.submaps_tv = load_submaps(0)
        for submap in self.submaps_tv.values():
            submap[1].update_all_values_via_function(not_function)

        self.submaps_ws_fixed = {'cochannel': load_submaps(11), 'adjchannel': load_submaps(1)}
        self.submaps_ws_portable = {'cochannel': load_submaps(4)}



    def test_empty_region(self):

        def remove_all(station):
            return False

        #TV viewership test
        test_assignment = Assignment(AssignmentType.test, QuantityToPlot.tv,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, self.submaps_tv,
                                     0, test_index = 1)

        empty_protected_entities = ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)
        empty_protected_entities.remove_entities(remove_all)

        test_assignment.region_object.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, empty_protected_entities)

        total_tv_map = test_assignment.make_data()

        for i in range(400):
            for j in range(600):
                self.assertEqual(total_tv_map.get_value_by_index(i, j), 0)

        #Portable whitespace test
        test_assignment = Assignment(AssignmentType.test, QuantityToPlot.whitespace,
                   self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                   self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                   0, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                   whitespace_evaluation_type = WhitespaceEvaluationType.total, test_index = 1)

        test_assignment.region_object.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, empty_protected_entities)

        total_portable_ws_map = test_assignment.make_data()

        for i in range(400):
            for j in range(600):
                self.assertEqual(total_portable_ws_map.get_value_by_index(i, j), 49 * self.region_map.get_value_by_index(i, j))


        #Fixed whitespace test
        test_assignment = Assignment(AssignmentType.test, QuantityToPlot.whitespace,
                   self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                   self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                   0, device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                   whitespace_evaluation_type = WhitespaceEvaluationType.total, test_index = 1)

        test_assignment.region_object.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, empty_protected_entities)

        total_fixed_ws_map = test_assignment.make_data()

        for i in range(400):
            for j in range(600):
                self.assertEqual(total_fixed_ws_map.get_value_by_index(i, j), 49 * self.region_map.get_value_by_index(i, j))






    def test_station_outside_us(self):
        def remove_all_but_one(station):
            return station.get_facility_id() == '83180'


        #TV viewership test
        test_assignment = Assignment(AssignmentType.test, QuantityToPlot.tv,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, self.submaps_tv,
                                     0, test_index = 3)

        empty_protected_entities = ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)
        empty_protected_entities.remove_entities(remove_all_but_one)

        test_assignment.region_object.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, empty_protected_entities)

        total_tv_map = test_assignment.make_data()

        for i in range(400):
            for j in range(600):
                self.assertEqual(total_tv_map.get_value_by_index(i, j), 0)

        #Portable whitespace test
        test_assignment = Assignment(AssignmentType.test, QuantityToPlot.whitespace,
                   self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                   self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                   0, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                   whitespace_evaluation_type = WhitespaceEvaluationType.total, test_index = 3)

        test_assignment.region_object.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, empty_protected_entities)

        total_portable_ws_map = test_assignment.make_data()

        for i in range(400):
            for j in range(600):
                self.assertEqual(total_portable_ws_map.get_value_by_index(i, j), 49 * self.region_map.get_value_by_index(i, j))


        #Fixed whitespace test
        test_assignment = Assignment(AssignmentType.test, QuantityToPlot.whitespace,
                   self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                   self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                   0, device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                   whitespace_evaluation_type = WhitespaceEvaluationType.total, test_index = 3)

        test_assignment.region_object.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, empty_protected_entities)

        total_fixed_ws_map = test_assignment.make_data()

        for i in range(400):
            for j in range(600):
                self.assertEqual(total_fixed_ws_map.get_value_by_index(i, j), 49 * self.region_map.get_value_by_index(i, j))

    def test_shuffle_repack(self):

        #TV viewership test
        original_assignment = Assignment(AssignmentType.original, QuantityToPlot.tv,
                                         self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                         self.tv_channel_list, self.submaps_tv,
                                         0)

        original_assignment.set_region(self.good_facility_ids)
        original_tv_map = original_assignment.make_data()



        test_assignment = Assignment(AssignmentType.repack, QuantityToPlot.tv,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, self.submaps_tv,
                                     0, repack = Repack(RepackType.C, 0))

        test_assignment.set_region(self.good_facility_ids)


        test_tv_map = test_assignment.make_data()

        for i in range(400):
            for j in range(600):
                self.assertEqual(original_tv_map.get_value_by_index(i, j), test_tv_map.get_value_by_index(i, j))


        #Portable whitespace test

        original_assignment = Assignment(AssignmentType.original, QuantityToPlot.whitespace,
                                         self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                         self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                         0, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                                         whitespace_evaluation_type = WhitespaceEvaluationType.total)

        original_assignment.set_region(self.good_facility_ids)
        original_ws_map = original_assignment.make_data()


        test_assignment = Assignment(AssignmentType.repack, QuantityToPlot.whitespace,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                     0, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                                     whitespace_evaluation_type = WhitespaceEvaluationType.total, repack = Repack(RepackType.C, 0))

        test_assignment.set_region(self.good_facility_ids)

        test_ws_map = test_assignment.make_data()
        original_map = original_assignment.get_map()
        original_map.blocking_show()
        test_map = test_assignment.get_map()
        test_map.blocking_show()

        avg_diff = 0

        cdf = west.data_manipulation.calculate_cdf_from_datamap2d(original_ws_map, self.population_map, self.region_map)
        print "CDF:", cdf

        for i in range(400):
            for j in range(600):
                avg_diff += abs(original_ws_map.get_value_by_index(i, j) - test_ws_map.get_value_by_index(i, j))


        print "AVERAGE DIFFERENCE: ", avg_diff
        avg_diff = avg_diff / 240000.0

        self.assertLess(avg_diff, 0.013)



    def test_one_station_inside_us(self):

        print "TEST TO BE CONSIDERED"

        def remove_all_but_one(station):
            return station.get_facility_id() == '1005'


        def buffer0(latitude, longitude, latitude_index, longitude_index, current_value):
            return vincenty((latitude, longitude), loc) <= max_protected_radius_km

        def buffer1(latitude, longitude, latitude_index, longitude_index, current_value):
            return vincenty((latitude, longitude), loc) <= max_protected_radius_km + 1

        def buffer4(latitude, longitude, latitude_index, longitude_index, current_value):
            return vincenty((latitude, longitude), loc) <= max_protected_radius_km + 4

        def buffer11(latitude, longitude, latitude_index, longitude_index, current_value):
            return vincenty((latitude, longitude), loc) <= max_protected_radius_km + 11

        #TV viewership test
        test_assignment = Assignment(AssignmentType.test, QuantityToPlot.tv,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, self.submaps_tv,
                                     0, test_index = 2)

        protected_entities_one_station = ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)
        protected_entities_one_station.remove_entities(remove_all_but_one)

        station_to_consider = protected_entities_one_station.stations()[0]

        ch = station_to_consider.get_channel()
        loc = station_to_consider.get_location()
        max_protected_radius_km = self.ruleset.get_tv_protected_radius_km(station_to_consider, loc)

        test_assignment.region_object.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, protected_entities_one_station)
        total_tv_map = test_assignment.make_data()
        test_map = test_assignment.get_map()
        test_map.blocking_show()





        cochannel_map = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(self.region_map)
        cochannel_map.update_all_values_via_function(buffer0)

        for i in range(400):
            for j in range(600):
                print i, j
                #self.assertEqual(cochannel_map.get_value_by_index(i, j), 0)
                self.assertEqual(total_tv_map.get_value_by_index(i, j), cochannel_map.get_value_by_index(i, j))

        #Portable whitespace test
        test_assignment = Assignment(AssignmentType.test, QuantityToPlot.whitespace,
                                    self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                    self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                    0, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                                    whitespace_evaluation_type = WhitespaceEvaluationType.total, test_index = 2)

        test_assignment.region_object.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, protected_entities_one_station)

        total_portable_ws_map = test_assignment.make_data()

        cochannel_map.update_all_values_via_function(buffer4)

        for i in range(400):
            for j in range(600):
                self.assertEqual(total_portable_ws_map.get_value_by_index(i, j), self.region_map.get_value_by_index(i, j) * (49 - cochannel_map.get_value_by_index(i, j)))


        #Fixed whitespace test
        test_assignment = Assignment(AssignmentType.test, QuantityToPlot.whitespace,
                                    self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                    self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                    0, device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                                    whitespace_evaluation_type = WhitespaceEvaluationType.total, test_index = 2)

        test_assignment.region_object.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, protected_entities_one_station)

        total_fixed_ws_map = test_assignment.make_data()

        cochannel_map.update_all_values_via_function(buffer11)
        adjchannel_map = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(self.region_map)
        adjchannel_map.update_all_values_via_function(buffer1)

        for i in range(400):
            for j in range(600):
                self.assertEqual(total_fixed_ws_map.get_value_by_index(i, j), self.region_map.get_value_by_index(i, j) * (49 - cochannel_map.get_value_by_index(i, j) - 2 * adjchannel_map.get_value_by_index(i, j)))




    """
    def test_chop_off_top(self):
        #Note: Use make_data() to return 3D maps for this test.

        #TV viewership test: NEEDS TO BE FIXED

        test_assignment = Assignment(AssignmentType.chopofftop, QuantityToPlot.tv,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, self.submaps_tv,
                                     8)

        print "NUMBER OF CHANNELS REMOVED:", test_assignment.bandplan

        test_assignment.set_region(self.good_facility_ids)
        print "LEN OF TOTAL STATIONS AFTER CHOPPING OFF TOP IN MAIN", len(test_assignment.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations())
        print "LEN OF STATIONS ON CHANNEL 44 AFTER CHOPPING OFF TOP IN MAIN", 44, len(test_assignment.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations_by_channel[44])
        print "LEN OF STATIONS ON CHANNEL 45 AFTER CHOPPING OFF TOP IN MAIN", 45, len(test_assignment.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations_by_channel[45])
        print "LEN OF STATIONS ON CHANNEL 46 AFTER CHOPPING OFF TOP IN MAIN", 46, len(test_assignment.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations_by_channel[46])
        print "LEN OF STATIONS ON CHANNEL 47 AFTER CHOPPING OFF TOP IN MAIN", 47, len(test_assignment.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations_by_channel[47])
        print "LEN OF STATIONS ON CHANNEL 48 AFTER CHOPPING OFF TOP IN MAIN", 48, len(test_assignment.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations_by_channel[48])
        print "LEN OF STATIONS ON CHANNEL 49 AFTER CHOPPING OFF TOP IN MAIN", 49, len(test_assignment.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations_by_channel[49])
        print "LEN OF STATIONS ON CHANNEL 50 AFTER CHOPPING OFF TOP IN MAIN", 50, len(test_assignment.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations_by_channel[50])
        print "LEN OF STATIONS ON CHANNEL 51 AFTER CHOPPING OFF TOP IN MAIN", 51, len(test_assignment.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations_by_channel[51])


        for c in self.tv_channel_list:
            print c
            l1 = len(test_assignment.region_object.protected_entities[west.protected_entities_tv_stations.ProtectedEntitiesTVStations].stations_by_channel[c])
            print l1

        total_tv_map_3D = test_assignment.make_data()
        total_tv_map = total_tv_map_3D.sum_all_layers()



        original_assignment = Assignment(AssignmentType.original, QuantityToPlot.tv,
                                             self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                             self.tv_channel_list, self.submaps_tv,
                                             0)


        original_assignment.set_region(self.good_facility_ids)



        original_tv_map_3D = original_assignment.make_data()
        original_tv_map_total = original_tv_map_3D.sum_all_layers()
        original_tv_map_cleared_spectrum = original_tv_map_3D.sum_subset_of_layers(range(44, 52))



        for c in self.tv_channel_list:
            print c
            if c < 52 - 8:
                for i in range(400):
                    for j in range(600):
                        self.assertEqual(total_tv_map_3D.get_layer(c).get_value_by_index(i, j), original_tv_map_3D.get_layer(c).get_value_by_index(i, j))
            else:
                for i in range(400):
                    for j in range(600):
                        #print i, j
                        self.assertEqual(total_tv_map_3D.get_layer(c).get_value_by_index(i, j), 0)

        for i in range(400):
            for j in range(600):
                print total_tv_map.get_value_by_index(i, j)
                print original_tv_map_total.get_value_by_index(i, j)
                print original_tv_map_cleared_spectrum.get_value_by_index(i, j)
                self.assertEqual(total_tv_map.get_value_by_index(i, j), original_tv_map_total.get_value_by_index(i, j) - original_tv_map_cleared_spectrum.get_value_by_index(i, j))



        #Portable whitespace test: PASSED

        original_assignment = Assignment(AssignmentType.original, QuantityToPlot.whitespace,
                   self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                   self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                   0, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                   whitespace_evaluation_type = WhitespaceEvaluationType.total)


        original_assignment.set_region(self.good_facility_ids)
        print original_assignment.get_ws_channel_subset()



        original_ws_map_3D = original_assignment.make_data()
        original_ws_map_subset = original_ws_map_3D.sum_subset_of_layers(original_assignment.get_ws_channel_subset()[0: len(original_assignment.get_ws_channel_subset()) - 14])

        test_assignment = Assignment(AssignmentType.chopofftop, QuantityToPlot.whitespace,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                     14, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                                     whitespace_evaluation_type = WhitespaceEvaluationType.total)


        test_assignment.set_region(self.good_facility_ids)


        test_ws_map_3D = test_assignment.make_data()
        test_ws_map_subset = test_ws_map_3D.sum_subset_of_layers(test_assignment.get_ws_channel_subset())

        test_ws_map_cleared = test_ws_map_3D.sum_subset_of_layers(range(38, 52))

        for i in range(400):
            for j in range(600):
                self.assertEqual(original_ws_map_subset.get_value_by_index(i, j), test_ws_map_subset.get_value_by_index(i, j))
                self.assertEqual(test_ws_map_cleared.get_value_by_index(i, j), 14 * self.region_map.get_value_by_index(i, j))

        for c in self.tvws_channel_list:
            for i in range(400):
                for j in range(600):
                    if c < 38:
                        self.assertEqual(test_ws_map_3D.get_layer(c).get_value_by_index(i, j), original_ws_map_3D.get_layer(c).get_value_by_index(i, j))
                    else:
                        self.assertEqual(test_ws_map_3D.get_layer(c).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))


        #Fixed whitespace test: PASSED
        original_assignment = Assignment(AssignmentType.original, QuantityToPlot.whitespace,
                                         self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                         self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                         0, device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                                         whitespace_evaluation_type = WhitespaceEvaluationType.total)

        original_assignment.set_region(self.good_facility_ids)

        original_ws_map_3D = original_assignment.make_data()
        original_ws_map_subset = original_ws_map_3D.sum_subset_of_layers(test_assignment.get_ws_channel_subset())

        test_assignment = Assignment(AssignmentType.chopofftop, QuantityToPlot.whitespace,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                     14, device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, plmrs_indicator = PLMRSExclusions.plmrs_notapplied,
                                     whitespace_evaluation_type = WhitespaceEvaluationType.total)


        test_assignment.set_region(self.good_facility_ids)


        test_ws_map_3D = test_assignment.make_data()
        test_ws_map_subset = test_ws_map_3D.sum_subset_of_layers(test_assignment.get_ws_channel_subset())

        test_ws_map_cleared = test_ws_map_3D.sum_subset_of_layers(range(38, 52))

        for i in range(400):
            for j in range(600):
                self.assertEqual(original_ws_map_subset.get_value_by_index(i, j), test_ws_map_subset.get_value_by_index(i, j))
                self.assertEqual(test_ws_map_cleared.get_value_by_index(i, j), 14 * self.region_map.get_value_by_index(i, j))

        for c in self.tvws_channel_list:
            for i in range(400):
                for j in range(600):
                    if c < 38:
                        self.assertEqual(test_ws_map_3D.get_layer(c).get_value_by_index(i, j), original_ws_map_3D.get_layer(c).get_value_by_index(i, j))
                    else:
                        self.assertEqual(test_ws_map_3D.get_layer(c).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))"""




unittest.main()























