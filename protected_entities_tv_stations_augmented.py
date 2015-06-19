from abc import abstractmethod
# from doc_inherit import doc_inherit
from west.protected_entities import ProtectedEntities
from west.protected_entities_tv_stations import ProtectedEntitiesTVStations, ProtectedEntitiesTVStationsUnitedStates, ProtectedEntitiesTVStationsUnitedStatesFromGoogle, ProtectedEntitiesTVStationsUnitedStatesIncentiveAuctionBaseline2014May20
from west.device import Device
import scipy
import os
import west.helpers
import csv
import random
import west.configuration
import numpy

class ProtectedEntitiesTVStationsUnitedStatesFromGoogle_Test2(ProtectedEntitiesTVStationsUnitedStates):
    def source_filename(self):
        base_directory = west.configuration.paths['UnitedStates']['protected_entities']
        return os.path.join(base_directory, 'FromGoogle', 'tv_us.csv')

    def source_name(self):
        return "Google TVWS database download [" \
               "http://www.google.com/get/spectrumdatabase/data/]"

    def _load_entities(self):
        """Example entry from Google's data:

        {'rcamsl_meters': '1348.1', 'application_id': '1297384', 'uid': 'KHMT',
        'erp_watts': '1000000.000', 'site_number': '0', 'parent_latitude': '',
        'entity_type': 'TV_US', 'keyhole_radius_meters': '',
        'antenna_rotation_degrees': '0.0', 'latitude': '45.739956',
        'tx_type': 'DT', 'channel': '22', 'parent_longitude': '',
        'facility_id': '47670', 'circle_radius_meters': '',
        'location_type': 'POINT', 'data_source': 'CDBS', 'rcagl_meters': '112.1',
        'geometry': '', 'longitude': '-108.139013', 'haat_meters': '247.5',
        'azimuth': '', 'antenna_id': '77895', 'parent_facility_id': '',
        'parent_callsign': ''}
        """

        self.log.debug("Loading TV stations from \"%s\" (%s)" % (str(self.source_filename()), str(self.source_name())))

        with open(self.source_filename(), 'r') as f:
            station_csv = csv.DictReader(f)
            for station in station_csv:

                tx_type = station['tx_type']

                # Skip distributed digital stations
                if tx_type in self.ignored_tv_types() or tx_type not in ['CA', 'DC', 'DT']:
                    continue


                try:
                    latitude = float(station['latitude'])
                    longitude = float(station['longitude'])
                    channel = int(station['channel'])
                    ERP = float(station['erp_watts'])
                    haat = float(station['haat_meters'])
                except Exception as e:
                    self.log.error("Error loading station: ", str(e))
                    continue

                new_station = ProtectedEntityTVStationWithFilterFunction(self, self.get_mutable_region(), latitude=latitude,
                                                       longitude=longitude, channel=channel, ERP_Watts=ERP,
                                                       HAAT_meters=haat, tx_type=tx_type)

                # Add optional information
                new_station.add_facility_id(station['facility_id'])
                new_station.add_callsign(station['uid'])

                self._add_entity(new_station)

class ProtectedEntitiesTVStationsUnitedStatesTVQuery_OriginalData(ProtectedEntitiesTVStationsUnitedStates):
    def _load_entities(self):
        """Example entry:

        ['', 'K02JU       ', '-         ', 'TX ', '2   ', 'DA  ', '                    ', '-  ', '-  ', 'LIC    ',
        'SELAWIK                  ', 'AK ', 'US ', 'BLTTV  -19800620IA  ', '0.018  kW ', '-         ', '0.0     ',
        '-       ', '11543      ', 'N ', '66 ', '35 ', '57.00 ', 'W ', '160 ', '0  ', '0.00  ',
        'CITY OF SELAWIK                                                             ', '   0.00 km ', '   0.00 mi ',
        '  0.00 deg ', '72.    m', 'H       ', '20773     ', '210.    ', '-       ', '0.      ', '21309     ', '-  ',
        '']

        Key: http://transition.fcc.gov/mb/audio/am_fm_tv_textlist_key.txt
        """

        #self.log.debug("Loading TV stations from \"%s\" (%s)" % "tvq_licensed_only.txt", str(self.source_name())))

        column_number = dict()
        column_number['callsign'] = 1
        column_number['tx_type'] = 3
        column_number['channel'] = 4
        column_number['country'] = 12
        column_number['ERP_kW'] = 14
        column_number['HAAT'] = 16
        column_number['facility_id'] = 18
        column_number['lat_dir'] = 19
        column_number['lat_deg'] = 20
        column_number['lat_min'] = 21
        column_number['lat_sec'] = 22
        column_number['lon_dir'] = 23
        column_number['lon_deg'] = 24
        column_number['lon_min'] = 25
        column_number['lon_sec'] = 26
        column_number['km_offset'] = 28

        def convert_dms_to_decimal(degrees, minutes, seconds):
            return degrees + minutes/60 + seconds/3600

        with open("/data/Region/UnitedStates/ProtectedEntities/tvq_licensed_only.txt", 'r') as f:
            station_csv = csv.reader(f, delimiter='|')

            for station_row in station_csv:
                # Skip blank rows
                if len(station_row) == 0:
                    continue

                try:
                    callsign = station_row[column_number['callsign']].strip()

                    # Skip "vacant" entries
                    if callsign in ['VACANT']:
                        continue

                    # Skip stations which are not in the US
                    if str.strip(station_row[column_number['country']]) in ["CA", "MX"]:
                        continue

                    tx_type = str.strip(station_row[column_number['tx_type']])

                    # The second list holds types which designate petitions
                    if tx_type in self.ignored_tv_types() or tx_type in ['DM', 'DR', 'DN']:
                        continue

                    channel = int(station_row[column_number['channel']])
                    # Skip stations that are outside the channel bounds
                    # See Q&A from 7/13/11 at
                    # http://www.fcc.gov/encyclopedia/white-space-database-administration-q-page:
                    #   "Database systems are not required to provide adjacent channel protection to legacy services
                    #    from the TV bands that are continuing to operate on channel 52."
                    if channel > 51:
                        continue

                    ERP_kW_string = station_row[column_number['ERP_kW']].split(" ")[0]
                    ERP_Watts = float(ERP_kW_string) * 1e3
                    # Skip stations with an ERP that is zero
                    # The FCC whitespace database administrators FAQ page
                    # (http://www.fcc.gov/encyclopedia/white-space-database-administration-q-page) mentions visual peak
                    # power and visual average power; however, these values are not present in the TV Query data.
                    if ERP_Watts < 0.001:
                        self.log.warning("Skipping station with 0 kW ERP; callsign: '%s'" % callsign)
                        continue

                    # Convert latitude
                    lat_dir = str.strip(station_row[column_number['lat_dir']])
                    lat_deg = float(station_row[column_number['lat_deg']])
                    lat_min = float(station_row[column_number['lat_min']])
                    lat_sec = float(station_row[column_number['lat_sec']])
                    if lat_dir in ['n', 'N']:
                        lat_sign = 1
                    elif lat_dir in ['s', 'S']:
                        lat_sign = -1
                    else:
                        self.log.error("Could not determine station latitude (direction: %s); skipping station with callsign %s" %
                                       (lat_dir, callsign))
                        print station_row
                        continue
                    latitude = lat_sign * convert_dms_to_decimal(lat_deg, lat_min, lat_sec)

                    # Convert longitude
                    lon_dir = str.strip(station_row[column_number['lon_dir']])
                    lon_deg = float(station_row[column_number['lon_deg']])
                    lon_min = float(station_row[column_number['lon_min']])
                    lon_sec = float(station_row[column_number['lon_sec']])
                    if lon_dir in ['e', 'E']:
                        lon_sign = 1
                    elif lon_dir in ['w', 'W']:
                        lon_sign = -1
                    else:
                        self.log.error("Could not determine station longitude (direction: %s); skipping station with callsign %s" %
                                       (lon_dir, callsign))
                        print station_row
                        continue
                    longitude = lon_sign * convert_dms_to_decimal(lon_deg, lon_min, lon_sec)

                    HAAT_meters = float(station_row[column_number['HAAT']])
                except Exception as e:
                    self.log.error("Error loading station: ", str(e))
                    continue

                # Create the station
                new_station = ProtectedEntityTVStation(self, self.get_mutable_region(), latitude=latitude,
                                                       longitude=longitude, channel=channel, ERP_Watts=ERP_Watts,
                                                       HAAT_meters=HAAT_meters, tx_type=tx_type)

                # Add optional information
                new_station.add_facility_id(station_row[column_number['facility_id']].strip())
                new_station.add_callsign(callsign)

                # Add it to the internal list
                self._add_entity(new_station)

class ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_PruneData(ProtectedEntitiesTVStationsUnitedStatesIncentiveAuctionBaseline2014May20):

    def source_filename(self):
        base_directory = west.configuration.paths['UnitedStates']['protected_entities']
        return os.path.join(base_directory, 'us_station_baseline_2014may20 - US Stations_withcorrections.csv')

    def get_station_dictionary_according_to_facility_id(self, good_facility_ids):
        count = 0
        #good_application_ids = ['1317477', '1275459', '1140624', '1276844', '1482575', '1331736', '623134', '1194833', '1291007', '1136652', '1252964', '1422438', '628839', '1293633', '1293629', '1326129']
        self.stationdict = {}
        for station in self.stations():
            if station.get_facility_id() not in good_facility_ids:
                continue
            count = count + 1
            #if station.get_tx_type() == 'DD' and station.get_app_id() not in good_application_ids:
                #continue
            self.stationdict[station.get_facility_id()] = station
            """if station.get_facility_id() not in self.stationdict.keys():
                self.stationdict[station.get_facility_id()] = station
            else:
                if station.get_erp_watts() > self.stationdict[station.get_facility_id()].get_erp_watts():
                    self.stationdict[station.get_facility_id()] = station"""


    def readd_stations_according_to_dictionary(self):
        self._entities = []
        for k in self.stationdict.keys():
            self._add_entity(self.stationdict[k])

    def prune_data(self, good_facility_ids):
        self.get_station_dictionary_according_to_facility_id(good_facility_ids)
        self.readd_stations_according_to_dictionary()
        self._refresh_cached_data()
        

class ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_PruneData):

    def ignored_tv_types(self):
        return ['LM']

    def full_repack_path(self, num_channels_removed, repack_index, filestringname): #Note: Need to reorganize Vijay's files to make this possible.
        return os.path.join("data", "FromVijay", "".join([str(num_channels_removed), filestringname, str(repack_index), ".csv"]))

    def write_to_csv(self, filename):
        with open(filename, 'w') as f:
            writer = csv.writer(f)
            for station in self.stations():
                writer.writerow([station.get_facility_id(), station.get_channel()])

    def implement_repack(self, num_channels_removed, repack_index, repack_filestringname, tvws_channels):
        def filter_function(station):
            if station.get_channel() == 'H':
                return False
            return True

        repack_file = self.full_repack_path(num_channels_removed, repack_index, repack_filestringname)

        return_stationlist = []
        list_of_valid_channels = []
        for c in tvws_channels:
            list_of_valid_channels.append(str(c))
        list_of_valid_channels.append('H')

        with open(repack_file, 'r') as f:
            stations_from_repack = csv.reader(f)
            print (stations_from_repack)
            ind = 0
            already_covered = {}
            for row in stations_from_repack:
                if len(row) == 0:
                    break
                ind = ind + 1
                f_id = row[0]
                channel = row[1]
                if str(channel) not in list_of_valid_channels:
                    print channel
                    raise ValueError ("Invalid TVWS channel in station-to-channel assignment. Please check input file for errors.")
                if f_id in already_covered.keys():
                    raise ValueError("Duplicate assignment present. Please check input file for errors.")
                try:
                    try:
                        channel = int(channel)
                        self.stationdict[f_id]._channel = channel
                    except ValueError:
                        self.stationdict[f_id]._channel = channel
                except KeyError:
                    raise ValueError("Invalid facility ID. Please check input file for errors.")
                already_covered[f_id] = channel

        self.readd_stations_according_to_dictionary()
        self.remove_entities(filter_function)
        print (len(self.stations()))
        self.stationdict = {}
        for s in self.stations():
            self.stationdict[s.get_facility_id()] = s
            return_stationlist.append([s.get_facility_id(), s.get_channel()])
        self._refresh_cached_data()
        return return_stationlist

    def permute_channels(self):
        """list_of_channels = self.stations_by_channel.keys()
        permuted_list_of_channels = list(numpy.random.permutation(52))
        permuted_list_of_channels.remove(0)
        permuted_list_of_channels.remove(1)
        print(len(permuted_list_of_channels))
        for k in self.stationdict.keys():
            c = self.stationdict[k].get_channel()
            print (c)
            self.stationdict[k]._channel = permuted_list_of_channels[c - 2]
        self.readd_stations_according_to_dictionary()
        self._refresh_cached_data()
        with open("permutation_list.csv", 'w') as f:
            writer = csv.writer(f)
            for s in self.stations():
                writer.writerow([s.get_facility_id(), s.get_channel()])"""
        with open("permutation_list.csv", 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                f_id = row[0]
                ch = int(row[1])
                self.stationdict[f_id]._channel = ch
            self.readd_stations_according_to_dictionary()
            self._refresh_cached_data()

    def modify_channels_at_random(self):
        channel_list = [3] + range(8, 13) + range(15, 36) + range(39, 51)
        for station in self.stations():
            station._channel = random.choice(channel_list)
        self._refresh_cached_data()

		
		
