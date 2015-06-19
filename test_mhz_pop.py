import west.device
import west.data_map
import west.data_management
import west.region_united_states
import west.region_united_states_vidya
import protected_entities_tv_stations_vidya, west.protected_entities_tv_stations
import west.helpers
import west.boundary
import west.data_manipulation
import west.ruleset_fcc2012
import numpy
import pickle
import west.boundary
import west.population
import os
import csv

resx = 400
resy = 600

def evaluate_population_of(datamap):
    population = 0
    for i in range(resx):
        for j in range(resy):
            if datamap.get_value_by_index(i, j) == 1 and is_in_region_map.get_value_by_index(i, j) == 1:
                population = population + population_map.get_value_by_index(i, j)

    return population

def not_function(latitude, longitude, latitude_index, longitude_index, current_value):
    return 1 - current_value


testreg = west.region_united_states.RegionUnitedStates()
boundary = west.boundary.BoundaryContinentalUnitedStatesWithStateBoundaries()
testruleset = west.ruleset_fcc2012.RulesetFcc2012()
bdr = west.boundary.BoundaryContinentalUnitedStates()

good_facility_ids = []
with open(os.path.join("data", "FromVijay", "C-All free", "C-15ChannelsRemoved", "15VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        good_facility_ids.append(row[0])

tvstationlist = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(testreg)
print len(tvstationlist.stations())
#tvstationlist.prune_data(good_facility_ids)

datamap_spec = west.data_management.SpecificationDataMap(west.data_map.DataMap2DContinentalUnitedStates, 400, 600)
is_in_region_map_spec = west.data_management.SpecificationRegionMap(west.boundary.BoundaryContinentalUnitedStates, datamap_spec)
is_in_region_map = is_in_region_map_spec.fetch_data()
population_map_spec = west.data_management.SpecificationPopulationMap(is_in_region_map_spec, west.population.PopulationData)
population_map = population_map_spec.fetch_data()

blankmap = is_in_region_map_spec.fetch_data()

with open("stamps_with_buffer=0km.pkl", 'r') as f:
    tvstation_submaps = pickle.load(f)


for stamp in tvstation_submaps.values():
    stamp[1].update_all_values_via_function(not_function)

populationlist = []

with open(os.path.join("data", "For Kate - Washington", "stations_mhz_pop.csv"), "w") as f:
    writer = csv.writer(f)
    count = 0
    for s in tvstationlist.stations():
        if s.get_facility_id() not in tvstation_submaps.keys():
            if boundary.location_inside_boundary(s.get_location()):
                print s.get_facility_id()
                raise KeyError("This station ought to be present. Please check.")
            else:
                continue
        print count
        blankmap.reset_all_values(0)
        try:
            blankmap.reintegrate_submap(tvstation_submaps[s.get_facility_id()][1], numpy.logical_or)
        except ValueError:
            print "Skipping facility ID %s as it is outside continental US"%s.get_facility_id()
        pop = evaluate_population_of(blankmap)
        populationlist.append(pop)
        writer.writerow([s.get_facility_id(), pop, tvstation_submaps[s.get_facility_id()][0]])
        count = count + 1

