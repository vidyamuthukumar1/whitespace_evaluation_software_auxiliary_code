from population_canada import PopulationDataCanada2011
from canada import DataMap2DCanada, BoundaryCanada
from west.data_management import SpecificationDataMap, SpecificationRegionMap


###
# Code block to create a population map of Canada based on population data from Statistics Canada.
###

pop_data = PopulationDataCanada2011()

datamap_spec = SpecificationDataMap(DataMap2DCanada, 200, 300)
region_map_spec = SpecificationRegionMap(BoundaryCanada, datamap_spec)
region_map = region_map_spec.fetch_data()
population_datamap = pop_data.create_population_map(region_map)

population_map = population_datamap.make_map(transformation = "log", is_in_region_map = region_map)
population_map.add_boundary_outlines(boundary=BoundaryCanada())
population_map.set_boundary_color('k')
population_map.set_boundary_linewidth('1')
population_map.blocking_show()

