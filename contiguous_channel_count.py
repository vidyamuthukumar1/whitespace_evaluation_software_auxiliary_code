from west.data_map_synthesis import *
from west.data_management import *
from west.data_map import *
from west.boundary import BoundaryContinentalUnitedStates, BoundaryContinentalUnitedStatesWithStateBoundaries
from west.region_united_states import RegionUnitedStates
import west.population
from west.ruleset_fcc2012 import RulesetFcc2012
from west.device import Device

from data_aggregation import get_ccdf_from_datamap2D

from canada import RegionUnitedStatesWithUSAndCanadaStations

test_device = Device(is_portable=False, haat_meters=30)
datamap_spec = SpecificationDataMap(DataMap2DContinentalUnitedStates, 400, 600)
region_map_spec = SpecificationRegionMap(BoundaryContinentalUnitedStates, datamap_spec)
is_whitespace_map_spec = SpecificationWhitespaceMap(region_map_spec,
                                                    RegionUnitedStatesWithUSAndCanadaStations,
                                                    RulesetFcc2012, test_device)

population_map_spec = SpecificationPopulationMap(region_map_spec, west.population.PopulationData)
population_map = population_map_spec.fetch_data()

region_map = region_map_spec.fetch_data()
is_whitespace_map = is_whitespace_map_spec.fetch_data()


length = len(is_whitespace_map.get_layer_descr_list())

def count_contiguous_channels(latitude, longitude, latitude_index,
                              longitude_index, tuple_of_values):
    is_whitespace_list, = tuple_of_values
    longest_run = 0
    current_run = 0
    for is_ws in is_whitespace_list:
        if is_ws:
            current_run += 1
        else:
            current_run = 0

        if current_run >= longest_run:
            longest_run = current_run

    return [longest_run] * length

contiguous_channel_map = synthesize_pixels_all_layers(
    count_contiguous_channels, (is_whitespace_map,))

contiguous_count = contiguous_channel_map.get_layer(2)

#Making maps for contiguous count
"""m = contiguous_count.make_map(is_in_region_map=region_map)
m.add_colorbar(vmin=0, vmax=50, label="Maximum # of contiguous channels")
m.save("data/FCC vs IC comparisons/Contiguous channel count (portable).png")


m_cut = contiguous_count.make_map(is_in_region_map=region_map)
m_cut.add_boundary_outlines(BoundaryContinentalUnitedStatesWithStateBoundaries())
m_cut.set_boundary_linewidth(1)
m_cut.add_colorbar(vmin=0, vmax=2, label="Maximum # of contiguous channels")
m_cut.save("data/FCC vs IC comparisons/Contiguous channel count (binary) (portable).png")"""

#Making CCDF for contiguous count
import matplotlib.pyplot as plt
ccdf = get_ccdf_from_datamap2D(contiguous_count, region_map, population_map)
plt.plot(ccdf[0], ccdf[1])
plt.xlabel("Maximum # of contiguous channels")
plt.ylabel("Fraction of population")
plt.grid(True, linestyle = '--', alpha = 0.5)
plt.savefig("data/FCC vs IC comparisons/contiguous_channel_count_ccdf.png")
plt.show()