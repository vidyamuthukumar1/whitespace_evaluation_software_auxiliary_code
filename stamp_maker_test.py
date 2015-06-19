from west.boundary import BoundaryContinentalUnitedStatesWithStateBoundaries, BoundaryContinentalUnitedStates
from west.region_united_states import RegionUnitedStates
from protected_entities_tv_stations_vidya import ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack
from west.protected_entities_tv_stations import ProtectedEntitiesTVStations
import protected_entities_tv_stations_vidya
from west.protected_entity_tv_station import ProtectedEntityTVStation
import west.helpers

from data_aggregation import plot_map_from_datamap2D

import stamp_maker
import unittest
import pickle
import shapely.geometry
from geopy.distance import vincenty
import numpy
import os

boundary = BoundaryContinentalUnitedStatesWithStateBoundaries()

with open("stamps_with_buffer=0km.pkl", "r") as f:
    submaps = pickle.load(f)

with open("stamps_with_buffer=0km_with_dd.pkl", "r") as f:
    submaps_withdd = pickle.load(f)

with open("circular_stamps_with_buffer=0km.pkl", 'r') as f:
    circular_submaps = pickle.load(f)

for s in submaps.values():
    s[1].update_all_values_via_function(stamp_maker.not_function)

for s in submaps_withdd.values():
    s[1].update_all_values_via_function(stamp_maker.not_function)

for s in circular_submaps.values():
    s.update_all_values_via_function(stamp_maker.not_function)
    s.mutable_matrix = 2 * s.mutable_matrix



class UnitSubmapGenerationTestCase(unittest.TestCase):
    def setUp(self):
        self.region = stamp_maker.region
        self.region_map = stamp_maker.region_map
        self.ruleset = stamp_maker.ruleset
        self.min_lat_us = self.region_map.latitudes[0]
        self.max_lat_us = self.region_map.latitudes[-1]
        self.min_lon_us = self.region_map.longitudes[0]
        self.max_lon_us = self.region_map.longitudes[-1]
        self.pixels_per_latitude = 400/(self.max_lat_us - self.min_lat_us)
        self.pixels_per_longitude = 600/(self.max_lon_us - self.min_lon_us)

        self.buffer_maker = stamp_maker.bm


    def test_helper_submap_generation(self):

        def inside_us_function(latitude, longitude, latitude_index, longitude_index, current_value):
            return self.region.location_is_in_region((latitude, longitude))


        test_tv_stations = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_PruneData(self.region)

        #Test for station whose bounding box is entirely within the US
        tv_station_lat = (self.min_lat_us + self.max_lat_us)/2
        tv_station_lon = (self.min_lon_us + self.max_lon_us)/2
        tv_station = ProtectedEntityTVStation(test_tv_stations, self.region, tv_station_lat, tv_station_lon, 20,
                                                                                 230*1000, 45, 'DT')
        test_tv_stations._add_entity(tv_station)
        bounding_box = tv_station.get_bounding_box()
        min_lat_index = west.helpers.find_last_value_below_or_equal(self.region_map.latitudes, bounding_box['min_lat'])
        max_lat_index = west.helpers.find_first_value_above_or_equal(self.region_map.latitudes, bounding_box['max_lat'])
        min_lon_index = west.helpers.find_last_value_below_or_equal(self.region_map.longitudes, bounding_box['min_lon'])
        max_lon_index = west.helpers.find_first_value_above_or_equal(self.region_map.longitudes, bounding_box['max_lon'])
        reqd_submap = west.data_map.DataMap2D.from_specification((self.region_map.latitudes[min_lat_index], self.region_map.latitudes[max_lat_index]), (self.region_map.longitudes[min_lon_index], self.region_map.longitudes[max_lon_index]),
                                                                 max_lat_index - min_lat_index + 1, max_lon_index - min_lon_index + 1)
        reqd_submap.reset_all_values(1)
        test_submap = west.helpers.generate_submap_for_protected_entity(self.region_map, tv_station)

        self.assertAlmostEqual(len(test_submap.latitudes), len(reqd_submap.latitudes))
        self.assertAlmostEqual(len(test_submap.longitudes), len(reqd_submap.longitudes))

        for i in range(len(test_submap.latitudes)):
            self.assertAlmostEqual(test_submap.latitudes[i], reqd_submap.latitudes[i])

        for i in range(len(test_submap.longitudes)):
            self.assertAlmostEqual(test_submap.longitudes[i], reqd_submap.longitudes[i])

        for i in range(max_lat_index - min_lat_index + 1):
            for j in range(max_lon_index - min_lon_index + 1):
                self.assertAlmostEqual(test_submap.get_value_by_index(i, j), reqd_submap.get_value_by_index(i, j))

        #Test for station whose bounding box is partly within the US
        tv_station_lat = 39
        tv_station_lon = -123
        tv_station = ProtectedEntityTVStation(test_tv_stations, self.region, tv_station_lat, tv_station_lon, 8,
                                                                                 26*1000, 744, 'DT')
        test_tv_stations._add_entity(tv_station)
        bounding_box = tv_station.get_bounding_box()
        min_lat_index = west.helpers.find_last_value_below_or_equal(self.region_map.latitudes, bounding_box['min_lat'])
        max_lat_index = west.helpers.find_first_value_above_or_equal(self.region_map.latitudes, bounding_box['max_lat'])
        min_lon_index = 0
        max_lon_index = west.helpers.find_first_value_above_or_equal(self.region_map.longitudes, bounding_box['max_lon'])
        reqd_submap = west.data_map.DataMap2D.from_specification((self.region_map.latitudes[min_lat_index], self.region_map.latitudes[max_lat_index]), (self.region_map.longitudes[min_lon_index], self.region_map.longitudes[max_lon_index]),
                                                                 max_lat_index - min_lat_index + 1, max_lon_index - min_lon_index + 1)
        reqd_submap.update_all_values_via_function(inside_us_function)

        test_submap = west.helpers.generate_submap_for_protected_entity(self.region_map, tv_station)

        self.assertAlmostEqual(len(test_submap.latitudes), len(reqd_submap.latitudes))
        self.assertAlmostEqual(len(test_submap.longitudes), len(reqd_submap.longitudes))

        for i in range(len(test_submap.latitudes)):
            self.assertAlmostEqual(test_submap.latitudes[i], reqd_submap.latitudes[i])

        for i in range(len(test_submap.longitudes)):
            self.assertAlmostEqual(test_submap.longitudes[i], reqd_submap.longitudes[i])

        for i in range(max_lat_index - min_lat_index + 1):
            for j in range(max_lon_index - min_lon_index + 1):
                self.assertAlmostEqual(test_submap.get_value_by_index(i, j), reqd_submap.get_value_by_index(i, j))


        for i in range(max_lat_index - min_lat_index + 1):
            for j in range(max_lon_index - min_lon_index + 1):
                self.assertAlmostEqual(test_submap.get_value_by_index(i, j), reqd_submap.get_value_by_index(i, j))


        #Test for station whose bounding box is outside the US
        tv_station_lat = 17
        tv_station_lon = -64
        tv_station = ProtectedEntityTVStation(test_tv_stations, self.region, tv_station_lat, tv_station_lon, 23,
                                              659, 124.2, 'DT')
        test_tv_stations._add_entity(tv_station)
        bounding_box = tv_station.get_bounding_box()

        self.assertRaises(ValueError, west.helpers.generate_submap_for_protected_entity, self.region_map, tv_station)




    def test_fcc_stamp_creation(self):
        #Tests for stamps created using FCC contours

        def inside_us_function(latitude, longitude, latitude_index, longitude_index, current_value):
            return self.region.location_is_in_region((latitude, longitude))

        #Control submap
        submap_lat = (self.min_lat_us + self.max_lat_us)/2
        submap_lon = (self.min_lon_us + self.max_lon_us)/2
        tv_station = ProtectedEntityTVStation(protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_PruneData(self.region), self.region, submap_lat, submap_lon, 20,
                                                                                 230*1000, 45, 'DT')

        bounding_box = tv_station.get_bounding_box()
        min_lat_index = west.helpers.find_last_value_below_or_equal(self.region_map.latitudes, bounding_box['min_lat'])
        max_lat_index = west.helpers.find_first_value_above_or_equal(self.region_map.latitudes, bounding_box['max_lat'])
        min_lon_index = west.helpers.find_last_value_below_or_equal(self.region_map.longitudes, bounding_box['min_lon'])
        max_lon_index = west.helpers.find_first_value_above_or_equal(self.region_map.longitudes, bounding_box['max_lon'])
        submap = west.data_map.DataMap2D.from_specification((self.region_map.latitudes[min_lat_index], self.region_map.latitudes[max_lat_index]), (self.region_map.longitudes[min_lon_index], self.region_map.longitudes[max_lon_index]),
                                                                 max_lat_index - min_lat_index + 1, max_lon_index - min_lon_index + 1)
        submap.update_all_values_via_function(inside_us_function)
        submap_control = west.data_map.DataMap2D.get_copy_of(submap)
        submap_control.reset_all_values(1)
        #This is temporarily done to make sure we have a nice control submap with all points inside continental US
        for i in range(max_lat_index - min_lat_index + 1):
            for j in range(max_lon_index - min_lon_index + 1):
                self.assertEqual(submap.get_value_by_index(i, j), submap_control.get_value_by_index(i, j))

        #Test for rectangular contour
        min_lon = submap_lon - 10/self.pixels_per_longitude
        max_lon = submap_lon + 10/self.pixels_per_longitude
        min_lat = submap_lat - 10/self.pixels_per_latitude
        max_lat = submap_lat + 10/self.pixels_per_latitude
        polygon_rect = shapely.geometry.geo.box(min_lon, min_lat, max_lon, max_lat)
        def not_inside_polygon_rect(latitude, longitude, latitude_index, longitude_index, current_value):
            if latitude < min_lat or latitude > max_lat:
                return 1
            if longitude < min_lon or longitude > max_lon:
                return 1
            return 0

        submap.update_all_values_via_function(not_inside_polygon_rect)
        test_submap = stamp_maker.make_fcc_stamp(list(polygon_rect.exterior.coords), stamp_maker.bm, submap_control, 0)
        for i in range(max_lat_index - min_lat_index + 1):
            for j in range(max_lon_index - min_lon_index + 1):
                self.assertEqual(submap.get_value_by_index(i, j), test_submap.get_value_by_index(i, j))


        #Test for polygon not entirely present inside submap.
        polygon_partially_outside = shapely.geometry.geo.box(self.region_map.longitudes[min_lon_index] - 5/self.pixels_per_longitude, self.region_map.latitudes[min_lat_index] - 1/self.pixels_per_latitude, self.region_map.longitudes[min_lon_index], self.region_map.latitudes[min_lat_index] + 1/self.pixels_per_latitude)
        submap_control.reset_all_values(1)
        self.assertRaises(ValueError, stamp_maker.make_fcc_stamp, list(polygon_partially_outside.exterior.coords), stamp_maker.bm, submap_control, 0)

        #Test for 1x1 polygon
        lon_index = (max_lon_index - min_lon_index)/2
        lat_index = (max_lat_index - min_lat_index)/2
        min_lon = submap_control.longitudes[lon_index] + (submap_control.longitudes[lon_index + 1] - submap_control.longitudes[lon_index])/4
        max_lon = submap_control.longitudes[lon_index] + 3 * (submap_control.longitudes[lon_index + 1] - submap_control.longitudes[lon_index])/4
        min_lat = submap_control.latitudes[lat_index] + (submap_control.latitudes[lat_index + 1] - submap_control.latitudes[lat_index])/4
        max_lat = submap_control.latitudes[lat_index] + 3 * (submap_control.latitudes[lat_index + 1] - submap_control.latitudes[lat_index])/4
        tiny_polygon = shapely.geometry.geo.box(min_lon, min_lat, max_lon, max_lat)
        #tiny_polygon = shapely.geometry.geo.box((submap_control.longitudes[lon_index] + submap_control.longitudes[lon_index - 1])/2, (submap_control.latitudes[lat_index - 1] + submap_control.latitudes[lat_index])/2,
                                                #(submap_control.longitudes[lon_index] + submap_control.longitudes[lon_index + 1])/2, (submap_control.latitudes[lat_index] + submap_control.latitudes[lat_index + 1])/2)

        def not_inside_tiny_polygon(latitude, longitude, latitude_index, longitude_index, current_value):
            return not (longitude == submap_control.longitudes[lon_index] and latitude == submap_control.latitudes[lat_index])

        submap_control.reset_all_values(1)
        #submap.update_all_values_via_function(not_inside_tiny_polygon)
        submap.reset_all_values(1)
        test_submap = stamp_maker.make_fcc_stamp(list(tiny_polygon.exterior.coords), stamp_maker.bm, submap_control, 0)
        for i in range(max_lat_index - min_lat_index + 1):
            for j in range(max_lon_index - min_lon_index + 1):
                self.assertEqual(submap.get_value_by_index(i, j), test_submap.get_value_by_index(i, j))




    def test_circular_stamp_creation(self):
        """Tests for submaps created using circular contours"""
        def inside_us_function(latitude, longitude, latitude_index, longitude_index, current_value):
            return self.region.location_is_in_region((latitude, longitude))

        #Control submap
        submap_lat = (self.min_lat_us + self.max_lat_us)/2
        submap_lon = (self.min_lon_us + self.max_lon_us)/2
        tv_station = ProtectedEntityTVStation(protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_PruneData(self.region), self.region, submap_lat, submap_lon, 20,
                                                                                 0, 45, 'DT')

        bounding_box = tv_station.get_bounding_box()
        min_lat_index = west.helpers.find_last_value_below_or_equal(self.region_map.latitudes, bounding_box['min_lat'])
        max_lat_index = west.helpers.find_first_value_above_or_equal(self.region_map.latitudes, bounding_box['max_lat'])
        min_lon_index = west.helpers.find_last_value_below_or_equal(self.region_map.longitudes, bounding_box['min_lon'])
        max_lon_index = west.helpers.find_first_value_above_or_equal(self.region_map.longitudes, bounding_box['max_lon'])
        submap = west.data_map.DataMap2D.from_specification((self.region_map.latitudes[min_lat_index], self.region_map.latitudes[max_lat_index]), (self.region_map.longitudes[min_lon_index], self.region_map.longitudes[max_lon_index]),
                                                            max_lat_index - min_lat_index + 1, max_lon_index - min_lon_index + 1)
        submap.update_all_values_via_function(inside_us_function)
        submap_control = west.data_map.DataMap2D.get_copy_of(submap)
        submap_control.reset_all_values(1)
        #This is temporarily done to make sure we have a nice control submap with all points inside continental US
        for i in range(max_lat_index - min_lat_index + 1):
            for j in range(max_lon_index - min_lon_index + 1):
                self.assertEqual(submap.get_value_by_index(i, j), submap_control.get_value_by_index(i, j))
        #Test for station with ERP = 0.
        self.assertRaisesRegexp(ValueError, "TV station's ERP cannot be zero. Please check input.", stamp_maker.make_circular_stamp, tv_station, tv_station.get_location(), self.region, self.ruleset, submap_control, 0)

        #Test for station with large ERP such that protection radius > bounding box size: No easy way to test this right now as protected radius is not independent of direction :(
        tv_station._ERP_Watts = 1000000000
        max_protected_radius = self.ruleset.get_tv_protected_radius_km(tv_station, tv_station.get_location())
        dist1 = vincenty(tv_station.get_location(), (tv_station.get_location()[0], min(submap_control.longitudes)))
        dist2 = vincenty(tv_station.get_location(), (tv_station.get_location()[0], max(submap_control.longitudes)))
        dist3 = vincenty(tv_station.get_location(), (min(submap_control.latitudes), tv_station.get_location()[1]))
        dist4 = vincenty(tv_station.get_location(), (max(submap_control.latitudes), tv_station.get_location()[1]))


        self.assertRaisesRegexp(ValueError, "Part of contour is outside the bounding box. Please check correctness of data for this protected entity.", stamp_maker.make_circular_stamp,
                                tv_station, tv_station.get_location(), self.region, self.ruleset, submap_control, 0)

        #Test for station with regular circular contour + buffer
        tv_station._ERP_Watts = 230 * 1000
        buffer_dist = 4
        max_protected_radius = self.ruleset.get_tv_protected_radius_km(tv_station, tv_station.get_location()) + buffer_dist
        initial_circular_polygon_coords = [(tv_station.get_location()[1], tv_station.get_location()[0]), (tv_station.get_location()[1], tv_station.get_location()[0]),
            (tv_station.get_location()[1], tv_station.get_location()[0]), (tv_station.get_location()[1], tv_station.get_location()[0])]
        circular_polygon_coords = self.buffer_maker.add_buffer(initial_circular_polygon_coords, max_protected_radius)
        circular_polygon = shapely.geometry.polygon.Polygon(shell = circular_polygon_coords)

        def outside_circular_polygon(latitude, longitude, latitude_index, longitude_index, current_value):
            point = shapely.geometry.Point((longitude, latitude))
            return not point.within(circular_polygon)

        submap.update_all_values_via_function(outside_circular_polygon)
        submap_control.reset_all_values(1)
        test_submap = stamp_maker.make_circular_stamp(tv_station, tv_station.get_location(), self.region, self.ruleset, submap_control, buffer_dist)

        for i in range(max_lat_index - min_lat_index + 1):
            for j in range(max_lon_index - min_lon_index + 1):
                self.assertEqual(submap.get_value_by_index(i, j), test_submap.get_value_by_index(i, j))



#unittest.main()



"""Tests on submaps we are using: Only need to check if we have any all-ones or all-zeros."""

"""def is_stamp_all_ones(datamap):
    datamap_ones = west.data_map.DataMap2D.get_copy_of(datamap)
    datamap_ones.reset_all_values(1)
    return numpy.array_equal(datamap.mutable_matrix, datamap_ones.mutable_matrix)

def is_stamp_all_zeros(datamap):
    datamap_zeros = west.data_map.DataMap2D.get_copy_of(datamap)
    datamap_zeros.reset_all_values(0)
    return numpy.array_equal(datamap.mutable_matrix, datamap_zeros.mutable_matrix)

print "LENGTH OF SUBMAPS DICTIONARY", len(submaps.keys())
for fid in submaps.keys():
    if is_stamp_all_ones(submaps[fid][1]):
        print fid, submaps[fid][0]
        print "Submap has only 1's, i.e. contour is infinitesmally small or does not exist"
    if is_stamp_all_zeros(submaps[fid][1]):
        print "Submap has only 0's, i.e. contour is bigger than submap bounds"
        """







data_map = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(stamp_maker.region_map)
data_map.reset_all_values(0)

def set_zero_to_inf(latitude, longitude, latitude_index, longitude_index, current_value):
    if current_value == 0:
        return numpy.inf
    return current_value

for f in submaps.keys():
    if submaps[f][0] == 'circular':
        print 'Hello'
        data_map.reintegrate_submap(submaps[f][1], lambda x, y: x + y)

data_map.update_all_values_via_function(set_zero_to_inf)

map = plot_map_from_datamap2D(data_map, stamp_maker.region_map, use_colorbar = True, colorbar_ticks = [0, 1, 2], colorbar_label = "Channels Affected", cmin = 0, cmax = 2)
map.blocking_show()

datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
region_map_spec = west.data_management.SpecificationRegionMap(BoundaryContinentalUnitedStates, datamap_spec)
region_map = region_map_spec.fetch_data()
population_map_spec = west.data_management.SpecificationPopulationMap(region_map_spec, west.population.PopulationData)
population_map = population_map_spec.fetch_data()
population = 0

for i in range(400):
    for j in range(600):
        if data_map.get_value_by_index(i, j) != numpy.inf:
            population += population_map.get_value_by_index(i, j)

print "Population = ", population

tv_stations = ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(stamp_maker.region)
zero_map = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)
zero_map.reset_all_values(0)

zero_map_2 = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(zero_map)

def make_zero_minusone(latitude, longitude, latitude_index, longitude_index, current_value):
    if current_value == 0:
        return -1
    return current_value

def make_zero_inf(latitude, longitude, latitude_index, longitude_index, current_value):
    if current_value == 0:
        return numpy.inf
    return current_value

"""for s in tv_stations.stations():
    if s.get_facility_id() in circular_submaps.keys():
        if submaps[s.get_facility_id()][0] == 'fcc':
            #zero_map.reset_all_values(0)
            data_map = west.helpers.generate_submap_for_protected_entity(stamp_maker.region_map, s)
            data_map.reset_all_values(0)
            data_map.reintegrate_submap(submaps[s.get_facility_id()][1], lambda x, y: x + y)
            data_map.reintegrate_submap(circular_submaps[s.get_facility_id()], lambda x, y: x + y)
            data_map.update_all_values_via_function(make_zero_minusone)
            map = plot_map_from_datamap2D(data_map, boundary = None, set_below_zero_color = '0.90', use_colorbar = False, cmin = 0, cmax = 3)
            #map.blocking_show()
            map.save(os.path.join("data", "FCC data exploration", "Circular vs FCC contours maps", "%s.png"%s.get_facility_id()))"""

list_of_facility_ids_of_type_dd = ['63865', '34440', '62442', '62430', '62427',
                                   '166319', '69300', '65919', '43952', '41237',
                                   '66219', '55305', '66378', '60111']
"""facility_ids_saved = {}
for f in list_of_facility_ids_of_type_dd:
    facility_ids_saved[f] = False

for s in tv_stations.stations():
    if s.get_facility_id() in list_of_facility_ids_of_type_dd and not facility_ids_saved[s.get_facility_id()]:
        print s.get_facility_id()
        data_map = west.helpers.generate_submap_for_protected_entity(stamp_maker.region_map, s)
        data_map.reset_all_values(0)
        data_map.reintegrate_submap(submaps[s.get_facility_id()][1], lambda x, y: x + y)
        map = plot_map_from_datamap2D(data_map, boundary = None, set_below_zero_color = '0.90', use_colorbar = False, cmin = 0, cmax = 1)
        map.save(os.path.join("data", "FCC data exploration", "DD contours", "%s_old.png"%s.get_facility_id()))
        data_map.reset_all_values(0)
        data_map.reintegrate_submap(submaps_withdd[s.get_facility_id()][1], lambda x, y: x + y)
        map = plot_map_from_datamap2D(data_map, boundary = None, set_below_zero_color = '0.90', use_colorbar = False, cmin = 0, cmax = 1)
        map.save(os.path.join("data", "FCC data exploration", "DD contours", "%s_new.png"%s.get_facility_id()))
        facility_ids_saved[s.get_facility_id()] = True"""

def subtraction_function(this_value, other_value):
    return this_value - other_value

for f in submaps_withdd.keys():
    if f in list_of_facility_ids_of_type_dd:
        zero_map.reintegrate_submap(submaps_withdd[f][1], lambda x, y: x + y)
        zero_map_2.reintegrate_submap(submaps[f][1], lambda x, y: x + y)

diff_map = zero_map.combine_datamaps_with_function(zero_map_2, subtraction_function)

sumdiff = 0
for i in range(400):
    for j in range(600):
        sumdiff += diff_map.get_value_by_index(i, j)


diff_map.update_all_values_via_function(make_zero_inf)
map = plot_map_from_datamap2D(diff_map, use_colorbar = False, cmin = 0, cmax = 1)
map.blocking_show()












