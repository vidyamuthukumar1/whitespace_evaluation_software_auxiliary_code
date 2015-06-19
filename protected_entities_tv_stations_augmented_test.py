import protected_entities_tv_stations_vidya
import west.region_united_states

import unittest
import os
import csv

class ImplementRepackTestCase(unittest.TestCase):

    def setUp(self):
        self.region = west.region_united_states.RegionUnitedStates()
        self.tvws_channels = self.region.get_tvws_channel_list()
        self.tvws_channels.append(3)
        self.tvws_channels.append(4)
        self.stations = protected_entities_tv_stations_vidya.ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(self.region)

    def prune_data(self):
        good_facility_ids = []
        with open(os.path.join("data", "FromVijay", "C-All free", "C-0channelsRemoved", "0VHFFreeUSMinimumStationstoRemove0.csv"), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                good_facility_ids.append(row[0])

        self.stations.prune_data(good_facility_ids)

    def test_unique_facility_ids_no_stations_removed(self):
        self.prune_data()
        num_channels_removed = 0
        repack_index = "_test_unique_no_stations_removed"
        repack_filestringname = "VHFFreeUSMinimumStationstoRemove"

        reqd_stationlist = []
        with open(os.path.join("data", "FromVijay", "0VHFFreeUSMinimumStationstoRemove_test_unique_no_stations_removed.csv"), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                reqd_stationlist.append([row[0], int(row[1])])

        test_stationlist = self.stations.implement_repack(num_channels_removed, repack_index, repack_filestringname, self.tvws_channels)
        self.assertEqual(sorted(reqd_stationlist), sorted(test_stationlist))

        self.assertEqual(len(self.stations.stations()), len(reqd_stationlist))

        self.assertEqual(len(self.stations.stationdict.values()), len(self.stations.stations()))


        for s in self.stations.stations():
            self.assertEqual(s.get_channel(), self.stations.stationdict[s.get_facility_id()].get_channel())


    def test_unique_facility_ids_some_stations_removed(self):
        self.prune_data()
        num_channels_removed = 7
        repack_index = "_test_unique"
        num_station_removed = 69
        repack_filestringname = "UHFnewUSMinimumStationstoRemove"

        reqd_stationlist = []
        uhf_fids = []
        with open(os.path.join("data", "FromVijay", "7UHFnewUSMinimumStationstoRemove_test_unique.csv"), 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                uhf_fids.append(row[0])
                if row[1] == 'H':
                    continue
                reqd_stationlist.append([row[0], int(row[1])])

        for s in self.stations.stations():
            if s.get_facility_id() not in uhf_fids:
                reqd_stationlist.append([s.get_facility_id(), s.get_channel()])

        test_stationlist = self.stations.implement_repack(num_channels_removed, repack_index, repack_filestringname, self.tvws_channels)
        self.assertEqual(sorted(reqd_stationlist), sorted(test_stationlist))
        self.assertEqual(len(self.stations.stations()), 2173 - 69)

        self.assertEqual(len(self.stations.stations()), len(reqd_stationlist))
        self.assertEqual(len(self.stations.stations()), len(self.stations.stationdict.values()))

        for s in self.stations.stations():
            self.assertEqual(s.get_channel(), self.stations.stationdict[s.get_facility_id()].get_channel())

    def test_nonunique_facility_ids(self):
        #self.setUp()
        self.prune_data()
        num_channels_removed = 0
        repack_index = '_test_nonunique'
        repack_filestringname = "VHFFreeUSMinimumStationstoRemove"

        self.assertRaisesRegexp(ValueError, "Duplicate assignment present. Please check input file for errors.", self.stations.implement_repack, num_channels_removed, repack_index, repack_filestringname, self.tvws_channels)

    def test_unique_facility_ids_one_station_invalid_channel(self):
        #self.setUp()
        self.prune_data()
        num_channels_removed = 0
        repack_index = "_test_one_station_invalid_channel"
        repack_filestringname = "VHFFreeUSMinimumStationstoRemove"

        self.assertRaisesRegexp(ValueError, "Invalid TVWS channel in station-to-channel assignment. Please check input file for errors.", self.stations.implement_repack, num_channels_removed, repack_index, repack_filestringname, self.tvws_channels)

    def test_facility_id_not_existing(self):
        #self.setUp()
        self.prune_data()
        num_channels_removed = 0
        repack_index = "_test_invalid_facility_id"
        repack_filestringname = "VHFFreeUSMinimumStationstoRemove"

        self.assertRaisesRegexp(ValueError, "Invalid facility ID. Please check input file for errors.", self.stations.implement_repack, num_channels_removed, repack_index, repack_filestringname, self.tvws_channels)


    #One remaining test that may/may not need to be done: Do we want to test repacks that are done sequentially? This situation may not arise in general, because sequential repacks as an idea will not make sense. When using this code, we generally initialize the list of TV stations and implement a repack. All test cases have been taken care of here.





unittest.main()