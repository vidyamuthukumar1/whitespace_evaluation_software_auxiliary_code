from evaluate_multiple_assignments import createWhitespaceFromAssignment, createTVViewershipFromAssignment, applyCoChannelSubmaps, applyAdjChannelSubmaps, reintegratePLMRSExclusions, DeviceSpecification
from evaluate_multiple_assignments import Assignment, Repack, QuantityToPlot, DeviceSpecification, AssignmentType, RepackType, WhitespaceEvaluationType, PLMRSExclusions
from data_management_vidya import SpecificationPLMRSMap
from west.region_united_states import RegionUnitedStates
from west.ruleset_fcc2012 import RulesetFcc2012
from west.data_management import SpecificationRegionMap, SpecificationDataMap
from west.boundary import BoundaryContinentalUnitedStates, BoundaryContinentalUnitedStatesWithStateBoundaries
from west.protected_entity_tv_station import ProtectedEntityTVStation
from west.device import Device
import west.protected_entities_tv_stations
import west.helpers
import protected_entities_tv_stations_vidya

import unittest
from copy import copy
from geopy.distance import vincenty
import numpy
import pickle
import os
import csv


def load_submaps(buffersize):
    with open("stamps_with_buffer=%dkm.pkl"%buffersize, 'r') as f:
        stamps = pickle.load(f)

    return stamps

"""class EvaluateAssignmentsTestCase(unittest.TestCase):

    def setUp(self):
        self.region = RegionUnitedStates()
        self.region._boundary = BoundaryContinentalUnitedStatesWithStateBoundaries()
        self.ruleset = RulesetFcc2012()
        self.tvws_channel_list = range(2, 52)
        self.tvws_channel_list.remove(37)
        self.tv_channel_list = copy(self.tvws_channel_list)

        datamap_spec = SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
        region_map_spec = SpecificationRegionMap(BoundaryContinentalUnitedStates, datamap_spec)
        self.region_map = region_map_spec.fetch_data()

        self.good_facility_ids = []
        with open(os.path.join("data", "FromVijay", "C-All free", "C-0channelsRemoved", "0VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                self.good_facility_ids.append(row[0])




    def test_apply_cochannel_submaps(self):

        test_submaps = {}

        tv_stations = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)

        #Test for station outside boundary of US
        tv_station_outside_boundary_lat = 17
        tv_station_outside_boundary_lon = -64
        tv_station_outside_boundary = ProtectedEntityTVStation(tv_stations, self.region, tv_station_outside_boundary_lat, tv_station_outside_boundary_lon, 23,
                                              659, 124.2, 'DT')
        submap_outside_boundary = west.data_map.DataMap2D.from_specification((15, 19), (-66, 60), 50, 50)
        submap_outside_boundary.reset_all_values(0)
        test_submaps['test_station_outside_us'] = ['fcc', west.data_map.DataMap2D.from_specification((15, 19), (-66, 60), 50, 50)]
        tv_station_outside_boundary.add_facility_id('test_station_outside_us')
        tv_stations._entities = [tv_station_outside_boundary]
        tv_stations._refresh_cached_data()

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)

        ws_map_3D = west.data_map.DataMap3D.from_DataMap2D(self.region_map, self.tvws_channel_list)

        applyCoChannelSubmaps(ws_map_3D, self.region, test_submaps, numpy.logical_and)
        applyAdjChannelSubmaps(ws_map_3D, self.region, test_submaps, numpy.logical_and)

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(23).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(24).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(22).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))


        #Test for station inside US but without valid submap
        tv_station_inside_boundary_without_submap_lat = self.region_map.latitudes[200]
        tv_station_inside_boundary_without_submap_lon = self.region_map.longitudes[300]
        tv_station_inside_boundary_without_submap = ProtectedEntityTVStation(tv_stations, self.region, tv_station_inside_boundary_without_submap_lat, tv_station_inside_boundary_without_submap_lon, 23,
                                                                             659, 124.2, 'DT')
        tv_station_inside_boundary_without_submap.add_facility_id('test_station_inside_us_invalid')
        tv_stations._entities = [tv_station_inside_boundary_without_submap]
        tv_stations._refresh_cached_data()
        test_submaps['test_station_inside_us_invalid'] = ['fcc', None]

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)

        self.assertRaises(ValueError, applyCoChannelSubmaps, ws_map_3D, self.region, test_submaps, numpy.logical_and)
        self.assertRaises(ValueError, applyAdjChannelSubmaps, ws_map_3D, self.region, test_submaps, numpy.logical_and)

        #Test for station inside US but on an invalid TVWS channel
        tv_station_inside_boundary_on_invalid_channel_lat = self.region_map.latitudes[200]
        tv_station_inside_boundary_on_invalid_channel_lon = self.region_map.longitudes[300]
        tv_station_inside_boundary_on_invalid_channel = ProtectedEntityTVStation(tv_stations, self.region, tv_station_inside_boundary_on_invalid_channel_lat, tv_station_inside_boundary_on_invalid_channel_lon, 53,
                                                                                 659, 124.2, 'DT')
        tv_station_inside_boundary_on_invalid_channel.add_facility_id('test_station_inside_us_invalid_channel')
        tv_stations._entities = [tv_station_inside_boundary_on_invalid_channel]
        tv_stations._refresh_cached_data()


        submap_invalid_channel = west.helpers.generate_submap_for_protected_entity(self.region_map, tv_station_inside_boundary_on_invalid_channel)
        submap_invalid_channel.reset_all_values(0)
        test_submaps['test_station_inside_us_invalid_channel'] = ['fcc', submap_invalid_channel]

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)

        #Should display appropriate skipping application message
        applyCoChannelSubmaps(ws_map_3D, self.region, test_submaps, numpy.logical_and)
        applyAdjChannelSubmaps(ws_map_3D, self.region, test_submaps, numpy.logical_and)


        #Test for station inside US but with incomparable submap
        tv_station_inside_boundary_incomparable_submap_lat = self.region_map.latitudes[200]
        tv_station_inside_boundary_incomparable_submap_lon = self.region_map.longitudes[300]
        tv_station_inside_boundary_incomparable_submap = ProtectedEntityTVStation(tv_stations, self.region, tv_station_inside_boundary_without_submap_lat, tv_station_inside_boundary_without_submap_lon, 23,
                                                                         659, 124.2, 'DT')
        tv_station_inside_boundary_incomparable_submap.add_facility_id('test_station_inside_us_incomparable')

        submap_incomparable = west.data_map.DataMap2D.from_specification((tv_station_inside_boundary_incomparable_submap_lat - 2, tv_station_inside_boundary_incomparable_submap_lat  + 2),
            (tv_station_inside_boundary_incomparable_submap_lon - 2, tv_station_inside_boundary_incomparable_submap_lon + 2), 10, 10)
        submap_incomparable.reset_all_values(0)
        tv_stations._entities = [tv_station_inside_boundary_incomparable_submap]
        tv_stations._refresh_cached_data()

        test_submaps['test_station_inside_us_incomparable'] = ['fcc', submap_incomparable]

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)
        #Should display appropriate skipping application message
        applyCoChannelSubmaps(ws_map_3D, self.region, test_submaps, numpy.logical_and)
        applyAdjChannelSubmaps(ws_map_3D, self.region, test_submaps, numpy.logical_and)

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(23).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(24).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(22).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))


        #Test for station with entirely valid submap

        tv_station_inside_boundary_valid_submap_lat = self.region_map.latitudes[200]
        tv_station_inside_boundary_valid_submap_lon = self.region_map.longitudes[300]
        tv_station_inside_boundary_valid_submap = ProtectedEntityTVStation(tv_stations, self.region, tv_station_inside_boundary_valid_submap_lat, tv_station_inside_boundary_valid_submap_lon, 23,
                                                                                  659, 124.2, 'DT')
        tv_station_inside_boundary_valid_submap.add_facility_id('test_station_inside_us_valid')

        tv_stations._entities = [tv_station_inside_boundary_valid_submap]
        tv_stations._refresh_cached_data()

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)


        min_lat_index = 170
        max_lat_index = 230
        min_lon_index = 280
        max_lon_index = 320
        submap_valid = west.data_map.DataMap2D.from_specification((self.region_map.latitudes[min_lat_index], self.region_map.latitudes[max_lat_index]),
                                                                  (self.region_map.longitudes[min_lon_index], self.region_map.longitudes[max_lon_index]),
                                                                  max_lat_index - min_lat_index + 1, max_lon_index - min_lon_index + 1)

        submap_valid.reset_all_values(0)

        test_submaps['test_station_inside_us_valid'] = ['fcc', submap_valid]

        applyCoChannelSubmaps(ws_map_3D, self.region, test_submaps, numpy.logical_and)

        def is_outside_valid_submap(latitude, longitude, latitude_index, longitude_index, current_value):
            if current_value == 0:
                return 0

            return latitude_index < min_lat_index or latitude_index > max_lat_index or longitude_index < min_lon_index or longitude_index > max_lon_index

        reqd_map = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(self.region_map)
        reqd_map.update_all_values_via_function(is_outside_valid_submap)

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(23).get_value_by_index(i, j), reqd_map.get_value_by_index(i, j))


    def test_apply_adj_channel_submaps(self):

        test_submaps = {}

        tv_stations = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)


        #Test for station whose lower channel is adjacent and upper channel is not
        tv_station_lower_channel_adj_lat = self.region_map.latitudes[200]
        tv_station_lower_channel_adj_lon = self.region_map.longitudes[300]
        tv_station_lower_channel_adj = ProtectedEntityTVStation(tv_stations, self.region, tv_station_lower_channel_adj_lat, tv_station_lower_channel_adj_lon, 13,
                                                                           659, 124.2, 'DT')
        tv_station_lower_channel_adj.add_facility_id('test_station_lower_channel_adj')

        tv_stations._entities = [tv_station_lower_channel_adj]
        tv_stations._refresh_cached_data()

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)


        min_lat_index = 170
        max_lat_index = 230
        min_lon_index = 280
        max_lon_index = 320
        submap_lower_channel_adj = west.data_map.DataMap2D.from_specification((self.region_map.latitudes[min_lat_index], self.region_map.latitudes[max_lat_index]),
                                                                  (self.region_map.longitudes[min_lon_index], self.region_map.longitudes[max_lon_index]),
                                                                  max_lat_index - min_lat_index + 1, max_lon_index - min_lon_index + 1)

        submap_lower_channel_adj.reset_all_values(0)

        test_submaps['test_station_lower_channel_adj'] = ['fcc', submap_lower_channel_adj]

        ws_map_3D = west.data_map.DataMap3D.from_DataMap2D(self.region_map, self.tvws_channel_list)

        def is_outside_valid_submap(latitude, longitude, latitude_index, longitude_index, current_value):
            if current_value == 0:
                return 0

            return latitude_index < min_lat_index or latitude_index > max_lat_index or longitude_index < min_lon_index or longitude_index > max_lon_index

        reqd_map = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(self.region_map)
        reqd_map.update_all_values_via_function(is_outside_valid_submap)

        applyAdjChannelSubmaps(ws_map_3D, self.region, test_submaps, numpy.logical_and)

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(13).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(12).get_value_by_index(i, j), reqd_map.get_value_by_index(i, j))

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(14).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))


        #Test for station whose upper channel is adjacent and whose lower channel is not
        ws_map_3D = west.data_map.DataMap3D.from_DataMap2D(self.region_map, self.tvws_channel_list)
        tv_station_lower_channel_adj._channel = 14
        tv_stations._entities = [tv_station_lower_channel_adj]
        tv_stations._refresh_cached_data()
        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)

        applyAdjChannelSubmaps(ws_map_3D, self.region, test_submaps, numpy.logical_and)

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(14).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(15).get_value_by_index(i, j), reqd_map.get_value_by_index(i, j))

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(13).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))

        #Test for station whose both upper and lower channels are adjacent

        ws_map_3D = west.data_map.DataMap3D.from_DataMap2D(self.region_map, self.tvws_channel_list)
        tv_station_lower_channel_adj._channel = 23
        tv_stations._entities = [tv_station_lower_channel_adj]
        tv_stations._refresh_cached_data()
        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)

        applyAdjChannelSubmaps(ws_map_3D, self.region, test_submaps, numpy.logical_and)

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(23).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(22).get_value_by_index(i, j), reqd_map.get_value_by_index(i, j))

        for i in range(400):
            for j in range(600):
                self.assertEqual(ws_map_3D.get_layer(24).get_value_by_index(i, j), reqd_map.get_value_by_index(i, j))



    #No test required for applying PLMRS exclusions


    def test_create_tv_viewership_from_assignment(self):

        def not_function(latitude, longitude, latitude_index, longitude_index, current_value):
            return 1 - current_value

        submaps_tv = load_submaps(0)

        #Because submaps by default have 1 for whitespace and 0 for excluded areas. For TV submaps, we want this the other way round.
        for submap_tv in submaps_tv.values():
            submap_tv[1].update_all_values_via_function(not_function)

        zero_map = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)
        zero_map.reset_all_values(0)
        tvws_channel_list = range(2, 37) + range(38, 52)


        #Test for empty region
        tv_stations = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)
        tv_stations._entities = []
        tv_stations._refresh_cached_data()
        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)
        test_map_3D = createTVViewershipFromAssignment(self.region, zero_map, submaps_tv)


        for c in tvws_channel_list:
            for i in range(400):
                for j in range(600):
                    self.assertEqual(test_map_3D.get_layer(c).get_value_by_index(i, j), 0)

        #Test for region with only one circular submap

        def filter_function_1(station):
            return station.get_facility_id() == '1005'
        tv_stations = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)
        tv_stations.remove_entities(filter_function_1)

        max_protected_radius_km = self.ruleset.get_tv_protected_radius_km(tv_stations.stations()[0], tv_stations.stations()[0].get_location())

        def inside_circular_contour(latitude, longitude, latitude_index, longitude_index, current_value):
            return vincenty((latitude, longitude), tv_stations.stations()[0].get_location()) <= max_protected_radius_km

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)

        reqd_map_3D = west.data_map.DataMap3D.from_DataMap2D(zero_map, tvws_channel_list)

        reqd_map_3D.get_layer(17).update_all_values_via_function(inside_circular_contour)

        test_map_3D = createTVViewershipFromAssignment(self.region, zero_map, submaps_tv)

        for c in tvws_channel_list:
            for i in range(400):
                for j in range(600):
                    self.assertEqual(test_map_3D.get_layer(c).get_value_by_index(i, j), reqd_map_3D.get_layer(c).get_value_by_index(i, j))


        #Test for region with one circular submap, and one outside continental US
        tv_station_outside_boundary_lat = 17
        tv_station_outside_boundary_lon = -64
        tv_station_outside_boundary = ProtectedEntityTVStation(tv_stations, self.region, tv_station_outside_boundary_lat, tv_station_outside_boundary_lon, 23,
                                                               659, 124.2, 'DT')
        tv_station_outside_boundary.add_facility_id('test_station_outside_us')
        submap_outside_boundary = west.data_map.DataMap2D.from_specification((15, 19), (-66, 60), 50, 50)
        submap_outside_boundary.reset_all_values(0)
        submaps_tv['test_station_outside_us'] = ['fcc', submap_outside_boundary]

        tv_stations._add_entity(tv_station_outside_boundary)
        tv_stations._refresh_cached_data()

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)

        test_map_3D = createTVViewershipFromAssignment(self.region, zero_map, submaps_tv)

        for c in tvws_channel_list:
            for i in range(400):
                for j in range(600):
                    self.assertEqual(test_map_3D.get_layer(c).get_value_by_index(i, j), reqd_map_3D.get_layer(c).get_value_by_index(i, j))


        #Test for multiple stations with non-overlapping locations
        def filter_function_2(station):
            return station.get_channel() == 4 or station.get_facility_id() == '1005'


        tv_stations = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)
        tv_stations.prune_data(self.good_facility_ids)

        tv_stations.remove_entities(filter_function_2)

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)

        test_map_3D = createTVViewershipFromAssignment(self.region, zero_map, submaps_tv)

        for i in range(400):
            for j in range(600):
                self.assertEqual(test_map_3D.get_layer(17).get_value_by_index(i, j), reqd_map_3D.get_layer(17).get_value_by_index(i, j))
                if test_map_3D.get_layer(4).get_value_by_index(i, j) not in [0, 1]:
                    print test_map_3D.get_layer(4).get_value_by_index(i, j)
                    raise ValueError("There are no overlaps and we should only have values 0 or 1")


    def test_create_whitespace_from_assignment(self):

        submaps_ws_fixed = {'cochannel': load_submaps(11), 'adjchannel': load_submaps(1)}
        submaps_ws_portable = {'cochannel': load_submaps(4)}

        #Test for empty region
        tv_stations = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)
        tv_stations._entities = []
        tv_stations._refresh_cached_data()
        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)
        test_map_3D = createWhitespaceFromAssignment(self.region, self.region_map, submaps_ws_fixed)


        for c in self.tvws_channel_list:
            for i in range(400):
                for j in range(600):
                    self.assertEqual(test_map_3D.get_layer(c).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))


        #Test for single station with circular submap
        def filter_function_1(station):
            return station.get_facility_id() == '1005'
        tv_stations = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)
        tv_stations.remove_entities(filter_function_1)
        tv_stations._refresh_cached_data()

        max_protected_radius_km = self.ruleset.get_tv_protected_radius_km(tv_stations.stations()[0], tv_stations.stations()[0].get_location())

        def not_inside_circular_contour(latitude, longitude, latitude_index, longitude_index, current_value):
            if current_value == 0:
                return 0
            return not vincenty((latitude, longitude), tv_stations.stations()[0].get_location()) <= max_protected_radius_km + 11

        def not_inside_circular_contour_11(latitude, longitude, latitude_index, longitude_index, current_value):
            if current_value == 0:
                return 0
            return not vincenty((latitude, longitude), tv_stations.stations()[0].get_location()) <= max_protected_radius_km + 11

        def not_inside_circular_contour_4(latitude, longitude, latitude_index, longitude_index, current_value):
            if current_value == 0:
                return 0
            return not vincenty((latitude, longitude), tv_stations.stations()[0].get_location()) <= max_protected_radius_km + 4

        def not_inside_circular_contour_1(latitude, longitude, latitude_index, longitude_index, current_value):
            if current_value == 0:
                return 0
            return not vincenty((latitude, longitude), tv_stations.stations()[0].get_location()) <= max_protected_radius_km + 1



        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)

        reqd_map_3D = west.data_map.DataMap3D.from_DataMap2D(self.region_map, self.tvws_channel_list)

        reqd_map_3D.get_layer(17).update_all_values_via_function(not_inside_circular_contour_11)
        reqd_map_3D.get_layer(16).update_all_values_via_function(not_inside_circular_contour_1)
        reqd_map_3D.get_layer(18).update_all_values_via_function(not_inside_circular_contour_1)

        #reqd_map_3D.get_layer(17).update_all_values_via_function(not_inside_circular_contour_4)

        test_map_3D = createWhitespaceFromAssignment(DeviceSpecification.fixed, self.region,
                                                     self.region_map, submaps_ws_fixed)

        for c in self.tvws_channel_list:
            for i in range(400):
                for j in range(600):
                    self.assertEqual(test_map_3D.get_layer(c).get_value_by_index(i, j), reqd_map_3D.get_layer(c).get_value_by_index(i, j))

        #Adding one station outside boundary
        tv_station_outside_boundary_lat = 17
        tv_station_outside_boundary_lon = -64
        tv_station_outside_boundary = ProtectedEntityTVStation(tv_stations, self.region, tv_station_outside_boundary_lat, tv_station_outside_boundary_lon, 23,
                                                               659, 124.2, 'DT')
        tv_station_outside_boundary.add_facility_id('test_station_outside_us')
        submap_outside_boundary = west.data_map.DataMap2D.from_specification((15, 19), (-66, 60), 50, 50)
        submap_outside_boundary.reset_all_values(0)
        submaps_ws_fixed['test_station_outside_us'] = {'cochannel': ['fcc', submap_outside_boundary], 'adjchannel': ['fcc', submap_outside_boundary]}

        tv_stations._add_entity(tv_station_outside_boundary)
        tv_stations._refresh_cached_data()

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)

        test_map_3D = createWhitespaceFromAssignment(DeviceSpecification.fixed, self.region,
                                                       self.region_map, submaps_ws_fixed)

        for c in self.tvws_channel_list:
            for i in range(400):
                for j in range(600):
                    self.assertEqual(test_map_3D.get_layer(c).get_value_by_index(i, j), reqd_map_3D.get_layer(c).get_value_by_index(i, j))


        #Test for stations with no overlap
        tv_stations = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)
        def filter_function_ch_3(station):
            return station.get_channel() == 3

        tv_stations.remove_entities(filter_function_ch_3)

        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)


        original_map_3D = createWhitespaceFromAssignment(DeviceSpecification.fixed, self.region,
                                                         self.region_map, submaps_ws_fixed)

        tv_stations.modify_channels_at_random()
        self.region.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, tv_stations)


        test_map_3D = createWhitespaceFromAssignment(DeviceSpecification.fixed, self.region,
                                                     self.region_map, submaps_ws_fixed)

        original_map = original_map_3D.sum_all_layers()
        test_map = test_map_3D.sum_all_layers()

        for i in range(400):
            for j in range(600):
                #print i, j
                self.assertEqual(original_map.get_value_by_index(i, j), test_map.get_value_by_index(i, j))"""



class testHigherLevelFunctions(unittest.TestCase):

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

        self.good_facility_ids = []
        with open(os.path.join("data", "FromVijay", "C-All free", "C-0channelsRemoved", "0VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                self.good_facility_ids.append(row[0])


        self.submaps_tv = load_submaps(0)
        self.submaps_ws_fixed = {'cochannel': load_submaps(11), 'adjchannel': load_submaps(1)}
        self.submaps_ws_portable = {'cochannel': load_submaps(4)}


    def test_cleared_layers_repack_bandplan(self):
        test_assignment = Assignment(AssignmentType.repack, QuantityToPlot.tv,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, self.submaps_tv,
                                     8, repack = Repack(RepackType.C, 0))

        test_assignment.set_region(self.good_facility_ids, self.tv_channel_list)
        test_tvmap_3D = test_assignment.make_data()

        for c in range(52 - 8, 52):
            for i in range(400):
                for j in range(600):
                    self.assertEqual(test_tvmap_3D.get_layer(c).get_value_by_index(i, j), 0)

        test_assignment = Assignment(AssignmentType.repack, QuantityToPlot.whitespace,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                     8, repack = Repack(RepackType.C, 0), device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                     whitespace_evaluation_type = WhitespaceEvaluationType.total)

        test_assignment.set_region(self.good_facility_ids, self.tv_channel_list)
        test_wsmap_3D = test_assignment.make_data()

        for c in range(52 - 8, 52):
            for i in range(400):
                for j in range(600):
                    self.assertEqual(test_wsmap_3D.get_layer(c).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))


        test_assignment = Assignment(AssignmentType.repack, QuantityToPlot.whitespace,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                     8, repack = Repack(RepackType.C, 0), device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                     whitespace_evaluation_type = WhitespaceEvaluationType.total)

        test_assignment.set_region(self.good_facility_ids, self.tv_channel_list)
        test_wsmap_3D = test_assignment.make_data()

        for c in range(52 - 7, 52):
            for i in range(400):
                for j in range(600):
                    self.assertEqual(test_wsmap_3D.get_layer(c).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))


    def test_all_layers_chop_off_top(self):

        original_assignment = Assignment(AssignmentType.original, QuantityToPlot.tv,
                                         self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                         self.tv_channel_list, self.submaps_tv,
                                         0)

        original_assignment.set_region(self.good_facility_ids, self.tv_channel_list)
        original_tvmap_3D = original_assignment.make_data()

        test_assignment = Assignment(AssignmentType.chopofftop, QuantityToPlot.tv,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, self.submaps_tv,
                                     8)

        test_assignment.set_region(self.good_facility_ids, self.tv_channel_list)
        test_tvmap_3D = test_assignment.make_data()

        for c in self.tv_channel_list:
            if c < 52 - 8:
                for i in range(400):
                    for j in range(600):
                        self.assertEqual(test_tvmap_3D.get_layer(c).get_value_by_index(i, j), original_tvmap_3D.get_layer(c).get_value_by_index(i, j))
            else:
                for i in range(400):
                    for j in range(600):
                        self.assertEqual(test_tvmap_3D.get_layer(c).get_value_by_index(i, j), 0)


        original_assignment = Assignment(AssignmentType.original, QuantityToPlot.whitespace,
                                         self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                         self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                         0, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                         whitespace_evaluation_type = WhitespaceEvaluationType.total)

        original_assignment.set_region(self.good_facility_ids, self.tv_channel_list)
        original_tvmap_3D = original_assignment.make_data()

        test_assignment = Assignment(AssignmentType.chopofftop, QuantityToPlot.whitespace,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                     8, device = Device(1, 30, 1), device_specification = DeviceSpecification.portable, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                     whitespace_evaluation_type = WhitespaceEvaluationType.total)

        test_assignment.set_region(self.good_facility_ids, self.tv_channel_list)
        test_tvmap_3D = test_assignment.make_data()

        for c in self.tv_channel_list:
            if c < 52 - 8:
                for i in range(400):
                    for j in range(600):
                        self.assertEqual(test_tvmap_3D.get_layer(c).get_value_by_index(i, j), original_tvmap_3D.get_layer(c).get_value_by_index(i, j))
            else:
                for i in range(400):
                    for j in range(600):
                        self.assertEqual(test_tvmap_3D.get_layer(c).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))


        original_assignment = Assignment(AssignmentType.original, QuantityToPlot.whitespace,
                                         self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                         self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                         0, device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                         whitespace_evaluation_type = WhitespaceEvaluationType.total)

        original_assignment.set_region(self.good_facility_ids, self.tv_channel_list)
        original_tvmap_3D = original_assignment.make_data()

        test_assignment = Assignment(AssignmentType.chopofftop, QuantityToPlot.whitespace,
                                     self.region, self.region_map_spec, self.plmrs_exclusions_map, self.ruleset,
                                     self.tv_channel_list, {'fixed': self.submaps_ws_fixed, 'portable': self.submaps_ws_portable},
                                     8, device = Device(0, 30, 1), device_specification = DeviceSpecification.fixed, plmrs_indicator = PLMRSExclusions.plmrs_applied,
                                     whitespace_evaluation_type = WhitespaceEvaluationType.total)

        test_assignment.set_region(self.good_facility_ids, self.tv_channel_list)
        test_tvmap_3D = test_assignment.make_data()

        for c in self.tv_channel_list:
            print c
            if c < 52 - 9:
                for i in range(400):
                    for j in range(600):
                        self.assertEqual(test_tvmap_3D.get_layer(c).get_value_by_index(i, j), original_tvmap_3D.get_layer(c).get_value_by_index(i, j))
            elif c > 52 - 8:
                for i in range(400):
                    for j in range(600):
                        self.assertEqual(test_tvmap_3D.get_layer(c).get_value_by_index(i, j), self.region_map.get_value_by_index(i, j))


















































unittest.main()














