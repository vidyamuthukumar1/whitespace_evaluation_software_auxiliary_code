from canada import DataMap2DCanada, BoundaryCanada, RegionCanadaTvOnly
from ruleset_industrycanada2015 import RulesetIndustryCanada2015
from population_canada import PopulationDataCanada2011
from data_aggregation import get_ccdf_from_datamap2D


from west.data_management import SpecificationDataMap, SpecificationRegionMap, SpecificationWhitespaceMap, SpecificationPopulationMap
from west.device import Device
from west.ruleset_fcc2012 import RulesetFcc2012
import west.data_manipulation

import os
import matplotlib.pyplot as plt

def subtraction_function(this_value, other_value):
    return this_value - other_value

datamap_spec = SpecificationDataMap(DataMap2DCanada, 200, 300)
regionmap_spec = SpecificationRegionMap(BoundaryCanada, datamap_spec)
region_map = regionmap_spec.fetch_data()
population_map_spec = SpecificationPopulationMap(regionmap_spec, PopulationDataCanada2011)
population_map = population_map_spec.fetch_data()


#Plotting whitespace map according to IC Ruleset
device = Device(is_portable=False, haat_meters=30)
whitespace_map_spec = SpecificationWhitespaceMap(regionmap_spec,
                                                 RegionCanadaTvOnly,
                                                 RulesetIndustryCanada2015, device)
print whitespace_map_spec.filename
is_whitespace_map_ic = whitespace_map_spec.fetch_data()
total_whitespace_channels_ic = is_whitespace_map_ic.sum_all_layers()

plot = total_whitespace_channels_ic.make_map(is_in_region_map=region_map)
plot.add_boundary_outlines(boundary=BoundaryCanada())
plot.set_boundary_color('k')
plot.set_boundary_linewidth('1')
plot.add_colorbar(vmin=0, vmax=50, label="Number of available WS channels")
plot.save(os.path.join("data", "FCC vs IC comparisons", "number_of_fixed_TVWS_channels_in_canada_under_ic_ruleset.png"))

#Plotting whitespace map according to FCC Ruleset
device = Device(is_portable=False, haat_meters=30)
whitespace_map_spec = SpecificationWhitespaceMap(regionmap_spec,
                                                 RegionCanadaTvOnly,
                                                 RulesetFcc2012, device)
print whitespace_map_spec.filename
is_whitespace_map_fcc = whitespace_map_spec.fetch_data()
total_whitespace_channels_fcc = is_whitespace_map_fcc.sum_all_layers()

plot = total_whitespace_channels_fcc.make_map(is_in_region_map=region_map)
plot.add_boundary_outlines(boundary=BoundaryCanada())
plot.set_boundary_color('k')
plot.set_boundary_linewidth('1')
plot.add_colorbar(vmin=0, vmax=50, label="Number of available WS channels")
plot.save(os.path.join("data", "FCC vs IC comparisons", "number_of_fixed_TVWS_channels_in_canada_under_fcc_ruleset.png"))

#Evaluating the difference map
diff_map = total_whitespace_channels_fcc.combine_datamaps_with_function(total_whitespace_channels_ic, subtraction_function)
plot = diff_map.make_map(is_in_region_map = region_map)
plot.add_boundary_outlines(boundary=BoundaryCanada())
plot.set_boundary_color('k')
plot.set_boundary_linewidth('1')
plot.add_colorbar(vmin = 0, vmax = 20, label = "Diff in available TVWS channels")
plot.save(os.path.join("data", "FCC vs IC comparisons", "number_of_fixed_TVWS_channels_in_canada_fcc_vs_ic_diff_map.png"))


#Code to get CCDFs

fcc_ccdf_by_population = west.data_manipulation.calculate_cdf_from_datamap2D(total_whitespace_channels_fcc, population_map, region_map)
fcc_ccdf_by_population[1] = 1 - fcc_ccdf_by_population
ic_ccdf_by_population = west.data_manipulation.calculate_cdf_from_datamap2D(total_whitespace_channels_ic, population_map, region_map)
ic_ccdf_by_population[1] = 1 - ic_ccdf_by_population

print fcc_ccdf_by_population
print ic_ccdf_by_population

plt.plot(fcc_ccdf_by_population[0], fcc_ccdf_by_population[1], 'b')
plt.plot(ic_ccdf_by_population[0], ic_ccdf_by_population[1], 'r')
plt.xlabel("TV Whitespace (Channels)")
plt.ylabel("CCDF")

plt.show()

fcc_ccdf_by_area = get_ccdf_from_datamap2D(total_whitespace_channels_fcc, region_map)

ic_ccdf_by_area = get_ccdf_from_datamap2D(total_whitespace_channels_ic, region_map)


print fcc_ccdf_by_area
print ic_ccdf_by_area

plt.plot(fcc_ccdf_by_area[0], fcc_ccdf_by_area[1], 'b')
plt.plot(ic_ccdf_by_area[0], ic_ccdf_by_area[1], 'r')
plt.xlabel("TV Whitespace (Channels)")
plt.ylabel("CCDF")
plt.xlim((0, 47))

plt.show()

#Code to get maps with separate kinds of TV stations
#TODO: Clean up all of this
"""def is_not_digital_filter_function(station):
    return not station.is_digital()

def is_digital_filter_function(station):
    return station.is_digital()

device = Device(is_portable = False, haat_meters = 30)
list_of_digital_tv_stations = r.get_protected_entities_of_type(west.protected_entities_tv_stations.ProtectedEntitiesTVStations)
print len(list_of_digital_tv_stations.stations())
list_of_digital_tv_stations.remove_entities(is_digital_filter_function)
print len(list_of_digital_tv_stations.stations())

list_of_digital_tv_stations = r.get_protected_entities_of_type(west.protected_entities_tv_stations.ProtectedEntitiesTVStations)
list_of_digital_tv_stations.remove_entities(is_digital_filter_function)
print len(list_of_digital_tv_stations.stations())

r.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, list_of_digital_tv_stations)
print len(r.get_protected_entities_of_type(west.protected_entities_tv_stations.ProtectedEntitiesTVStations).stations())
fcc_whitespace_map_spec = SpecificationWhitespaceMap(regionmap_spec,
                                                 r,
                                                 RulesetFcc2012, device)
print fcc_whitespace_map_spec.filename
is_whitespace_map = fcc_whitespace_map_spec.make_data()
fcc_total_whitespace_channels = is_whitespace_map.sum_all_layers()

ic_whitespace_map_spec = SpecificationWhitespaceMap(regionmap_spec,
                                                 r,
                                                 RulesetIndustryCanada2015, device)
print ic_whitespace_map_spec.filename
is_whitespace_map = ic_whitespace_map_spec.make_data()
ic_total_whitespace_channels = is_whitespace_map.sum_all_layers()

ic_total_whitespace_channels.to_pickle(os.path.join("data", "FCC vs IC comparisons", "canada_fixed_TVWS_under_ic_ruleset_map_total_only_digital_stations.pcl"))
fcc_total_whitespace_channels.to_pickle(os.path.join("data", "FCC vs IC comparisons", "canada_fixed_TVWS_under_fcc_ruleset_map_total_only_digital_stations.pcl"))


diff_map = fcc_total_whitespace_channels.combine_datamaps_with_function(ic_total_whitespace_channels, subtraction_function)

plot = diff_map.make_map(is_in_region_map = region_map)
plot.add_boundary_outlines(boundary=BoundaryCanada())
plot.set_boundary_color('k')
plot.set_boundary_linewidth('1')
plot.add_colorbar(vmin = 0, vmax = 20, label = "Diff in available TVWS channels - Only digital")
plot.save(os.path.join("data", "FCC vs IC comparisons", "number_of_fixed_TVWS_channels_in_canada_fcc_vs_ic_diff_map_only_digital.png"))"""