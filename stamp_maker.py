import pickle
from buffer_maker import BufferMaker
from fcc_polygons import FccPolygons
from west.region_united_states import RegionUnitedStates
from west.data_management import SpecificationDataMap, SpecificationRegionMap
from west.ruleset_fcc2012 import RulesetFcc2012
"""Need to import data_map and boundary"""
import west.data_map
import west.boundary
from west.boundary import BoundaryContinentalUnitedStates, BoundaryContinentalUnitedStatesWithStateBoundaries
from west.data_map import DataMap2DContinentalUnitedStates
from west.helpers import generate_submap_for_protected_entity
from west.protected_entities_tv_stations import \
    ProtectedEntitiesTVStations
from protected_entities_tv_stations_vidya import ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from geopy.distance import vincenty
"""Need to import os as data_management is not imported anymore"""
import os
import csv
import west.configuration
from west.custom_logging import getModuleLogger
import simplekml

facility_ids_with_haat_zero = {'167799': 179, '168662': 473, '168800': 61, '18736': 124, '191262': 114, '191793': 210, '191822': 115, '24574': 327,
                               '29464': 461, '30129': 197 , '33819': 548, '349': 69, '35101': 356, '40058': 155, '48013': 128, '5010': 287, '57905': 50,
                               '58739': 39, '66172': 86, '66978': 445, '70419': 264, '74214': 146}

#All negative values + '349', '58739' have changed


def not_function(latitude, longitude, latitude_index, longitude_index, current_value):
    return 1 - current_value

def closest_lat(latitude, region_map):
    abs = 0
    for i in range(len(region_map.latitudes)):
        if latitude < region_map.latitudes[i]:
            abs1 = latitude - region_map.latitudes[i - 1]
            abs2 = region_map.latitudes[i] - latitude
            if abs1 < abs2:
                return region_map.latitudes[i - 1]
            else:
                return region_map.latitudes[i]
    return None

def closest_lon(longitude, region_map):
    abs = 0
    for i in range(len(region_map.longitudes)):
        if longitude < region_map.longitudes[i]:
            abs1 = longitude - region_map.longitudes[i - 1]
            abs2 = region_map.longitudes[i] - longitude
            if abs1 < abs2:
                return region_map.longitudes[i - 1]
            else:
                return region_map.longitudes[i]
    return None




good_facility_ids = []
with open(os.path.join("data", "FromVijay", "15VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if row == []:
            break
        good_facility_ids.append(row[0])


def make_fcc_stamp(fcc_poly_coords, bm, submap,
               buffer_distance):
    """Function to make stamps from FCC contours. This function can in fact be used for any polygon."""

    buffer_coords = bm.add_buffer(fcc_poly_coords,
                                  buffer_distance)
    buffer_polygon = Polygon(shell=buffer_coords)

    for point in buffer_coords:
        point_lat = closest_lat(point[1], region_map)
        point_lon = closest_lon(point[0], region_map)
        if (point_lon < submap.longitudes[0] or point_lon > submap.longitudes[-1] or point_lat < submap.latitudes[0] or point_lat > submap.latitudes[-1]) and boundary.location_inside_boundary((point[1], point[0])):
            print point, submap.longitudes[0], submap.longitudes[-1], submap.latitudes[0], submap.latitudes[-1]
            raise ValueError("Part of contour is outside the bounding box. Please check correctness of data for this protected entity.")

    def is_whitespace(latitude, longitude, latitude_index, longitude_index, current_value):
        point = Point( (longitude, latitude) )
        return not point.within(buffer_polygon)


    submap.update_all_values_via_function(update_function=is_whitespace)
    return submap

def make_circular_stamp(station, station_location, region, ruleset, submap, buffer_size_km):

    if station.get_erp_watts() == 0:
        raise ValueError("TV station's ERP cannot be zero. Please check input.")

    max_protected_radius = ruleset.get_tv_protected_radius_km(station, station_location) + buffer_size_km
    distance_east = vincenty(station_location, (station_location[0], station_location[1] + 2))
    distance_west = vincenty(station_location, (station_location[0], station_location[1] - 2))
    distance_north = vincenty(station_location, (station_location[0] + 2, station_location[1]))
    distance_south = vincenty(station_location, (station_location[0] - 2, station_location[1]))
    if max_protected_radius > min([distance_east, distance_west, distance_north, distance_south]):
        raise ValueError("Part of contour is outside the bounding box. Please check correctness of data for this protected entity.")

    def point_not_within_circular_contour(latitude, longitude, latitude_index, longitude_index, current_value):
        if current_value == 0:
            return 0
        current_location = (latitude, longitude)

        return not vincenty(station_location, current_location) <= max_protected_radius

    #Making the circular contour with buffer
    submap.update_all_values_via_function(point_not_within_circular_contour)

    return submap


# Buffer Maker
bm = BufferMaker()

# Region and TV stations
region = RegionUnitedStates()
boundary = BoundaryContinentalUnitedStatesWithStateBoundaries()
tv_stations = ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(region)
#tv_stations.prune_data(good_facility_ids)
print (len(tv_stations.stations()))
region.replace_protected_entities(ProtectedEntitiesTVStations, tv_stations)

# Load the appropriate is_in_region map
# Can bypass use of specifications if desired
datamap_spec = SpecificationDataMap(DataMap2DContinentalUnitedStates, 400, 600)
region_map_spec = SpecificationRegionMap(BoundaryContinentalUnitedStates, datamap_spec)
region_map = region_map_spec.fetch_data()

ruleset = RulesetFcc2012()
"""Use old datamap constructors as data_management broken in my repository"""
#datamap_spec = data_map.DataMap2DContinentalUnitedStates.create(400, 600)
#region_map = data_map.DataMap2DContinentalUnitedStates.from_pickle("is_in_region400x600.pcl")
#region_map.log = getModuleLogger(region_map)

# FCC Polygons
"""data file present in FromKate"""

fcc_poly_filename = os.path.join("data", "TV contours", "export", "home",
                                 "radioTVdata", "results",
                                 "TV_service_contour_current.txt")
fcc_polys = FccPolygons(fcc_poly_filename)

# Buffer size
buffer_distance = 0

list_of_tv_stations = tv_stations.list_of_entities()

polylist = {}

for c in range(2, 52):
    polylist[c] = {}

for s in list_of_tv_stations:
    try:
        polylist[s.get_channel()][s.get_app_id()] = fcc_polys.get_poly_by_app_id(s.get_app_id())
    except KeyError:
        continue

for c in polylist.keys():
    print (c)
    kml = simplekml.Kml()
    for poly in polylist[c].values():
        poly.add_to_kml(kml)
    kml.save("Fcccontours_ch%d.kml" %c)


stamps_by_facility_id = dict()
facility_ids_outside_continental_us = []
missing_app_ids = {}
count = 0

"""for num, tv_station in enumerate(list_of_tv_stations):
    if tv_station.get_tx_type() == 'DD':
        continue
    facility_id = tv_station.get_facility_id()
    if facility_id in facility_ids_with_haat_zero.keys():
        tv_station._HAAT_meters = facility_ids_with_haat_zero[facility_id]
    if facility_id == '29455':
        tv_station._create_bounding_box(override_max_protected_radius_km = 250)
    print facility_id
    print "   Working on entry %d of %d" % (num, len(list_of_tv_stations))
    try:
        submap = generate_submap_for_protected_entity(region_map, tv_station)
    except ValueError:
        facility_ids_outside_continental_us.append(facility_id)
        print "Facility id %s is outside the continental US"%facility_id
        count = count + 1
        print count
        continue
    try:
        fcc_poly = fcc_polys.get_poly_by_app_id(tv_station.get_app_id())
        print "Creating FCC contour submap for facility ID %s"%facility_id
        stamp = make_fcc_stamp(fcc_poly.get_lonlat_coordinates(), bm, submap, buffer_distance)
        stamps_by_facility_id[facility_id] = ["fcc", stamp]
    except KeyError:
        print "Creating circular contour submap for facility ID %s"%facility_id
        stamp = make_circular_stamp(tv_station, tv_station.get_location(), region, ruleset, submap, buffer_distance)
        missing_app_ids[facility_id] = tv_station.get_app_id()
        stamps_by_facility_id[facility_id] = ["circular", stamp]


for num, tv_station in enumerate(list_of_tv_stations):
    facility_id = tv_station.get_facility_id()
    try:
        if tv_station.get_tx_type() == 'DD':
            stamps_by_facility_id[facility_id][1] = make_circular_stamp(tv_station, tv_station.get_location(), region, ruleset, stamps_by_facility_id[facility_id][1], buffer_distance)
    except KeyError:
        continue

with open("stamps_with_buffer=%dkm_with_dd.pkl"%buffer_distance, 'w') as output_file:
    pickle.dump(stamps_by_facility_id, output_file)"""




"""with open("stamps_with_buffer=%dkm.pkl" % buffer_distance, "w") as output_file:
    pickle.dump(stamps_by_facility_id, output_file)"""

"""circular_stamps_by_facility_id = {}

for num, tv_station in enumerate(list_of_tv_stations):
    facility_id = tv_station.get_facility_id()
    if tv_station.get_haat_meters() == 0:
        if facility_id in facility_ids_with_haat_zero:
            tv_station._HAAT_meters = facility_ids_with_haat_zero[facility_id]
        else:
            continue

    try:
        submap = generate_submap_for_protected_entity(region_map, tv_station)
    except ValueError:
        print "Facility id %s is outside the continental US"%facility_id
        continue

    print "Creating circular contour submap for facility ID %s"%facility_id
    stamp = make_circular_stamp(tv_station, tv_station.get_location(), region, ruleset, submap, buffer_distance)
    circular_stamps_by_facility_id[facility_id] = stamp

with open("circular_stamps_with_buffer=%dkm.pkl"%buffer_distance, 'w') as output_file:
    pickle.dump(circular_stamps_by_facility_id, output_file)"""

"""new_app_ids = {}

with open("new_app_ids_for_fcc_contours.csv", 'rU') as f:
    reader = csv.reader(f)
    for ind, row in enumerate(reader):
        if ind != 0:
            new_app_ids[row[0]] = row[1]

makeshift_fcc_contours = {}
for tv_station in list_of_tv_stations:
    if tv_station.get_facility_id() in new_app_ids.keys():
        submap = generate_submap_for_protected_entity(region_map, tv_station)
        if new_app_ids[tv_station.get_facility_id()] == 'N/A':
            continue
        fcc_poly = fcc_polys.get_poly_by_app_id(new_app_ids[tv_station.get_facility_id()])
        print "Creating makeshift FCC contour submap for facility ID %s"%tv_station.get_facility_id()
        stamp = make_fcc_stamp(fcc_poly.get_lonlat_coordinates(), bm, submap, buffer_distance)
        makeshift_fcc_contours[tv_station.get_facility_id()] = stamp

with open("makeshift_stamps_with_buffer=%dkm.pkl"%buffer_distance, 'w') as output_file:
    pickle.dump(makeshift_fcc_contours, output_file)"""








