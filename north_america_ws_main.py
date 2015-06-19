from west.ruleset_fcc2012 import RulesetFcc2012
from data_aggregation import plot_map_from_datamap2D
from west.data_management import *
from west.device import Device


from north_america_ws import *

#Main function to evaluate available whitespace across North America for the FCC and IC rulesets.

#Defining specifications for DataMap2D and region of North America.
data_map_spec = SpecificationDataMap(DataMap2DContinentalNorthAmerica, 800, 600)
region_map_spec = SpecificationRegionMap(BoundaryContinentalNorthAmerica, data_map_spec)
region_map = region_map_spec.fetch_data()

#Make sure region map looks good
"""plot = region_map.make_map(is_in_region_map=region_map)
plot.add_boundary_outlines(boundary=BoundaryContinentalNorthAmerica())
plot.set_boundary_color('k')
plot.set_boundary_linewidth('1')
plot.save("data/north_american_map.png")"""

#Defining rulesets and device
ruleset_fcc = RulesetFcc2012()
ruleset_ic = RulesetIndustryCanada2015()
device = Device(is_portable=False, haat_meters=30)

#Evaluating whitespace for FCC ruleset

def convert_channels_to_mhz(latitude, longitude, latitude_index, longitude_index, current_value):
    return 6 * current_value

whitespace_map_spec = SpecificationWhitespaceMap(region_map_spec,
                                                 RegionNorthAmericaTvOnly,
                                                 RulesetFcc2012, device)

whitespace_map_fcc = whitespace_map_spec.fetch_data().sum_all_layers()
whitespace_map_fcc.update_all_values_via_function(convert_channels_to_mhz)
whitespace_map_fcc.mutable_matrix = 6 * whitespace_map_fcc.mutable_matrix

map_ws_fcc = plot_map_from_datamap2D(whitespace_map_fcc, region_map, cmin = 0, cmax = 50*6, colorbar_label = 'Available Whitespace (MHz)', boundary=BoundaryContinentalNorthAmerica(), colorbar_ticks = [0, 50, 100, 150, 200, 250, 300])
map_ws_fcc.save("data/North America maps/north_america_ws_fcc.png")

#Evaluating whitespace for IC ruleset

whitespace_map_spec = SpecificationWhitespaceMap(region_map_spec,
                                                 RegionNorthAmericaTvOnly,
                                                 RulesetIndustryCanada2015, device)
whitespace_map_ic = whitespace_map_spec.fetch_data().sum_all_layers()
whitespace_map_ic.update_all_values_via_function(convert_channels_to_mhz)
map_ws_ic = plot_map_from_datamap2D(whitespace_map_ic, region_map, cmin = 0, cmax = 50*6, colorbar_label = 'Available Whitespace (MHz)', boundary=BoundaryContinentalNorthAmerica(), colorbar_ticks = [0, 50, 100, 150, 200, 250, 300])
map_ws_ic.save("data/North America maps/north_america_ws_ic.png")
