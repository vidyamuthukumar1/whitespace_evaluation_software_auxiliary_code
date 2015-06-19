import west.data_map_signal_strength
import west.protected_entities_tv_stations, protected_entities_tv_stations_vidya
import west.region_united_states
from west.propagation_model_fcurves import PropagationModelFcurvesWithoutTerrain, PropagationCurve
import west.data_map
import west.data_management
import west.helpers
import west.device
import os
from west.map import Map
from west.boundary import BoundaryContinentalUnitedStatesWithStateBoundaries
import west.ruleset_fcc2012
import csv
import numpy
import pickle

create_original_noise_map = False
find_powers_on_all_channels = False
test_submap_for_new_channel = False
create_submaps = False
test_original_and_a_repack = False
make_map_noise = False
find_datarate_for_a_repack = True
make_datarate_tadpole = False

if create_original_noise_map:
    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    testmap = west.data_map_signal_strength.DataMap2DSignalStrengthSum.get_copy_of(is_in_region_map)
    testmap.reset_all_values(0)

    testreg = west.region_united_states.RegionUnitedStates()
    good_facility_ids = []
    with open(os.path.join("data", "FromVijay", "C-All free", "C-15ChannelsRemoved", "15VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            good_facility_ids.append(row[0])

    tvstationlist = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(testreg)
    tvstationlist.prune_data(good_facility_ids)


    pm = PropagationModelFcurvesWithoutTerrain()
    pl_function = lambda *args, **kwargs: pm.get_pathloss_coefficient(*args, curve_enum=PropagationCurve.curve_50_90, **kwargs)
    count = 0


    for s in tvstationlist.stations():
        s._protected_bounding_box = {'min_lat': s.get_latitude() - 3, 'max_lat': s.get_latitude() + 3, 'min_lon': s.get_longitude() - 4, 'max_lon': s.get_longitude() + 4}

    s = tvstationlist.stations()[1]
    testmap.add_tv_stations([s], pathloss_function = pl_function)
    """for s in tvstationlist.stations():
        count = count + 1
        print (count)
        testmap.add_tv_stations([s], pathloss_function = pl_function)
    testmap.to_pickle(os.path.join("data", "Noise Maps", "noise_map_test_originalallocation_actual.pcl"))"""


    countzero = 0
    for i in range(400):
        for j in range(600):
            if testmap.get_value_by_index(i, j) == 0.0:
                testmap.set_value_by_index(i, j, -(numpy.inf))
            else:
                testmap.set_value_by_index(i, j, numpy.log(testmap.get_value_by_index(i, j))/numpy.log(10))

    new_map = testmap.make_map(is_in_region_map = is_in_region_map)



    #new_map = Map(testmap, transformation = 'log', is_in_region_map = is_in_region_map)
    new_map.add_boundary_outlines(BoundaryContinentalUnitedStatesWithStateBoundaries())
    new_map._image.set_clim(-20, 0)
    #new_map.add_colorbar(vmin = -30, vmax = 0, decimal_precision = 0)
    new_map.set_boundary_color('k')
    new_map.set_boundary_linewidth(1)
    new_map.make_region_background_white(is_in_region_map)
    new_map.blocking_show()

def get_power_on_new_channel(station, new_channel, max_protected_radius_km):
    #pm = PropagationModelFcurvesWithoutTerrain()
    #pl_function = lambda *args, **kwargs: pm.get_pathloss_coefficient_unchecked(*args, curve_enum=PropagationCurve.curve_50_90, **kwargs)
    station._channel = new_channel
    new_pathloss = pl_function(max_protected_radius_km, frequency = station.get_center_frequency(), tx_height = station.get_haat_meters(), rx_height = None, tx_location = station.get_location())
    freq = station.get_center_frequency()
    target_field_strength_dBu = testruleset.get_tv_target_field_strength_dBu(s.is_digital(), freq)
    desired_watts = pm.dBu_to_Watts(target_field_strength_dBu, freq)
    station._ERP_Watts = desired_watts/new_pathloss
    return desired_watts/new_pathloss


if find_powers_on_all_channels:
    testreg = west.region_united_states.RegionUnitedStates()
    testruleset = west.ruleset_fcc2012.RulesetFcc2012()
    good_facility_ids = []
    with open(os.path.join("data", "FromVijay", "C-All free", "C-15ChannelsRemoved", "15VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            good_facility_ids.append(row[0])

    tvstationlist = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(testreg)
    tvstationlist.prune_data(good_facility_ids)

    s = tvstationlist.stations()[1]
    print s.get_channel()

    power_on_all_channels = {}
    desired_watts_on_all_channels = {}
    pathloss_on_all_channels = {}
    channel_list = range(2, 52)
    channel_list.remove(37)

    pm = PropagationModelFcurvesWithoutTerrain()
    pl_function = lambda *args, **kwargs: pm.get_pathloss_coefficient_unchecked(*args, curve_enum=PropagationCurve.curve_50_90, **kwargs)

    max_protected_radius_km = testruleset.get_tv_protected_radius_km(s, s.get_location())
    original_pathloss = pl_function(max_protected_radius_km, frequency = s.get_center_frequency(), tx_height = s.get_haat_meters(), rx_height = None, tx_location = s.get_location())
    original_power = s.get_erp_watts()
    freq = s.get_center_frequency()

    for c in channel_list:
        power_on_all_channels[c] = get_power_on_new_channel(s, c, max_protected_radius_km)
        #print (testruleset.get_tv_protected_radius_km(s, s.get_location()))

    import matplotlib.pyplot as plt
    plt.plot(power_on_all_channels.keys(), power_on_all_channels.values())
    #plt.plot(desired_watts_on_all_channels.keys(), desired_watts_on_all_channels.values())
    #plt.plot(pathloss_on_all_channels.keys(), pathloss_on_all_channels.values())
    plt.show()

if test_submap_for_new_channel:
    testreg = west.region_united_states.RegionUnitedStates()
    testruleset = west.ruleset_fcc2012.RulesetFcc2012()
    pm = PropagationModelFcurvesWithoutTerrain()
    pl_function = lambda *args, **kwargs: pm.get_pathloss_coefficient(*args, curve_enum=PropagationCurve.curve_50_90, **kwargs)
    good_facility_ids = []
    with open(os.path.join("data", "FromVijay", "C-All free", "C-15ChannelsRemoved", "15VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            good_facility_ids.append(row[0])

    tvstationlist = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(testreg)
    tvstationlist.prune_data(good_facility_ids)

    s = tvstationlist.stations()[1]
    print s.get_channel()

    max_protected_radius_km = testruleset.get_tv_protected_radius_km(s, s.get_location())
    new_channel = 12
    s._ERP_Watts = get_power_on_new_channel(s, new_channel, max_protected_radius_km)
    s._channel = new_channel
    s._protected_bounding_box = {'min_lat': s.get_latitude() - 3, 'max_lat': s.get_latitude() + 3, 'min_lon': s.get_longitude() - 4, 'max_lon': s.get_longitude() + 4}

    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    testmap = west.data_map_signal_strength.DataMap2DSignalStrengthSum.get_copy_of(is_in_region_map)
    testmap.reset_all_values(0)

    testmap.add_tv_stations([s], pathloss_function = pl_function)

    for i in range(400):
        for j in range(600):
            if testmap.get_value_by_index(i, j) == 0.0:
                testmap.set_value_by_index(i, j, -(numpy.inf))
            else:
                testmap.set_value_by_index(i, j, numpy.log(testmap.get_value_by_index(i, j))/numpy.log(10))


    new_map = testmap.make_map(is_in_region_map = is_in_region_map)



    #new_map = Map(testmap, transformation = 'log', is_in_region_map = is_in_region_map)
    new_map.add_boundary_outlines(BoundaryContinentalUnitedStatesWithStateBoundaries())
    new_map._image.set_clim(-20, 0)
    #new_map.add_colorbar(vmin = -30, vmax = 0, decimal_precision = 0)
    new_map.set_boundary_color('k')
    new_map.set_boundary_linewidth(1)
    new_map.make_region_background_white(is_in_region_map)
    new_map.blocking_show()

if create_submaps:
    testreg = west.region_united_states.RegionUnitedStates()
    testruleset = west.ruleset_fcc2012.RulesetFcc2012()
    pm = PropagationModelFcurvesWithoutTerrain()
    pl_function = lambda *args, **kwargs: pm.get_pathloss_coefficient(*args, curve_enum=PropagationCurve.curve_50_90, **kwargs)
    good_facility_ids = []
    with open(os.path.join("data", "FromVijay", "C-All free", "C-15ChannelsRemoved", "15VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            good_facility_ids.append(row[0])

    tvstationlist = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(testreg)
    tvstationlist.prune_data(good_facility_ids)

    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    testmap = west.data_map_signal_strength.DataMap2DSignalStrengthSum.get_copy_of(is_in_region_map)

    noise_submaps = {}
    for s in tvstationlist.stations():
        noise_submaps[s] = {}

    for s in tvstationlist.stations():
        s._protected_bounding_box = {'min_lat': s.get_latitude() - 3.5, 'max_lat': s.get_latitude() + 3.5, 'min_lon': s.get_longitude() - 4.5, 'max_lon': s.get_longitude() + 4.5}

    channel_list = range(2, 52)
    channel_list.remove(37)

    count = 0
    for s in tvstationlist.stations():
        count = count + 1
        print "Station number  %d"%count
        max_protected_radius_km = testruleset.get_tv_protected_radius_km(s, s.get_location())
        for channel in channel_list:
            if channel != s.get_channel():
                continue
            print (s.get_erp_watts())
            testmap.reset_all_values(0)
            s._ERP_watts = get_power_on_new_channel(s, channel, max_protected_radius_km)
            print (s.get_erp_watts())
            testmap.add_tv_stations([s], pathloss_function = pl_function)
            try:
                noise_submaps[s][channel] = west.helpers.generate_submap_for_protected_entity(testmap, s)
            except ValueError:
                continue

    #noise_submaps.to_pickle("noise_submaps.pcl")

def make_map(noisemap, is_in_region_map, cmin = 0, cmax = 50, calculate_logs = True):
    if calculate_logs:
        for i in range(400):
            for j in range(600):
                if noisemap.get_value_by_index(i, j) == 0.0:
                    noisemap.set_value_by_index(i, j, -(numpy.inf))
                else:
                    noisemap.set_value_by_index(i, j, numpy.log(noisemap.get_value_by_index(i, j))/numpy.log(10))

    new_map = noisemap.make_map(is_in_region_map = is_in_region_map)



    #new_map = Map(testmap, transformation = 'log', is_in_region_map = is_in_region_map)
    new_map.add_boundary_outlines(BoundaryContinentalUnitedStatesWithStateBoundaries())
    #new_map._image.set_clim(cmin, cmax)
    #new_map._image.set_clim(-1e-11, 1e-11)
    new_map.add_colorbar(vmin = cmin, vmax = cmax, decimal_precision = 0)
    new_map.set_boundary_color('k')
    new_map.set_boundary_linewidth(1)
    new_map.make_region_background_white(is_in_region_map)
    new_map.blocking_show()


if test_original_and_a_repack:
    test_repack = True
    testreg = west.region_united_states.RegionUnitedStates()
    testruleset = west.ruleset_fcc2012.RulesetFcc2012()
    pm = PropagationModelFcurvesWithoutTerrain()
    pl_function = lambda *args, **kwargs: pm.get_pathloss_coefficient(*args, curve_enum=PropagationCurve.curve_50_90, **kwargs)
    good_facility_ids = []
    with open(os.path.join("data", "FromVijay", "C-All free", "C-15ChannelsRemoved", "15VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            good_facility_ids.append(row[0])

    tvstationlist = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(testreg)
    tvstationlist.prune_data(good_facility_ids)

    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    testmap = west.data_map_signal_strength.DataMap2DSignalStrengthSum.get_copy_of(is_in_region_map)
    testmap.reset_all_values(0)
    channel_list = range(2, 52)
    channel_list.remove(37)
    testmap3D = west.data_map.DataMap3D.from_DataMap2D(testmap, channel_list)

    noise_submaps = {}
    count = 0
    for s in tvstationlist.stations():
        count = count + 1
        print (count)
        with open(os.path.join("data", "Noise Submaps", "noise_submaps%d.pkl"%count), 'r') as f:
            noise_submaps[s] = pickle.load(f)

    if test_repack:
        repack_file = "15VHFFreeUSMinimumStationstoRemove0.csv"
        tvstationlist.implement_repack(repack_file, 15)

    count = 0
    for s in tvstationlist.stations():
        if noise_submaps[s] == {}:
            continue
        count = count + 1
        print (count)
        c = s.get_channel()
        testmap3D.get_layer(c).reintegrate_submap(noise_submaps[s][c], lambda x, y: x + y)

    if test_repack:
        filename = "noise_map_test_repack_withsubmaps.pcl"
        filename2 = "noise_map_test_repack_allchannels_withsubmaps.pcl"
    else:
        filename = "noise_map_test_original_allocation_withsubmaps.pcl"
        filename2 = "noise_map_test_original_allocation_allchannels_withsubmaps.pcl"
    testmap3D.to_pickle(os.path.join("data", "Noise Maps", filename))
    testmap3D.sum_all_layers().to_pickle(os.path.join("data", "Noise Maps", filename2))

if make_map_noise:
    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    noisemap = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "Noise Maps", "noise_map_test_repack_allchannels_withsubmaps.pcl"))
    #noisemap = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "Noise Maps", "noise_map_test_original_allocation_allchannels_withsubmaps.pcl"))
    #noisemap2 = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "Noise Maps", "noise_map_test_originalallocation_actual.pcl"))

    #diffmap = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)
    #diffmap.mutable_matrix = noisemap2.mutable_matrix - noisemap.mutable_matrix

    make_map(noisemap, is_in_region_map)


if find_datarate_for_a_repack:

    def logoneplussnrfunction(this_value, other_value):
        if this_value == 0 and other_value == 0:
            return 0
        return numpy.log(1 + float(other_value/this_value))/numpy.log(2)

    def dataratefunction(this_value, other_value):
        return other_value * 6 * 1000000 * this_value

    def and_function(this_value, other_value):
        if other_value == 0:
            return 0
        else:
            return this_value

    test_repack = True
    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    testdevice = west.device.Device(0, 100, 1)
    testreg = west.region_united_states.RegionUnitedStates()

    pm = PropagationModelFcurvesWithoutTerrain()
    pl_function = lambda *args, **kwargs: pm.get_pathloss_coefficient(*args, curve_enum=PropagationCurve.curve_50_90, **kwargs)


    distance_km = 10
    transmission_power = 4
    signal_power = {}
    channel_list = range(2, 52)
    channel_list.remove(37)
    if test_repack:
        for c in range(52 - 14, 52):
            channel_list.remove(c)
    signal_map = west.data_map.DataMap3D.from_DataMap2D(is_in_region_map, channel_list)
    for c in channel_list:
        freq = testreg.get_center_frequency(c)
        pathloss = pl_function(distance_km, frequency=freq, tx_height=testdevice.get_haat(), rx_height=None)
        signal_power[c] = pathloss * transmission_power
        signal_map.get_layer(c).reset_all_values(signal_power[c])
        signal_map.set_layer(c, signal_map.get_layer(c).combine_datamaps_with_function(is_in_region_map, and_function))

    if test_repack:
        noisefilename = "noise_map_test_repack_withsubmaps.pcl"
    else:
        noisefilename = "noise_map_test_original_allocation_withsubmaps.pcl"

    noise_map = west.data_map.DataMap3D.from_pickle(os.path.join("data", "Noise Maps", noisefilename))

    for c in channel_list:
        n = noise_map.get_layer(c)
        for i in range(400):
            for j in range(600):
                n.set_value_by_index(i, j, n.get_value_by_index(i, j) + 2.4017220000000003e-14)
        noise_map.set_layer(c, n)

    if test_repack:
        exclusionfilename = "15VHFFreeUSMinimumStationstoRemove0_allchannels.pcl"
    else:
        exclusionfilename = "original_map_fcccontours_withplmrs_allchannels.pcl"
    exclusion_map_3D = west.data_map.DataMap3D.from_pickle(exclusionfilename)

    #make_map(exclusion_map_3D.sum_subset_of_layers(channel_list), is_in_region_map, cmin = 0, cmax = 50, calculate_logs = False)
    #make_map(noise_map.sum_subset_of_layers(channel_list), is_in_region_map, cmin = -20, cmax = 0)


    dataratemap3D = west.data_map.DataMap3D.from_DataMap2D(is_in_region_map, channel_list)
    for c in channel_list:
        print c
        logoneplussnr = noise_map.get_layer(c).combine_datamaps_with_function(signal_map.get_layer(c), logoneplussnrfunction)
        #make_map(logoneplussnr, is_in_region_map, calculate_logs = False)
        dataratechannel = logoneplussnr.combine_datamaps_with_function(exclusion_map_3D.get_layer(c), dataratefunction)
        dataratemap3D.set_layer(c, dataratechannel)
        #make_map(dataratechannel, is_in_region_map, calculate_logs = False)

    totaldatarate = dataratemap3D.sum_all_layers()
    for i in range(400):
        for j in range(600):
            totaldatarate.set_value_by_index(i, j, totaldatarate.get_value_by_index(i, j) * 1e-9)
    make_map(totaldatarate, is_in_region_map, cmin = 0, cmax = 5.2, calculate_logs = False)
    """if test_repack:
        totaldatarate.to_pickle(os.path.join("data", "Data Rate Maps", "datarate_repack_range=%dkm.pcl"%distance_km))
    else:
        totaldatarate.to_pickle(os.path.join("data", "Data Rate Maps", "datarate_original_range=%dkm.pcl"%distance_km))"""

if make_datarate_tadpole:
    number_of_bins = 90
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    originaldatarate = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "Data Rate Maps", "datarate_original.pcl"))
    repackdatarate = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "Data Rate Maps", "datarate_repack.pcl"))
    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    population_map_spec = west.data_management.SpecificationPopulationMap(is_in_region_map_spec, west.population.PopulationData)
    population_map = population_map_spec.fetch_data()

    dataimgplot = numpy.zeros((number_of_bins, number_of_bins))
    bins = numpy.linspace(0, 5.2, number_of_bins + 1)
    originalindices = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(originaldatarate)
    repackindices = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(repackdatarate)
    maskmap = west.data_map.DataMap2D.from_specification((0, number_of_bins + 1), (0, number_of_bins + 1), number_of_bins + 1, number_of_bins + 1)
    maskmap.reset_all_values(0)

    def update_function(latitude, longitude, latitude_index, longitude_index, current_value):
        for i in range(len(bins)):
            if current_value >= bins[i] and current_value < bins[i + 1]:
                return i

    originalindices.update_all_values_via_function(update_function)
    repackindices.update_all_values_via_function(update_function)

    for i in range(400):
        for j in range(600):
            if is_in_region_map.get_value_by_index(i, j) != 0:
                maskmap.set_value_by_index(repackindices.get_value_by_index(i, j), originalindices.get_value_by_index(i, j), 1)
                dataimgplot[repackindices.get_value_by_index(i, j)][originalindices.get_value_by_index(i,j)] = dataimgplot[repackindices.get_value_by_index(i, j)][originalindices.get_value_by_index(i,j)] + population_map.get_value_by_index(i, j)

    for i in range(number_of_bins):
        for j in range(number_of_bins):
            if maskmap.get_value_by_index(i, j) == 0:
                dataimgplot[i][j] = numpy.inf
            else:
                dataimgplot[i][j] = numpy.log(1 + dataimgplot[i][j])/numpy.log(10)

    fig = plt.figure(figsize = (9, 9))
    ax = fig.add_subplot(111)
    c_map = cm.jet
    c_map.set_over('w')
    ax.imshow(dataimgplot, cmap = c_map, vmin = 0, vmax = 8, interpolation = 'nearest')
    plt.gca().invert_yaxis()
    plt.xlabel("Original datarate (Gbps)")
    labelindices = numpy.linspace(0, number_of_bins, 6)
    print (labelindices)
    labelbins = []
    for i in range(6):
        labelbins.append(bins[labelindices[i]])
    plt.xticks(labelindices)
    ax.set_xticklabels(labelbins)
    plt.ylabel("Datarate after repack (Gbps)")
    plt.yticks(labelindices)
    ax.set_yticklabels(labelbins)
    xy = range(0, number_of_bins)
    plt.plot(xy, xy, 'k')
    plt.xlim(0, number_of_bins)
    plt.ylim(0, number_of_bins)
    plt.savefig(os.path.join("data", "Data Rate Maps", "datarate_tadpole_numberofbins=%d.png"%number_of_bins))





























