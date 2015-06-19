import west.data_map
import west.data_management
import west.data_manipulation
import west.population
from west.boundary import BoundaryContinentalUnitedStatesWithStateBoundaries
import os
import numpy
import matplotlib.cm
import matplotlib.pyplot as plt

def plot_binary_map(datamap, is_in_region_map, cmin = 0, cmax = 1):
    new_map = datamap.make_map(is_in_region_map = is_in_region_map)
    new_map.add_boundary_outlines(BoundaryContinentalUnitedStatesWithStateBoundaries())
    cmap = matplotlib.cm.Reds
    #cmap = matplotlib.cm.jet
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


def create_maps_of_zerows_for_band_plan(num_channels_removed, number_of_repacks, calculate_probability = False):

    def check_for_zeros(latitude, longitude, latitude_index, longitude_index, current_value):
        if current_value == 0:
            return 1
        return 0

    def check_for_ones(latitude, longitude, latitude_index, longitude_index, current_value):
        if current_value == 1:
            return 1
        return 0

    def or_function(this_value, other_value):
        return numpy.logical_or(this_value, other_value)

    def sum_function(this_value, other_value):
        return this_value + other_value

    zerows_map = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)
    zerows_map.reset_all_values(0)
    onews_map = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)
    onews_map.reset_all_values(0)
    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    population_map_spec = west.data_management.SpecificationPopulationMap(is_in_region_map_spec, west.population.PopulationData)
    population_map = population_map_spec.fetch_data()

    #fixed, total
    repack_file_list = os.listdir(os.path.join("data", "Pickled Files - Whitespace Maps", "A-%dChannelsRemoved"%num_channels_removed, "Portable - Only UHF"))
    repack_file_list = repack_file_list[1:]
    for i in range(number_of_repacks):
        #print i
        wsmap = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "Pickled Files - Whitespace Maps", "A-%dChannelsRemoved"%num_channels_removed, "Portable - Only UHF", repack_file_list[i]))
        wsmap_copy = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(wsmap)
        cdf = west.data_manipulation.calculate_cdf_from_datamap2d(wsmap, population_map, is_in_region_map)
        print "Median = ", cdf[3]
        #plot_binary_map(wsmap, is_in_region_map, cmin = 0, cmax = 50)
        wsmap.update_all_values_via_function(check_for_zeros)
        wsmap_copy.update_all_values_via_function(check_for_ones)

        countzero = 0
        for i in range(400):
            for j in range(600):
                if is_in_region_map.get_value_by_index(i, j) == 1 and wsmap.get_value_by_index(i, j) == 1:
                    countzero += 1
        print countzero
        #plot_binary_map(wsmap, is_in_region_map)

        if calculate_probability:
            zerows_map = zerows_map.combine_datamaps_with_function(wsmap, sum_function)
        else:
            zerows_map = zerows_map.combine_datamaps_with_function(wsmap, or_function)
        onews_map = onews_map.combine_datamaps_with_function(wsmap_copy, or_function)

    zero_and_one_map = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)
    zero_and_one_map.reset_all_values(0)
    for i in range(400):
        for j in range(600):
            if zerows_map.get_value_by_index(i, j):
                zero_and_one_map.set_value_by_index(i, j, 1.7)
            elif onews_map.get_value_by_index(i, j) == 1:
                zero_and_one_map.set_value_by_index(i, j, 0.2)
            else:
                zero_and_one_map.set_value_by_index(i, j, numpy.inf)

    """wsmap = west.data_map.DataMap2DContinentalUnitedStates.from_pickle("original_map_fcccontours_withplmrs_onlyuhf.pcl")
    cdf = west.data_manipulation.calculate_cdf_from_datamap2d(wsmap, population_map, is_in_region_map)
    print "Median = ", cdf[3]
    wsmap.update_all_values_via_function(check_for_zeros)"""

    populationzero = 0
    populationone = 0
    populationonlyone = 0
    for i in range(400):
        for j in range(600):
            if zerows_map.get_value_by_index(i, j) == 0:
                zerows_map.set_value_by_index(i, j, numpy.inf)
            if zerows_map.get_value_by_index(i, j) == 1 and is_in_region_map.get_value_by_index(i, j) == 1:
                populationzero += population_map.get_value_by_index(i, j)
            if onews_map.get_value_by_index(i, j) == 1 and is_in_region_map.get_value_by_index(i, j) == 1:
                populationone += population_map.get_value_by_index(i, j)
            if onews_map.get_value_by_index(i, j) == 1 and is_in_region_map.get_value_by_index(i, j) == 1 and zerows_map.get_value_by_index(i, j) == 0:
                populationonlyone += population_map.get_value_by_index(i, j)
    print populationzero, populationone, populationonlyone
    plot_binary_map(zerows_map, is_in_region_map, cmin = 0, cmax = 100)

def plot_acceleration_or_instantaneous_curves(number_of_repacks):
    def check_for_zeros(latitude, longitude, latitude_index, longitude_index, current_value):
        if current_value == 0:
            return 1
        return 0

    def or_function(this_value, other_value):
        return numpy.logical_or(this_value, other_value)

    def calculate_population_of_zerows(datamap, populationmap):
        population = 0
        for i in range(400):
            for j in range(600):
                if datamap.get_value_by_index(i, j) == 1:
                    population += populationmap.get_value_by_index(i, j)
        return population


    colors = {7: 'b', 14: 'r', 22: 'g', 25: 'm'}


    for num_channels_removed in [25]:
        zerows_map = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)
        zerows_map.reset_all_values(0)

        datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
        is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
        is_in_region_map = is_in_region_map_spec.fetch_data()
        population_map_spec = west.data_management.SpecificationPopulationMap(is_in_region_map_spec, west.population.PopulationData)
        population_map = population_map_spec.fetch_data()

        instantaneous_values = numpy.zeros(number_of_repacks)
        acceleration_values = numpy.zeros(number_of_repacks)
        num_repacks_index  = numpy.arange(number_of_repacks)

        if num_channels_removed == 25:
            repack_file_list = os.listdir(os.path.join("data", "Pickled Files - Whitespace Maps", "A-%dChannelsRemoved"%num_channels_removed, "Only UHF"))
            repack_file_list = repack_file_list[1:]

        else:
            repack_file_list = []
            for i in range(number_of_repacks):
                repack_file_list.append("%dUHFnewUSMinimumStationstoRemove_OnlyUHF_PLMRS_FCCcontours%d.pcl"%(num_channels_removed, i))
        for i in range(number_of_repacks):
            print i
            print repack_file_list[i]
            if num_channels_removed == 25:
                wsmap = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "Pickled Files - Whitespace Maps", "A-%dChannelsRemoved"%num_channels_removed, "Only UHF", repack_file_list[i]))
            else:
                wsmap = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "Pickled Files - Whitespace Maps", "A-%dChannelsREmoved"%num_channels_removed, repack_file_list[i]))
            wsmap.update_all_values_via_function(check_for_zeros)
            zerows_map = zerows_map.combine_datamaps_with_function(wsmap, or_function)

            instantaneous_values[i] = calculate_population_of_zerows(wsmap, population_map)
            acceleration_values[i] = calculate_population_of_zerows(zerows_map, population_map)

            print instantaneous_values[i], acceleration_values[i]


        from scipy.stats import cumfreq
        num_bins = 100
        inst_values_cdf = cumfreq(instantaneous_values, num_bins)
        xaxis = numpy.linspace(0, max(instantaneous_values), num_bins)
        plt.plot(xaxis, inst_values_cdf[0]/number_of_repacks)

    plt.xlabel("Population that sees zero whitespace after repack")
    plt.ylabel("CDF")
    plt.show()


def create_variance_zerows_map(num_channels_removed, number_of_repacks):
    def check_for_zeros(latitude, longitude, latitude_index, longitude_index, current_value):
        if current_value == 0:
            return 1
        return 0

    def set_zeros_to_inf(latitude, longitude, latitude_index, longitude_index, current_value):
        if current_value == 0:
            return numpy.inf
        return current_value


    def or_function(this_value, other_value):
        return numpy.logical_or(this_value, other_value)

    def stddev_function(latitude, longitude, latitude_index, longitude_index, list_of_values_in_order):
        return numpy.std(list_of_values_in_order)

    def total_or_function(latitude, longitude, latitude_index, longitude_index, list_of_values_in_order):
        if 1 in list_of_values_in_order:
            return 1
        return 0



    zerows_map = west.data_map.DataMap2DContinentalUnitedStates.create(400, 600)
    zerows_map.reset_all_values(0)
    zerows_map_3D = west.data_map.DataMap3D.from_DataMap2D(zerows_map, range(number_of_repacks))

    datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
    is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
    is_in_region_map = is_in_region_map_spec.fetch_data()
    population_map_spec = west.data_management.SpecificationPopulationMap(is_in_region_map_spec, west.population.PopulationData)
    population_map = population_map_spec.fetch_data()

    for i in range(number_of_repacks):
        print i
        zerows_map = west.data_map.DataMap2DContinentalUnitedStates.from_pickle(os.path.join("data", "Pickled Files - Whitespace Maps", "C-%dChannelsRemoved"%num_channels_removed, "%dVHFFreeUSMinimumStationstoRemove_OnlyRemainingChannels_PLMRS_FCCcontours%d.pcl"%(num_channels_removed, i)))
        zerows_map.update_all_values_via_function(check_for_zeros)
        zerows_map_3D.set_layer(i, zerows_map)
        zerows_map.update_all_values_via_function(set_zeros_to_inf)
        map = plot_binary_map(zerows_map, is_in_region_map, cmin = 0, cmax = 1)
        map.save(os.path.join("data", "For Kate - Washington", "%dchannelsremoved_fixed_totalWS%d.png"%(num_channels_removed, i)))

    stddev_map = zerows_map_3D.combine_values_elementwise_across_layers_using_function(stddev_function)
    zerows_map = zerows_map_3D.combine_values_elementwise_across_layers_using_function(total_or_function)

    for i in range(400):
        for j in range(600):
            if zerows_map.get_value_by_index(i, j) == 0:
                stddev_map.set_value_by_index(i, j, numpy.inf)

    map = plot_binary_map(stddev_map, is_in_region_map, cmin = 0, cmax = 1)












