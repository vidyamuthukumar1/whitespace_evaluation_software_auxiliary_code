from evaluate_multiple_assignments import Assignment, Repack, AssignmentType, RepackType, DeviceSpecification, PLMRSExclusions, WhitespaceEvaluationType, QuantityToPlot, StatisticalMetricToPlot

import west.data_manipulation
import west.data_map
from west.boundary import BoundaryContinentalUnitedStatesWithStateBoundaries
from west.map import Map

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import os
import csv
import numpy



def plot_map_from_datamap2D(datamap, is_in_region_map = None, transformation = "linear", boundary = BoundaryContinentalUnitedStatesWithStateBoundaries(), boundary_color = 'black', boundary_linewidth = 1, use_colorbar = True, colorbar_label = None, colorbar_ticks = [0, 10, 20, 30, 40, 50], colormap = cm.jet, set_below_zero_color = 'black', cmin = 0, cmax = 50):
    """Plots a map of a given DataMap2D given input parameters."""


    if cmin >= cmax:
        raise ValueError("Invalid limits set on colormap. Please check inputs.")

    if transformation == 'log':
        for i in range(400):
            for j in range(600):
                if datamap.get_value_by_index(i, j) <= 0:
                    raise ValueError("Cannot apply log transformation for given DataMap2D.")


    map = Map(datamap, transformation = transformation, is_in_region_map = is_in_region_map)

    colormap.set_under(set_below_zero_color)
    map._image.set_cmap(colormap) #Hack-y, suggest changing this to Kate
    map._image.set_clim(cmin, cmax)


    if use_colorbar == True:
        map.add_colorbar(decimal_precision = 0, label = colorbar_label, vmin = cmin, vmax = cmax)
        map.set_colorbar_ticks(colorbar_ticks)


    if boundary is not None:
        map.add_boundary_outlines(boundary)
        map.set_boundary_color(boundary_color)
        map.set_boundary_linewidth(boundary_linewidth)
        map.make_region_background_white(is_in_region_map)
    return map

def make_loss_map(original_assignment, new_assignment, statistical_metric_to_plot = None):
    """Makes a loss map for a particular assignment and bandplan. Note: assignment.bandplans will only contain one set of channels removed."""

    if original_assignment.region_map_spec != new_assignment.region_map_spec:
        raise ValueError("Assignments may not correspond to same region. Please check.")


    def subtraction_function(this_value, other_value):
        return this_value - other_value


    original_datamap = original_assignment.fetch_data()
    if new_assignment.type in [AssignmentType.chopofftop, AssignmentType.original]:
        new_datamap = new_assignment.fetch_data()
    elif new_assignment.type == AssignmentType.repack:
        if statistical_metric_to_plot is not None and new_assignment.statistical_data_exists(QuantityToPlot.tv, statistical_metric_to_plot):
            new_datamap = new_assignment.load_statistical_data(QuantityToPlot.tv, statistical_metric_to_plot)
        else:
            new_datamap = new_assignment.fetch_data()
    else:
        raise ValueError("Data does not exist for new assignment. Please check again.")

    loss_datamap = original_datamap.combine_datamaps_with_function(new_datamap, subtraction_function)

    loss_map = plot_map_from_datamap2D(loss_datamap, new_assignment.region_map, colorbar_label = "Lost TV channels", set_below_zero_color = 'grey', cmin = min(loss_datamap.mutable_matrix), cmax = max(loss_datamap.mutable_matrix))
    return loss_map

def get_ccdf_from_datamap2D(datamap, is_in_region_map, population_map):
    """Creates a plot object of the CCDF of a particular data map. Parameters such as linestyle, color, etc can be input."""

    ccdfX, ccdfY, mean, median = west.data_manipulation.calculate_cdf_from_datamap2d(datamap, population_map, is_in_region_map)
    ccdfY = 1 - ccdfY
    #plt_object = ax.plot(ccdfX, ccdfY, color = color, linestyle = linestyle)
    return ccdfX, ccdfY

def plot_ccdfs_for_set_of_bandplans(assignment, quantity_to_plot, statistical_metric, is_in_region_map, population_map, color_code = ['blue', 'red', 'green', 'cyan', 'magenta', 'yellow'], linestyle = '-'):
    """Plots CCDFs for a set of band plans achieved either by repacking or chopping-off-the-top, all on the same figure.
    These CCDFs are plotted versus the original assignment. We may be plotting whitespace or TV viewership CCDFs."""

    if len(assignment.bandplans) > len(color_code):
        raise Warning("Some plots will have the same color and/or plot will look messy. Please enter a bigger set of colorcodes to fix this problem.")

    """Need to finish writing this. It is a little painful in terms of matplotlib nitty gritties."""


def plot_tadpole_for_given_bandplan(repack_assignment, xaxis_assignment, population_map, num_repacks_considered, all_fids_considered_in_auction = None):
    """Plots a tadpole for a given band plan and considering a certain number of repacks. Some points to note:
    1. We can plot the tadpoles for either whitespace or TV.
    2. We can plot repack assignment versus either original assignment or chop-off-top assignment.
    3. repack_assignment as well as xaxis_assignment should consider only one bandplan. The bandplans should be identical if we are comparing repack to chop-off-top."""

    def logical_or(latitude, longitude, latitude_index, longitude_index, list_of_values_in_order):
        if 1 in list_of_values_in_order:
            return 1
        else:
            return 0

    if xaxis_assignment.type_object == AssignmentType.repack or repack_assignment.type_object != AssignmentType.repack:
        raise InputError("We want to compare a repack against chopping off the top or original assignment. Please check your input.")

    if xaxis_assignment.type_object == AssignmentType.chopofftop and xaxis_assignment.bandplan != repack_assignment.bandplan:
        raise InputError("Cannot compare different bandplans. Please check your input.")

    if xaxis_assignment.region_map_spec != repack_assignment.region_map_spec:
        raise ValueError("Assignments may not correspond to same region. Please check your input.")

    test_list = range(num_repacks_considered)

    original_map = xaxis_assignment.fetch_data()
    is_in_region_map = xaxis_assignment.region_map_spec.fetch_data()

    image_matrix_3D = numpy.zeros((num_repacks_considered, 51, 51)) #Make this generalized with len(tvws_channel_list) perhaps?
    starting_map = west.data_map.DataMap2D.from_specification((0, 51), (0, 51), 51, 51)
    starting_map.reset_all_values(0)
    mask3D = west.data_map.DataMap3D.from_DataMap2D(starting_map, test_list)

    for count in test_list:
        #print count
        repack_assignment.set_repack_index(count)
        #repack_assignment.set_region(all_fids_considered_in_auction)
        new_map = repack_assignment.fetch_data()
        for i in range(400):
            for j in range(600):
                if is_in_region_map.get_value_by_index(i, j) != 0:
                    mask3D.get_layer(count).set_value_by_index(new_map.get_value_by_index(i, j), original_map.get_value_by_index(i, j), 1)
                    image_matrix_3D[count][int(new_map.get_value_by_index(i, j))][int(original_map.get_value_by_index(i,j))] = image_matrix_3D[count][int(new_map.get_value_by_index(i, j))][int(original_map.get_value_by_index(i,j))] + population_map.get_value_by_index(i,j)


    image_matrix = numpy.sum(image_matrix_3D, axis = 0)/(max(test_list) - min(test_list) + 1)
    mask = mask3D.combine_values_elementwise_across_layers_using_function(logical_or, layer_descr_list = test_list)

    for i in range(51):
        for j in range(51):
            if mask.get_value_by_index(i, j) == 0:
                image_matrix[i][j] = numpy.inf
            else:
                image_matrix[i][j] = numpy.log(1 + image_matrix[i][j])/numpy.log(10)

    cmap = cm.jet
    cmap.set_over('white')
    fig = plt.figure(figsize = (11.5, 11.5))
    ax = fig.add_subplot(111)
    ax.imshow(image_matrix, cmap = cmap, vmin = 0, vmax = 8, interpolation = 'nearest')
    return fig

#Still need to incorporate extra parameters in this plot.

def plot_pareto_curves(repack_type, bandplans, statistical_metric, include_chopofftop = True):
    """Plot Pareto curves for a particular type of repack."""

    pareto_data_ws_fixed = {}
    pareto_data_ws_portable = {}
    pareto_data_ws_chopofftop_fixed = {}
    pareto_data_ws_chopofftop_portable = {}
    pareto_data_tv = {}
    pareto_data_tv_chopofftop = {}
    lte_data = []

    for b in bandplans:
        lte_data.append(6 * b)
        pareto_data_ws_fixed[b] = []
        pareto_data_ws_portable[b] = []
        pareto_data_tv[b] = []

    if statistical_metric == StatisticalMetricToPlot.mean:
        entry_index = 5
    elif statistical_metric == StatisticalMetricToPlot.median:
        entry_index = 6

    with open(os.path.join("data", "pareto_curve_data_ws.csv"), 'r') as f:
        reader = csv.reader(f)
        ind = 0
        for entry in reader:
            ind = ind + 1
            if ind == 1:
                continue
            #print entry
            if include_chopofftop:
                if entry[0] == 'AssignmentType.chopofftop':
                    #print "Appending entry  %f"%float(entry[entry_index])
                    #print pareto_data_ws_chopofftop_fixed
                    pareto_data_ws_chopofftop_fixed[int(entry[2])] = float(entry[entry_index])

            if entry[0] != 'AssignmentType.repack':
                continue
            if entry[1] != repack_type.name:
                continue
            #print "Appending entry %f" %float(entry[entry_index])
            pareto_data_ws_fixed[int(entry[2])].append(float(entry[entry_index]))

    with open(os.path.join("data", "pareto_curve_data_ws_portable.csv"), 'r') as f:
        reader = csv.reader(f)
        ind = 0
        for entry in reader:
            ind = ind + 1
            if ind == 1:
                print "Skipping empty row"
                continue
            print entry
            if include_chopofftop:
                if entry[0] == 'AssignmentType.chopofftop':
                    pareto_data_ws_chopofftop_portable[int(entry[2])] = float(entry[entry_index])

            if entry[0] != 'AssignmentType.repack':
                print "Not of type repack or chopofftop"
                continue
            if entry[1] != repack_type.name:
                print "Not of repack type C"
                continue

            print "Appending portable entry %f" %float(entry[entry_index])
            pareto_data_ws_portable[int(entry[2])].append(float(entry[entry_index]))

    with open(os.path.join("data", "pareto_curve_data_tv.csv"), 'r') as f:
        reader = csv.reader(f)
        ind = 0
        for entry in reader:
            ind = ind + 1
            if ind == 1:
                continue
            if include_chopofftop:
                if entry[0] == 'AssignmentType.chopofftop':
                    pareto_data_tv_chopofftop[int(entry[2])] = float(entry[entry_index])

            if entry[0] != 'AssignmentType.repack':
                continue
            if entry[1] != repack_type.name:
                continue
            pareto_data_tv[int(entry[2])].append(float(entry[entry_index]))

    for b in bandplans:
        if statistical_metric == StatisticalMetricToPlot.mean:
            pareto_data_ws_chopofftop_portable[b] = numpy.mean(pareto_data_ws_chopofftop_portable[b])
            pareto_data_ws_chopofftop_fixed[b] = numpy.mean(pareto_data_ws_chopofftop_fixed[b])
            pareto_data_ws_portable[b] = numpy.mean(pareto_data_ws_portable[b])
            pareto_data_ws_fixed[b] = numpy.mean(pareto_data_ws_fixed[b])
            pareto_data_tv_chopofftop[b] = numpy.mean(pareto_data_tv_chopofftop[b])
            pareto_data_tv[b] = numpy.mean(pareto_data_tv[b])
        elif statistical_metric == StatisticalMetricToPlot.median:
            pareto_data_ws_chopofftop_portable[b] = numpy.median(pareto_data_ws_chopofftop_portable[b])
            pareto_data_ws_chopofftop_fixed[b] = numpy.median(pareto_data_ws_chopofftop_fixed[b])
            pareto_data_ws_portable[b] = numpy.median(pareto_data_ws_portable[b])
            pareto_data_ws_fixed[b] = numpy.median(pareto_data_ws_fixed[b])
            pareto_data_tv_chopofftop[b] = numpy.median(pareto_data_tv_chopofftop[b])
            pareto_data_tv[b] = numpy.median(pareto_data_tv[b])

    return pareto_data_tv, pareto_data_tv_chopofftop, pareto_data_ws_fixed, pareto_data_ws_chopofftop_fixed, pareto_data_ws_portable, pareto_data_ws_chopofftop_portable, lte_data

    #Note: Main plotting code has not been done yet.


def evaluate_zero_and_one_whitespace_map(assignment, repack_indices = None):
    """For a particular bandplan and a particular set of repacks, return the map that shows red wherever there is zero whitespace in ANY repack, and blue wherever there is one whitespace channel in ANY repack.
    This can be done for fixed or portable devices, and for total or UHF-only-whitespace."""

    if assignment.quantity_to_evaluate != QuantityToPlot.whitespace:
        raise InputError("We can only evaluate zero and one whitespace. Please check input.")

    if assignment.type != AssignmentType.repack or (assignment.type == AssignmentType.repack and repack_indices is None):
        repack_indices = [0]


    def evaluate_zero_and_one(this_value, other_value):
        if this_value == 'red': #Hard-code red into some color.
            return this_value
        if other_value == 0:
            return 'red'
        if other_value == 1:
            return 'blue'
        return this_value

    def set_zero_to_inf(latitude, longitude, latitude_index, longitude_index, current_value):
        if current_value == 0:
            return numpy.inf
        return current_value

    is_in_region_map = assignment.region_map_spec.fetch_data()

    zero_and_one_map = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(is_in_region_map)
    zero_and_one_map.reset_all_values(0)

    for i in repack_indices:
        if assignment.type == AssignmentType.repack:
            assignment.set_repack_index(i)
        repack_map = assignment.fetch_data()
        zero_and_one_map = zero_and_one_map.combine_datamaps_with_function(repack_map, evaluate_zero_and_one)

    zero_and_one_map.update_all_values_via_function(set_zero_to_inf)
    map = plot_map_from_datamap2D(zero_and_one_map, is_in_region_map, use_colorbar = False, colormap = cm.jet, cmin = 0, cmax = 3) #Check clims and colormap.
    return map


def evaluate_probability_of_zero_whitespace_map(repack_assignment, repack_indices):
    """For a particular bandplan and a particular set of repacks, return the map that shows the probability that there is zero whitespace after a repack."""

    if repack_assignment.quantity_to_evaluate != QuantityToPlot.whitespace:
        raise InputError("We can only evaluate zero and one whitespace. Please check input.")

    if repack_assignment.type != AssignmentType.repack:
        raise InputError("This evaluation makes sense only for repack assignments. Please revise input.")

    def zero_indicator(latitude, longitude, latitude_index, longitude_index, current_value):
        if current_value == 0:
            return 1
        else:
            return 0

    def addition_function(this_value, other_value):
        return this_value + other_value

    def set_zero_to_inf(latitude, longitude, latitude_index, longitude_index, current_value):
        if current_value == 0:
            return numpy.inf
        return current_value

    if repack_assignment.type != AssignmentType.repack:  #Might be restrictive if we want to do the same for chop-off-top or original assignment; consider removing.
        raise InputError("We can only consider repacks while making this plot. Please check your input.")

    is_in_region_map = repack_assignment.region_map_spec.fetch_data()
    probability_map = west.data_map.DataMap2DContinentalUnitedStates.get_copy_of(is_in_region_map)
    probability_map.reset_all_values(0)
    num_repacks_considered = repack_assignment.num_repacks_considered

    for i in repack_indices:
        repack_assignment.set_repack_index(i)
        repack_map = repack_assignment.fetch_data()
        repack_map.update_all_values_via_function(zero_indicator)
        probability_map = probability_map.combine_datamaps_with_function(repack_map, addition_function)

    probability_map.update_all_values_via_function(set_zero_to_inf)
    map = plot_map_from_datamap2D(probability_map, is_in_region_map, use_colorbar = False, colormap = cm.Reds, cmin = 0, cmax = num_repacks_considered)
    return map





"""To-dos:
Decide protected and public datatypes in assignment class.
Figure out how to handle plot objects in functions while returning, etc."""




















