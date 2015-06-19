import west.boundary
import west.data_management
import west.data_map
import west.device
import west.protected_entities_tv_stations
import west.region_united_states
import west.ruleset_fcc2012

import ruleset_industrycanada2015
import data_aggregation
from protected_entities_tv_stations_vidya import ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack

datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
region_map = region_map_spec.fetch_data()
population_map_spec = west.data_management.SpecificationPopulationMap(region_map_spec, west.population.PopulationData)
population_map = population_map_spec.fetch_data()

region_us = west.region_united_states.RegionUnitedStates()
ruleset_fcc = west.ruleset_fcc2012.RulesetFcc2012()
ruleset_canada = ruleset_industrycanada2015.RulesetIndustryCanada2015()

protected_entities_tv_stations = ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(region_us)
region_us.replace_protected_entities(west.protected_entities_tv_stations.ProtectedEntitiesTVStations, protected_entities_tv_stations)

tvws_channel_list = region_us.get_tvws_channel_list()
tvws_channel_list.append(3)
tvws_channel_list.append(4)
tvws_channel_list = sorted(tvws_channel_list)

device = west.device.Device(0, 30, 1)
#device = west.device.Device(1, 1, 1)

whitespace_map_us = west.data_map.DataMap3D.from_DataMap2D(region_map, tvws_channel_list)
whitespace_map_canada = west.data_map.DataMap3D.from_DataMap2D(region_map, tvws_channel_list)

#Applying TV exclusions
for c in tvws_channel_list:
    print "Channel %d"%c
    ruleset_fcc.apply_tv_exclusions_to_map(region_us, whitespace_map_us.get_layer(c),
                                           c, device)
    ruleset_canada.apply_tv_exclusions_to_map(region_us, whitespace_map_canada.get_layer(c), c, device)

total_whitespace_map_us = whitespace_map_us.sum_all_layers()
total_whitespace_map_canada = whitespace_map_canada.sum_all_layers()

map_us = data_aggregation.plot_map_from_datamap2D(total_whitespace_map_us, region_map, cmin = 0, cmax = 50, colorbar_label = "TV Whitespace Channels")
map_canada = data_aggregation.plot_map_from_datamap2D(total_whitespace_map_canada, region_map, cmin = 0, cmax = 50, colorbar_label = "TV Whitespace Channels")
map_us.blocking_show()
map_canada.blocking_show()

