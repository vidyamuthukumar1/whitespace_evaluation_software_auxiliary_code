import west.data_map
import west.data_management
import west.population
import numpy
import scipy

def evaluate_hex_capacity(p = 250, min_radius = 0.05, max_radius = 100, test_repack = False):

    areaarray = numpy.logspace(numpy.log(numpy.pi * 0.05 * 0.05)/numpy.log(10), numpy.log(numpy.pi * 100 * 100)/numpy.log(10), 65)

    def divide_function(this_value, other_value):
        if this_value == 0 and other_value == 0:
            return 0
        return float(this_value/other_value)

    def calculate_tower_area(latitude, longitude, latitude_index, longitude_index, current_value):
        return p / current_value

    def find_area_less_than_and_greater_than_towerarea(tower_area):
        for i in range(len(areaarray)):
            if areaarray[i] <= tower_area and areaarray[i + 1] > tower_area:
                if i == len(areaarray) - 1:
                    return areaarray[i], None
                return areaarray[i], areaarray[i + 1]

    def interpolate(low_value, high_value, low_area, high_area, actual_area):
        low_value_log = numpy.log(low_value)/numpy.log(10)
        high_value_log = numpy.log(high_value)/numpy.log(10)
        actual_value_log = (high_value_log - low_value_log)/(high_area - low_area) * (actual_area - low_area)
        actual_value = scipy.power(10, actual_value_log)
        return actual_value


    with open ("noisestrength_hex_data.pkl", 'r') as f:
        interferencestrengthsdict = pickle.load(f)

    with open("signalstrength_hex_data.pkl", 'r') as f:
        signalstrengthsdict = pickle.load(f)

    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    population_map_spec = west.data_management.SpecificationPopulationMap(is_in_region_map_spec, west.population.PopulationData)
    population_map = population_map_spec.fetch_data()
    region_area_map_spec = west.data_management.SpecificationRegionAreaMap(datamap_spec)
    region_area_map = region_area_map_spec.fetch_data()
    population_density_map = population_map.combine_datamaps_with_function(region_area_map, divide_function)
    areaoftower_map = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(population_density_map)

    #Note: Keep in mind what will happen if the population density is 0.
    areaoftower_map.update_all_values_via_function(calculate_tower_area)
    min_area = numpy.pi * min_radius * min_radius
    max_area = numpy.pi * max_radius * max_radius

    def clip_map(latitude, longitude, latitude_index, longitude_index, current_value):
        if current_value > max_area:
            return max_area
        if current_value < min_area:
            return min_area
        return current_value


    areaoftower_map.update_all_values_via_function(clip_map)

    channel_list = range(2, 52)
    channel_list.remove(37)

    if test_repack:
        exclusionfilename = "15VHFFreeUSMinimumStationstoRemove0_allchannels.pcl"
        noisefilename = "noise_map_test_repack_withsubmaps.pcl"
    else:
        exclusionfilename = "original_map_fcccontours_withplmrs_allchannels.pcl"
        noisefilename = "noise_map_test_original_allocation_withsubmaps.pcl"


    exclusion_map_3D = west.data_map.DataMap3D.from_pickle(exclusionfilename)
    noise_map_3D = west.data_map.DataMap3D.from_pickle(os.path.join("data", "Noise Maps", noisefilename))


    fair_capacity_hex_map_3D = west.data_map.DataMap3D.from_DataMap2D(is_in_region_map, channel_list)
    avg_capacity_hex_map_3D = west.data_map.DataMap3D.from_DataMap2D(is_in_region_map, channel_list)
    min_capacity_hex_map_3D = west.data_map.DataMap3D.from_DataMap2D(is_in_region_map, channel_list)

    for c in channel_list:
        faircapacity_channelmap = fair_capacity_hex_map_3D.get_layer(c)
        avgcapacity_channelmap = avg_capacity_hex_map_3D.get_layer(c)
        mincapacity_channelmap = min_capacity_hex_map_3D.get_layer(c)
        for i in range(400):
            for j in range(600):
                if is_in_region_map.get_value_by_index(i, j) == 0:
                    continue
                tower_area = areaoftower_map.get_value_by_index(i, j)
                low_area, high_area = find_area_less_than_and_greater_than_towerarea(tower_area)
                if high_area == None:
                    high_area = areaarray[len(areaarray) - 1]
                low_signal = signalstrengthsdict[c][low_area]
                high_signal = signalstrengthsdict[c][high_area]
                low_interference = interferencestrengthsdict[c][low_area]
                high_interference = interferencestrengthsdict[c][high_area]

                signal = interpolate(low_signal, high_signal, low_area, high_area, tower_area)
                interference = interpolate(low_interference, high_interference, low_area, high_area, tower_area)
                total_noise = interference + noise_map_3D.get_layer(c).get_value_by_index(i, j)
                potential_capacity = exclusion_map_3D.get_layer(c).get_value_by_index(i, j) * 6e6 * numpy.log(1 + signal/total_noise)

                #Fair capacity: If each person is allowed to use the same rate, what would this rate be?
                fair_capacity_per_person = 1/sum(1/potential_capacity)

                total_fair_capacity = fair_capacity_per_person * p
                faircapacity_channelmap.set_value_by_index(i, j, total_fair_capacity)

                #Avg capacity
                avg_capacity = numpy.mean(potential_capacity)
                avgcapacity_channelmap.set_value_by_index(i, j, avg_capacity)

                #Min capacity
                min_capacity = min(potential_capacity)
                mincapacity_channelmap.set_value_by_index(i, j, min_capacity)

    fair_capacity_hex_map = fair_capacity_hex_map_3D.sum_all_layers()
    avg_capacity_hex_map = avg_capacity_hex_map_3D.sum_all_layers()
    min_capacity_hex_map = min_capacity_hex_map_3D.sum_all_layers()

    return fair_capacity_hex_map, avg_capacity_hex_map, min_capacity_hex_map


faircapacityhexmap, avgcapacityhexmap, mincapacityhexmap = evaluate_hex_capacity()

faircapacityhexmap.to_pickle(os.path.join("data", "Data Rate Maps", "hex_fair_capacity_original_allocation.pcl"))
avgcapacityhexmap.to_pickle(os.path.join("data", "Data Rate Maps", "hex_avg_capacity_original_allocation.pcl"))
mincapacityhexmap.to_pickle(os.path.join("data", "Data Rate Maps", "hex_min_capacity_original_allocation.pcl"))







































