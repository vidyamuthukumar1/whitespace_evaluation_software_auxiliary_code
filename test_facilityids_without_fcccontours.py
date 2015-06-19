import west.device
import west.data_map
import west.data_management
import west.region_united_states
import west.region_united_states_vidya
from west.boundary import BoundaryContinentalUnitedStatesWithStateBoundaries
import protected_entities_tv_stations_vidya, west.protected_entities_tv_stations
import west.helpers
import west.boundary
from west.map import Map
#import map_test_vidya
import west.data_manipulation
import west.ruleset_fcc2012
import numpy
import pickle
import west.boundary
import west.population
import os
import west.configuration
import csv
import matplotlib.cm

def plot_map(datamap, is_in_region_map, cmin, cmax):
    new_map = datamap.make_map(is_in_region_map = is_in_region_map)
    new_map.add_boundary_outlines(BoundaryContinentalUnitedStatesWithStateBoundaries())
    #cmap = matplotlib.cm.Reds
    cmap = matplotlib.cm.jet
    cmap.set_under('0.90')
    cmap.set_over('w')
    cmap.set_bad('w')
    new_map._image.set_cmap(cmap)
    new_map._image.set_clim(cmin, cmax)
    #new_map.add_colorbar(vmin = cmin, vmax = cmax, decimal_precision = 0)
    new_map.set_boundary_color('k')
    new_map.set_boundary_linewidth(1)
    new_map.make_region_background_white(is_in_region_map)
    new_map.blocking_show()
    #return new_map

def set_zeros_to_inf(latitude, longitude, latitude_index, longitude_index, current_value):
    if current_value == 0:
        return numpy.inf

    return current_value

test_repacks = True
test_choppedoff = False

def median_function(latitude, longitude, latitude_index, longitude_index, list_of_values_in_order):
    return numpy.median(list_of_values_in_order)

def stddev_function(latitude, longitude, latitude_index, longitude_index, list_of_values_in_order):
    return numpy.std(list_of_values_in_order)


testreg = west.region_united_states.RegionUnitedStates()
testruleset = west.ruleset_fcc2012.RulesetFcc2012()
bdr = west.boundary.BoundaryContinentalUnitedStates()

base_directory = west.configuration.paths['UnitedStates']['protected_entities']

good_facility_ids = []
with open(os.path.join("data", "FromVijay", "C-All free", "C-15ChannelsRemoved", "15VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        good_facility_ids.append(row[0])

tvstationlist = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(testreg)
tvstationlist.prune_data(good_facility_ids)

layer_list = range(2, 52)

datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
is_in_region_map = is_in_region_map_spec.fetch_data()
starting_map = is_in_region_map_spec.fetch_data()
population_map_spec = west.data_management.SpecificationPopulationMap(is_in_region_map_spec, west.population.PopulationData)
population_map = population_map_spec.fetch_data()

starting_map.reset_all_values(0)

test_device_gridmap = west.data_map.DataMap3D.from_DataMap2D(starting_map, layer_list)

with open("circular_stamps_with_buffer=0km.pkl", "r") as f:
    submapdict_cochannel = pickle.load(f)

count = 0
for fid in submapdict_cochannel.keys():
    if tvstationlist.stationdict[fid] not in tvstationlist.stations():
        continue
    count = count + 1
    print count
    test_device_gridmap.get_layer(tvstationlist.stationdict[fid].get_channel()).reintegrate_submap(submapdict_cochannel[fid], lambda x, y: x + y)

tv_map = test_device_gridmap.sum_all_layers()
tv_map.update_all_values_via_function(set_zeros_to_inf)
populationaffected = 0
placesaffected = 0

for i in range(400):
    for j in range(600):
        if tv_map.get_value_by_index(i, j) != 0 and is_in_region_map.get_value_by_index(i, j) != 0:
            populationaffected += population_map.get_value_by_index(i, j)
            placesaffected += 1
plot_map(tv_map, is_in_region_map, 0, 2)


