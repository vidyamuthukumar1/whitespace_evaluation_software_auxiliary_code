import west.device
import west.data_map
import west.region_united_states
import region_united_states_vidya
import protected_entities_tv_stations_vidya, west.protected_entities_tv_stations
import west.population
import west.helpers
import west.boundary
from west.map import Map
#import map_test_vidya
import west.data_manipulation
import west.ruleset_fcc2012
import numpy
import pickle
import west.boundary
import os
import west.configuration
import csv
import west.data_management
from west.boundary import BoundaryContinentalUnitedStates, BoundaryContinentalUnitedStatesWithStateBoundaries
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def compute_tv_loss_map():
    testreg = west.region_united_states.RegionUnitedStates()
    testruleset = west.ruleset_fcc2012.RulesetFcc2012()
    bdr = west.boundary.BoundaryContinentalUnitedStates()

    tvstationlist = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(testreg)
    good_facility_ids = []
    with open(os.path.join("data", "FromVijay", "C-All free", "C-15ChannelsRemoved", "15VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            good_facility_ids.append(row[0])

    tvstationlist.prune_data(good_facility_ids)
    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    starting_map = is_in_region_map_spec.fetch_data()
    starting_map.reset_all_values(0)

    layer_list = range(2, 52)

    list_of_deleted_fids = []
    with open(os.path.join("data", "From Kate", "facilities_with_domain_leq_20.csv"), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            list_of_deleted_fids.append(row[0])

    def del_filter_function(station):
        if station.get_facility_id() in list_of_deleted_fids:
            return True
        else:
            return False

    with open("stamps_with_buffer=0km.pkl", 'r') as f:
        submapdict_cochannel = pickle.load(f)

    for k in submapdict_cochannel.keys():
        submapdict_cochannel[k].mutable_matrix = 1 - submapdict_cochannel[k].mutable_matrix

    test_device_gridmap = west.data_map.DataMap3D.from_DataMap2D(starting_map, layer_list)


    count = 0
    deletedstationslist = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(testreg)
    deletedstationslist.prune_data(good_facility_ids)
    deletedstationslist.remove_entities(del_filter_function)
    deletedstationslist.export_to_kml(os.path.join("data", "For Kate", "stations_domain_leq_20.kml"))
    for s in tvstationlist.stations():
        if s.get_facility_id() in list_of_deleted_fids and s.get_facility_id() in submapdict_cochannel.keys():
            count = count + 1
            print (count)
            test_device_gridmap.get_layer(s.get_channel()).reintegrate_submap(submapdict_cochannel[s.get_facility_id()], lambda x, y: x + y)

    tv_loss_map = test_device_gridmap.sum_all_layers()
    tv_loss_map.to_pickle(os.path.join("data", "For Kate", "tv_loss_map_domain_leq_20.pcl"))
    #test_device_gridmap.to_pickle(os.path.join("data", "For Kate", "tv_loss_domain_leq_40_allchannels.pcl"))



def see_tv_loss_map():
    tv_loss_map = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "For Kate", "tv_loss_map_domain_leq_40.pcl"))
    #tv_loss_map = west.data_map.DataMap3D.from_pickle(os.path.join("data", "For Kate", "tv_loss_domain_leq_20_allchannels.pcl"))
    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    starting_map = is_in_region_map_spec.fetch_data()

    for i in range(400):
        for j in range(600):
            if tv_loss_map.get_value_by_index(i, j) == 0 and starting_map.get_value_by_index(i, j) != 0:
                tv_loss_map.set_value_by_index(i, j, -1)

    """for channel in range(2, 52):
        mapobj = tv_loss_map.get_layer(channel)
        new_map = Map(mapobj, is_in_region_map = starting_map)
        new_map.add_colorbar(vmin = 0, vmax = 3, decimal_precision = 0, label = "TV Channels")
        new_map.add_boundary_outlines(BoundaryContinentalUnitedStatesWithStateBoundaries())
        new_map.set_boundary_color('k')
        new_map.set_boundary_linewidth(1)
        new_map.make_region_background_white(starting_map)
        new_map.save(os.path.join("data", "For Kate", "tv_loss_domain_leq_40_channel%d.png"%channel))"""
    new_map = Map(tv_loss_map, is_in_region_map = starting_map)
    cmap = cm.jet
    cmap.set_under('0.90')
    cmap.set_over('w')
    cmap.set_bad('w')
    new_map._image.set_cmap(cmap)

    new_map.add_colorbar(decimal_precision=0, vmin = 0, vmax = 35, label = "Channels" )
    #new_map.set_title("Median Whitespace Map: B-%dChannelsRemoved"%n)

    new_map.add_boundary_outlines(BoundaryContinentalUnitedStatesWithStateBoundaries())
    new_map.set_colorbar_ticks([0, 5, 10, 15, 20, 25, 30, 35])
    new_map.set_boundary_color('k')
    new_map.set_boundary_linewidth(1)
    new_map.make_region_background_white(starting_map)
    new_map.blocking_show()

def see_tv_loss_ccdf():
    tv_loss_map = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "For Kate", "tv_loss_map_domain_leq_40.pcl"))
    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    population_map_spec = west.data_management.SpecificationPopulationMap(is_in_region_map_spec, west.population.PopulationData)
    population_map = population_map_spec.fetch_data()
    cdf = west.data_manipulation.calculate_cdf_from_datamap2d(tv_loss_map, population_map, is_in_region_map)
    ccdf = (cdf[0], 1 - cdf[1], cdf[2], cdf[3])
    plt.xlabel("Number of channels lost")
    plt.ylabel("CCDF")
    plt.plot(ccdf[0], ccdf[1])
    for i in range(len(ccdf[0])):
        if ccdf[0][i] == 1:
            print ccdf[1][i]
            break
    plt.show()

