from west.data_management import SpecificationDataMap, SpecificationRegionMap, SpecificationWhitespaceMap, SpecificationPopulationMap
from west.boundary import BoundaryContinentalUnitedStates
from west.device import Device
from west.data_map import DataMap2DContinentalUnitedStates
import west.population
from west.ruleset_fcc2012 import RulesetFcc2012

from ruleset_industrycanada2015 import RulesetIndustryCanada2015
from hybrid_rulesets import *
from data_aggregation import get_ccdf_from_datamap2D
from population_canada import PopulationDataCanada2011
from australia_tvws import * #Comment out main evaluation before this step
from canada_tvws import * #Comment out main evaluation before this step
from population_australia import *

import matplotlib.pyplot as plt
import matplotlib.lines as mlines


####
#   UPDATE FUNCTION DEFINITIONS FOR DATAMAP2D
####

def subtraction_function(this_value, other_value):
    return this_value - other_value

def percentage_function(this_value, other_value):
    return float(this_value)/other_value * 100

def convert_channels_to_mhz_north_america(latitude, longitude, latitude_index, longitude_index, current_value):
    return 6 * current_value

def convert_channels_to_mhz_australia(latitude, longitude, latitude_index, longitude_index, current_value):
    return 7 * current_value

####
#   END OF UPDATE FUNCTION DEFINITIONS
####

####
#   FUNCTION DEFINITION FOR WHITESPACE EVALUATION
####

def evaluate_whitespace_for_region_and_ruleset(region_map_spec, device, region, ruleset):

    """Function that evaluates whitespace given a particular region, ruleset,
    device, and region map specification."""

    print "Evaluating whitespace for region and ruleset"

    whitespace_map_spec = SpecificationWhitespaceMap(region_map_spec,
                                                     region, ruleset,
                                                     device)

    is_whitespace_map = whitespace_map_spec.fetch_data()
    total_whitespace_channels = is_whitespace_map.sum_all_layers()
    return total_whitespace_channels

####
#   END OF FUNCTION DEFINITION
####

####
#   MAIN EVALUATION
####

#Type of whitespace device
device = Device(is_portable=False, haat_meters =30)

#Defining specification DataMap2Ds and region maps for US, Canada, and Australia.
data_map_us_spec = SpecificationDataMap(DataMap2DContinentalUnitedStates, 400, 600)
region_map_us_spec = SpecificationRegionMap(BoundaryContinentalUnitedStates, data_map_us_spec)
region_map_us = region_map_us_spec.fetch_data()
population_map_us_spec = SpecificationPopulationMap(region_map_us_spec, west.population.PopulationData)
population_map_us = population_map_us_spec.fetch_data()

data_map_canada_spec = SpecificationDataMap(DataMap2DCanada, 200, 300)
region_map_canada_spec = SpecificationRegionMap(BoundaryCanada, data_map_canada_spec)
region_map_canada = region_map_canada_spec.fetch_data()
population_map_canada_spec = SpecificationPopulationMap(region_map_canada_spec, PopulationDataCanada2011)
population_map_canada = population_map_canada_spec.fetch_data()

data_map_australia_spec = SpecificationDataMap(DataMap2DAustralia, 35*8, 45*8)
region_map_australia_spec = SpecificationRegionMap(BoundaryAustralia, data_map_australia_spec)
region_map_australia = region_map_australia_spec.fetch_data()
population_map_australia_spec = SpecificationPopulationMap(region_map_australia_spec, PopulationDataAustralia2006)
population_map_australia = population_map_australia_spec.fetch_data()

#Defining regions for US, Canada, and Australia.
region_us = RegionUnitedStatesWithUSAndCanadaStations()
region_canada = RegionCanadaWithUSAndCanadaStations()
region_australia = RegionAustraliaTvOnly()

#Defining all rulesets - FCC ruleset, IC ruleset, and hypothetical chimera rulesets.
ruleset_fcc = RulesetFcc2012()
ruleset_hybrid_1 = RulesetFcc2012WithIndustryCanada2015ProtectedContourRadii()
ruleset_hybrid_2 = RulesetIndustryCanada2015HybridTwo()
ruleset_hybrid_3 = RulesetIndustryCanada2015HybridThree()
ruleset_ic = RulesetIndustryCanada2015()
ruleset_fcc_modified_for_australia = RulesetFcc2012ModifiedForAustralia()

#WHITESPACE EVALUATION IN US, CANADA AND AUSTRALIA UNDER FCC AND IC RULESETS

us_map_fcc = evaluate_whitespace_for_region_and_ruleset(region_map_us_spec, device, region_us, ruleset_fcc)
us_map_ic = evaluate_whitespace_for_region_and_ruleset(region_map_us_spec, device, region_us, ruleset_ic)

canada_map_fcc = evaluate_whitespace_for_region_and_ruleset(region_map_canada_spec, device, region_canada, ruleset_fcc)
canada_map_ic = evaluate_whitespace_for_region_and_ruleset(region_map_canada_spec, device, region_canada, ruleset_ic)

australia_map_fcc = evaluate_whitespace_for_region_and_ruleset(region_map_australia_spec, device, region_australia, ruleset_fcc_modified_for_australia)
australia_map_ic = evaluate_whitespace_for_region_and_ruleset(region_map_australia_spec, device, region_australia, ruleset_ic)

#CCDFS FOR FCC AND IC

#Converting to MHz
us_map_fcc_mhz = west.data_map.DataMap2D.get_copy_of(us_map_fcc)
us_map_fcc_mhz.update_all_values_via_function(convert_channels_to_mhz_north_america)
us_map_ic_mhz = west.data_map.DataMap2D.get_copy_of(us_map_ic)
us_map_ic_mhz.update_all_values_via_function(convert_channels_to_mhz_north_america)

canada_map_fcc_mhz = west.data_map.DataMap2D.get_copy_of(canada_map_fcc)
canada_map_fcc_mhz.update_all_values_via_function(convert_channels_to_mhz_north_america)
canada_map_ic_mhz = west.data_map.DataMap2D.get_copy_of(canada_map_ic)
canada_map_ic_mhz.update_all_values_via_function(convert_channels_to_mhz_north_america)

australia_map_fcc_mhz = west.data_map.DataMap2D.get_copy_of(australia_map_fcc)
australia_map_fcc_mhz.update_all_values_via_function(convert_channels_to_mhz_australia)
australia_map_ic_mhz = west.data_map.DataMap2D.get_copy_of(australia_map_ic)
australia_map_ic_mhz.update_all_values_via_function(convert_channels_to_mhz_australia)

#Actually getting CCDFs
us_fcc_ccdf_pop = get_ccdf_from_datamap2D(us_map_fcc_mhz, region_map_us, population_map_us)
us_ic_ccdf_pop = get_ccdf_from_datamap2D(us_map_ic_mhz, region_map_us, population_map_us)
canada_fcc_ccdf_pop = get_ccdf_from_datamap2D(canada_map_fcc_mhz, region_map_canada, population_map_canada)
canada_ic_ccdf_pop = get_ccdf_from_datamap2D(canada_map_ic_mhz, region_map_canada, population_map_canada)
australia_fcc_ccdf = get_ccdf_from_datamap2D(australia_map_fcc_mhz, region_map_australia, population_map_australia)
australia_ic_ccdf = get_ccdf_from_datamap2D(australia_map_ic_mhz, region_map_australia, population_map_australia)

#Plotting the CCDFs
plt.plot(us_fcc_ccdf_pop[0], us_fcc_ccdf_pop[1], 'b--', linewidth=1)
plt.plot(us_ic_ccdf_pop[0], us_ic_ccdf_pop[1], 'b', linewidth=1)
plt.plot(canada_fcc_ccdf_pop[0], canada_fcc_ccdf_pop[1], 'r--', linewidth=1)
plt.plot(canada_ic_ccdf_pop[0], canada_ic_ccdf_pop[1], 'r', linewidth=1)
plt.plot(australia_fcc_ccdf[0], australia_ic_ccdf[1], 'g--', linewidth=1)
plt.plot(australia_ic_ccdf[0], australia_ic_ccdf[1], 'g', linewidth=1)

plt.xlim((0, 51*7))
plt.ylim((0, 1))
plt.xlabel("Available Whitespace (MHz)")
plt.ylabel("Fraction of population")

greenline = mlines.Line2D([], [], color = 'blue', linewidth = 1, label = 'United States')
redline = mlines.Line2D([], [], color = 'red', linewidth = 1, label = 'Canada')
blueline = mlines.Line2D([], [], color = 'green', linewidth = 1, label = 'Australia')

blacksolidline = mlines.Line2D([], [], color = 'black', linewidth = 1, label = 'IC ruleset')
blackdashline = mlines.Line2D([], [], color = 'black', linestyle = '--', label = 'FCC ruleset')

l1 = plt.legend(handles = [greenline, redline, blueline])
l2 = plt.legend(loc=(0.67, 0.63), handles = [blacksolidline, blackdashline])
plt.gca().add_artist(l1)

plt.grid(True, linestyle = '--', alpha = 0.5)
plt.savefig("data/FCC vs IC comparisons/all_ccdfs_by_population_mhz_with_australia.png")
plt.show()

#WHITESPACE EVALUATION FOR CHIMERA RULESETS
#Note: From here on, we only consider the US and Canada.

#Evaluating whitespace data maps and difference data maps.
#Canada
canada_map_h1 = evaluate_whitespace_for_region_and_ruleset(region_map_canada_spec, device, region_canada, ruleset_hybrid_1)
canada_map_h2 = evaluate_whitespace_for_region_and_ruleset(region_map_canada_spec, device, region_canada, ruleset_hybrid_2)
canada_map_h3 = evaluate_whitespace_for_region_and_ruleset(region_map_canada_spec, device, region_canada, ruleset_hybrid_3)

h1minusfcc_canada = canada_map_fcc.combine_datamaps_with_function(canada_map_h1, subtraction_function) #Shows us difference made by increased protected contour radii
h1minush2_canada = canada_map_h1.combine_datamaps_with_function(canada_map_h2, subtraction_function) #Shows us difference made by increased sep distances
h2minush3_canada = canada_map_h2.combine_datamaps_with_function(canada_map_h3, subtraction_function) #Shows us difference made by taboo channels
h3minusic_canada = canada_map_h3.combine_datamaps_with_function(canada_map_ic, subtraction_function) #Shows us difference made by far side sep distances

#US
us_map_h1 = evaluate_whitespace_for_region_and_ruleset(region_map_us_spec, device, region_us, ruleset_hybrid_1)
us_map_h2 = evaluate_whitespace_for_region_and_ruleset(region_map_us_spec, device, region_us, ruleset_hybrid_2)
us_map_h3 = evaluate_whitespace_for_region_and_ruleset(region_map_us_spec, device, region_us, ruleset_hybrid_3)

h1minusfcc_us = us_map_fcc.combine_datamaps_with_function(us_map_h1, subtraction_function) #Shows us difference made by increased protected contour radii
h1minush2_us = us_map_h1.combine_datamaps_with_function(us_map_h2, subtraction_function) #Shows us difference made by increased sep distances
h2minush3_us = us_map_h2.combine_datamaps_with_function(us_map_h3, subtraction_function) #Shows us difference made by taboo channels
h3minusic_us = us_map_h3.combine_datamaps_with_function(us_map_ic, subtraction_function) #Shows us difference made by far side sep distances


#Get percentage diff CCDFs

#Canada
h1minusfcc_canada_percentage = h1minusfcc_canada.combine_datamaps_with_function(canada_map_fcc, percentage_function)
h1minush2_canada_percentage = h1minush2_canada.combine_datamaps_with_function(canada_map_h1, percentage_function)
h2minush3_canada_percentage = h2minush3_canada.combine_datamaps_with_function(canada_map_h2, percentage_function)
h3minusic_canada_percentage = h3minusic_canada.combine_datamaps_with_function(canada_map_h3, percentage_function)

canada_h1minusfcc_perc_ccdf = get_ccdf_from_datamap2D(h1minusfcc_canada_percentage, region_map_canada, population_map_canada)
canada_h1minush2_perc_ccdf = get_ccdf_from_datamap2D(h1minush2_canada_percentage, region_map_canada, population_map_canada)
canada_h2minush3_perc_ccdf = get_ccdf_from_datamap2D(h2minush3_canada_percentage, region_map_canada, population_map_canada)
canada_h3minusic_perc_ccdf = get_ccdf_from_datamap2D(h3minusic_canada_percentage, region_map_canada, population_map_canada)

#Plotting
plt.plot(canada_h1minusfcc_perc_ccdf[0], canada_h1minusfcc_perc_ccdf[1], 'b')
plt.plot(canada_h1minush2_perc_ccdf[0], canada_h1minush2_perc_ccdf[1], 'g')
plt.plot(canada_h2minush3_perc_ccdf[0], canada_h2minush3_perc_ccdf[1], 'r')
plt.plot(canada_h3minusic_perc_ccdf[0], canada_h3minusic_perc_ccdf[1], 'm')
plt.xlim((-25, 100))

plt.xlabel("Percentage difference in whitespace")
plt.ylabel("Fraction of population")
blueline = mlines.Line2D([], [], color = 'blue', label = 'Protected contour definition')
greenline = mlines.Line2D([], [], color = 'green', label = 'Separation distances')
redline = mlines.Line2D([], [], color = 'red', label = 'Taboo channels')
magentaline = mlines.Line2D([], [], color = 'magenta', label = 'Far-side separation distances')
plt.legend(handles = [blueline, greenline, redline, magentaline])
plt.grid(True, linestyle = '--', alpha = 0.5)
plt.savefig("data/FCC vs IC comparisons/percentage_diff_whitespace_ccdfs_canada.png")

plt.show()

#US
h1minusfcc_us_percentage = h1minusfcc_us.combine_datamaps_with_function(us_map_fcc, percentage_function)
h1minush2_us_percentage = h1minush2_us.combine_datamaps_with_function(us_map_h1, percentage_function)
h2minush3_us_percentage = h2minush3_us.combine_datamaps_with_function(us_map_h2, percentage_function)
h3minusic_us_percentage = h3minusic_us.combine_datamaps_with_function(us_map_h3, percentage_function)

us_h1minusfcc_perc_ccdf = get_ccdf_from_datamap2D(h1minusfcc_us_percentage, region_map_us, population_map_us)
us_h1minush2_perc_ccdf = get_ccdf_from_datamap2D(h1minush2_us_percentage, region_map_us, population_map_us)
us_h2minush3_perc_ccdf = get_ccdf_from_datamap2D(h2minush3_us_percentage, region_map_us, population_map_us)
us_h3minusic_perc_ccdf = get_ccdf_from_datamap2D(h3minusic_us_percentage, region_map_us, population_map_us)

#Plotting
plt.plot(us_h1minusfcc_perc_ccdf[0], us_h1minusfcc_perc_ccdf[1], 'b')
plt.plot(us_h1minush2_perc_ccdf[0], us_h1minush2_perc_ccdf[1], 'g')
plt.plot(us_h2minush3_perc_ccdf[0], us_h2minush3_perc_ccdf[1], 'r')
plt.plot(us_h3minusic_perc_ccdf[0], us_h3minusic_perc_ccdf[1], 'm')
plt.xlim((-25, 100))

plt.xlabel("Percentage difference in whitespace")
plt.ylabel("Fraction of population")
blueline = mlines.Line2D([], [], color = 'blue', label = 'Protected contour definition')
greenline = mlines.Line2D([], [], color = 'green', label = 'Separation distances')
redline = mlines.Line2D([], [], color = 'red', label = 'Taboo channels')
magentaline = mlines.Line2D([], [], color = 'magenta', label = 'Far-side separation distances')
plt.legend(handles = [blueline, greenline, redline, magentaline])
plt.grid(True, linestyle = '--', alpha = 0.5)
plt.savefig("data/FCC vs IC comparisons/percentage_diff_whitespace_ccdfs_us.png")

plt.show()

####
#   END OF MAIN EVALUATION
####










