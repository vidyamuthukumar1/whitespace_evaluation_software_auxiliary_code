import pickle
from ruleset_industrycanada2015 import RulesetIndustryCanada2015
from west.region_united_states import RegionUnitedStates
from west.data_management import SpecificationDataMap, SpecificationRegionMap
from west.ruleset_fcc2012 import RulesetFcc2012
"""Need to import data_map and boundary"""
import west.data_map
from west.device import Device
import west.boundary
from west.boundary import BoundaryContinentalUnitedStates, BoundaryContinentalUnitedStatesWithStateBoundaries
from west.data_map import DataMap2DContinentalUnitedStates
from west.helpers import generate_submap_for_protected_entity
from west.protected_entities_tv_stations import \
    ProtectedEntitiesTVStations
from protected_entities_tv_stations_vidya import ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack

from geopy.distance import vincenty
"""Need to import os as data_management is not imported anymore"""

import west.configuration


#This is done to take care of the HAAT zero bug.
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




def make_circular_stamp(station, ruleset, submap, separation_distance_km, far_side_separation_distance_km = None):

    if station.get_erp_watts() == 0:
        raise ValueError("TV station's ERP cannot be zero. Please check input.")

    station_location = station.get_location()

    max_protected_radius = ruleset.get_tv_protected_radius_km(station, station_location)

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
        if far_side_separation_distance_km is not None:
            return not (vincenty(station_location, current_location) <= max_protected_radius + separation_distance_km or vincenty(station_location, current_location) + max_protected_radius <= far_side_separation_distance_km)
        else:
            return not vincenty(station_location, current_location) <= max_protected_radius + separation_distance_km


    #Making the circular contour with buffer
    submap.update_all_values_via_function(point_not_within_circular_contour)

    return submap



def get_separation_distance_function_handle(device, ruleset, exclusion_type):
    if isinstance(ruleset, RulesetFcc2012):
        if exclusion_type == 'cochannel':
            separation_distance_function_handle = ruleset.get_tv_cochannel_separation_distance_km
        elif exclusion_type == 'adj_channel':
            separation_distance_function_handle = ruleset.get_tv_adjacent_channel_separation_distance_km
        else:
            raise ValueError("This type of exclusion is not supported on this ruleset")

    elif isinstance(ruleset, RulesetIndustryCanada2015):
        if exclusion_type == 'cochannel':
            if device.is_portable():
                separation_distance_function_handle = ruleset.get_tv_cochannel_separation_distance_km_for_portable_devices
            else:
                separation_distance_function_handle = ruleset.get_tv_cochannel_separation_distance_km_for_fixed_devices
        elif exclusion_type == 'adj_channel':
            if device.is_portable():
                separation_distance_function_handle = ruleset.get_tv_adjacent_channel_separation_distance_km_for_portable_devices
            else:
                separation_distance_function_handle = ruleset.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices
        elif exclusion_type == 'taboo_channel':
            if device.is_portable():
                separation_distance_function_handle = ruleset.get_tv_taboo_channel_separation_distance_km_for_portable_devices
            else:
                separation_distance_function_handle = ruleset.get_tv_taboo_channel_separation_distance_km_for_fixed_devices
        else:
            raise ValueError("This type of exclusion is not supported on this ruleset")
        return separation_distance_function_handle

def get_far_side_separation_distance_function_handle(device, ruleset, exclusion_type):
    if isinstance(ruleset, RulesetFcc2012):
        raise ValueError("This type of exclusion is not supported on this ruleset")

    elif isinstance(ruleset, RulesetIndustryCanada2015):
        if exclusion_type == 'cochannel':
            if device.is_portable():
                far_side_separation_distance_function_handle = ruleset.get_tv_cochannel_far_side_separation_distance_km_for_portable_devices
            else:
                far_side_separation_distance_function_handle = ruleset.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices
        elif exclusion_type == 'adj_channel':
            if device.is_portable():
                far_side_separation_distance_function_handle = ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_portable_devices
            else:
                far_side_separation_distance_function_handle = ruleset.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices
        elif exclusion_type == 'taboo_channel':
            if device.is_portable():
                far_side_separation_distance_function_handle = ruleset.get_tv_taboo_channel_far_side_separation_distance_km_for_portable_devices
            else:
                far_side_separation_distance_function_handle = ruleset.get_tv_taboo_channel_far_side_separation_distance_km_for_fixed_devices
        else:
            raise ValueError("This type of exclusion is not supported on this ruleset")
        return far_side_separation_distance_function_handle


def make_all_stamps(device, region, region_map, ruleset, separation_distance_function_handle, make_approximate_circular_contours = True, far_side_separation_distance_function_handle = None):

    list_of_tv_stations = region.get_protected_entities_of_type(west.protected_entities_tv_stations.ProtectedEntitiesTVStations).stations()

    #exclusion_type in ['cochannel', 'adj_channel', 'taboo_channel']

    stamps_by_facility_id = {}
    for num, tv_station in enumerate(list_of_tv_stations):
        if tv_station.get_tx_type() == 'DD':
            continue
        if exclusion_type == 'taboo_channel' and tv_station.is_digital():
            print "Skipping entry %d as it is not an analog TV station"%num
            continue
        facility_id = tv_station.get_facility_id()
        if facility_id in facility_ids_with_haat_zero.keys():
            tv_station._HAAT_meters = facility_ids_with_haat_zero[facility_id]
        #Buggy
        if facility_id == '29455':
            tv_station._create_bounding_box(override_max_protected_radius_km = 250)
        print facility_id
        if isinstance(ruleset, RulesetFcc2012):
            separation_distance_km = separation_distance_function_handle(device.get_haat())
            far_side_separation_distance_km = None
        elif isinstance(ruleset, RulesetIndustryCanada2015):
            if far_side_separation_distance_function_handle is None:
                raise ValueError("Need a far side separation distance function handle for this ruleset")
            if device.is_portable():
                separation_distance_km = separation_distance_function_handle(tv_station.is_digital())
                far_side_separation_distance_km = far_side_separation_distance_function_handle(tv_station.is_digital())
            else:
                separation_distance_km = separation_distance_function_handle(device.get_haat(), tv_station.get_center_frequency(), tv_station.is_digital())
                far_side_separation_distance_km = far_side_separation_distance_function_handle(device.get_haat(), tv_station.get_center_frequency(), tv_station.is_digital())

        print "Working on entry %d of %d" % (num, len(list_of_tv_stations))
        try:
            submap = generate_submap_for_protected_entity(region_map, tv_station)
        except ValueError:
            print "Facility id %s is outside region"%facility_id
            count = count + 1
            print count
            continue
        print "Creating circular contour submap for facility ID %s"%facility_id
        if make_approximate_circular_contours:
            stamp = make_circular_stamp(tv_station, ruleset, submap, separation_distance_km, far_side_separation_distance_km)
        else:
            stamp = make_accurate_stamp() #TODO: Define this function later
        stamps_by_facility_id[facility_id] = ["circular", stamp]


    #Adding auxiliary 'DD' transmitters to existing submaps
    for num, tv_station in enumerate(list_of_tv_stations):
        facility_id = tv_station.get_facility_id()
        try:
            if tv_station.get_tx_type() == 'DD':
                if isinstance(ruleset, RulesetFcc2012):
                    separation_distance_km = separation_distance_function_handle(device.get_haat())
                    far_side_separation_distance_km = None
                elif isinstance(ruleset, RulesetIndustryCanada2015):
                    if device.is_portable():
                        separation_distance_km = separation_distance_function_handle(tv_station.is_digital())
                        far_side_separation_distance_km = far_side_separation_distance_function_handle(tv_station.is_digital())
                    else:
                        separation_distance_km = separation_distance_function_handle(device.get_haat(), tv_station.get_center_frequency(), tv_station.is_digital())
                        far_side_separation_distance_km = far_side_separation_distance_function_handle(device.get_haat(), tv_station.get_center_frequency(), tv_station.is_digital())
                stamps_by_facility_id[facility_id][1] = make_circular_stamp(tv_station, ruleset, stamps_by_facility_id[facility_id][1],
                                                                            separation_distance_km, far_side_separation_distance_km)
        except KeyError:
            continue

    return stamps_by_facility_id


# Region and TV stations
region = RegionUnitedStates()
boundary = BoundaryContinentalUnitedStatesWithStateBoundaries()
tv_stations = ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(region)
region.replace_protected_entities(ProtectedEntitiesTVStations, tv_stations)

# Load the appropriate region map
datamap_spec = SpecificationDataMap(DataMap2DContinentalUnitedStates, 400, 600)
region_map_spec = SpecificationRegionMap(BoundaryContinentalUnitedStates, datamap_spec)
region_map = region_map_spec.fetch_data()

ruleset = RulesetIndustryCanada2015()

device = Device(0, 30, 1)

sep_distance_function_handle = get_separation_distance_function_handle(device, ruleset, "cochannel")
far_side_sep_distance_function_handle = get_far_side_separation_distance_function_handle(device, ruleset, "cochannel")
us_cochannel_stamps_canada_ruleset_fixed_devices = make_all_stamps(device, region, region_map, ruleset, sep_distance_function_handle, far_side_sep_distance_function_handle)

sep_distance_function_handle = get_separation_distance_function_handle(device, ruleset, "adj_channel")
far_side_sep_distance_function_handle = get_far_side_separation_distance_function_handle(device, ruleset, "adj_channel")
us_adjchannel_stamps_canada_ruleset_fixed_devices = make_all_stamps(device, region, region_map, ruleset, sep_distance_function_handle, far_side_sep_distance_function_handle)

sep_distance_function_handle = get_separation_distance_function_handle(device, ruleset, "taboo_channel")
far_side_sep_distance_function_handle = get_far_side_separation_distance_function_handle(device, ruleset, "taboo_channel")
us_taboochannel_stamps_canada_ruleset_fixed_devices = make_all_stamps(device, region, region_map, ruleset, sep_distance_function_handle, far_side_sep_distance_function_handle)

device = Device(1, 30, 1)

sep_distance_function_handle = get_separation_distance_function_handle(device, ruleset, "cochannel")
far_side_sep_distance_function_handle = get_far_side_separation_distance_function_handle(device, ruleset, "cochannel")
us_cochannel_stamps_canada_ruleset_portable_devices = make_all_stamps(device, region, region_map, ruleset, sep_distance_function_handle, far_side_sep_distance_function_handle)

sep_distance_function_handle = get_separation_distance_function_handle(device, ruleset, "adj_channel")
far_side_sep_distance_function_handle = get_far_side_separation_distance_function_handle(device, ruleset, "adj_channel")
us_adjchannel_stamps_canada_ruleset_portable_devices = make_all_stamps(device, region, region_map, ruleset, sep_distance_function_handle, far_side_sep_distance_function_handle)

sep_distance_function_handle = get_separation_distance_function_handle(device, ruleset, "taboo_channel")
far_side_sep_distance_function_handle = get_far_side_separation_distance_function_handle(device, ruleset, "taboo_channel")
us_taboochannel_stamps_canada_ruleset_portable_devices = make_all_stamps(device, region, region_map, ruleset, sep_distance_function_handle, far_side_sep_distance_function_handle)


with open("us_cochannel_stamps_canada_ruleset_fixed_devices.pkl", 'w') as output_file:
    pickle.dump(us_cochannel_stamps_canada_ruleset_fixed_devices, output_file)

with open("us_cochannel_stamps_canada_ruleset_portable_devices.pkl", 'w') as output_file:
    pickle.dump(us_cochannel_stamps_canada_ruleset_portable_devices, output_file)

with open("us_adjchannel_stamps_canada_ruleset_fixed_devices.pkl", 'w') as output_file:
    pickle.dump(us_adjchannel_stamps_canada_ruleset_fixed_devices, output_file)

with open("us_adjchannel_stamps_canada_ruleset_portable_devices.pkl", 'w') as output_file:
    pickle.dump(us_adjchannel_stamps_canada_ruleset_portable_devices, output_file)

with open("us_taboochannel_stamps_canada_ruleset_fixed_devices.pkl", 'w') as output_file:
    pickle.dump(us_taboochannel_stamps_canada_ruleset_fixed_devices, output_file)

with open("us_taboochannel_stamps_canada_ruleset_portable_devices.pkl", 'w') as output_file:
    pickle.dump(us_taboochannel_stamps_canada_ruleset_portable_devices, output_file)











