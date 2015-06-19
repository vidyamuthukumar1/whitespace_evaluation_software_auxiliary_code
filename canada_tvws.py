import csv
import os
import simplekml

from west.region_united_states import RegionUnitedStates
from west.region import Region
from west.ruleset_fcc2012 import RulesetFcc2012
from west import boundary
from west import protected_entities_tv_stations
from west.protected_entities import ProtectedEntitiesDummy
from west.protected_entities_radio_astronomy_sites import ProtectedEntitiesRadioAstronomySites
from west.protected_entities_plmrs import ProtectedEntitiesPLMRS
from west.protected_entity_tv_station import ProtectedEntityTVStation
from west.data_map import DataMap2DWithFixedBoundingBox
from west.data_management import *
from west.device import Device

from protected_entities_tv_stations_augmented import ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack


####
#   CLASS DEFINITIONS
####

class BoundaryCanada(boundary.BoundaryShapefile):
    """
    :class:`Boundary` describing Canada.

    Data source:
    http://www.nws.noaa.gov/geodata/catalog/national/data/province.zip
    """
    def boundary_filename(self):
        return os.path.join("data", "Canada WS data", "province", "PROVINCE.SHP")

    def _geometry_name_field_str(self):
        return "NAME"


class ProtectedEntitiesTVStationsCanadaFromFccLearn(
    protected_entities_tv_stations.ProtectedEntitiesTVStations):
    """This class contains Canadian TV stations listed at
    http://data.fcc.gov/download/incentive-auctions/Constraint_Files/Canadian_Allotment_List_2014May20.xlsx

    Main website:
    http://data.fcc.gov/download/incentive-auctions/Constraint_Files/
    """

    def source_filename(self):
        return \
            "Canadian_Allotment_List_2014May20.xlsx - Canadian Allotments.csv"

    def source_name(self):
        return "FCC LEARN download [" \
               "http://data.fcc.gov/download/incentive-auctions/Constraint_Files/]"


    def _load_entities(self):
        """
        Example data:

        {'city': 'ASHMONT', 'erp': '26.7', 'service': 'TV',
        'facility_id': '1000001', 'country': 'CA', 'lon': '1113617',
        'app_id': '2000001', 'haat': '194', 'da': 'ND', 'rcamsl': '827.5',
        'state': 'AB', 'ant_id': '', 'arn': 'CANADA1',
        'fac_callsign': 'CFRN-TV-4', 'lat': '540807', 'ref az': '',
        'channel': '12'}

        """
        self.log.debug("Loading TV stations from \"%s\" (%s)" % (
            str(self.source_filename()), str(self.source_name())))

        def convert_dms_to_decimal(degrees, minutes, seconds):
            return degrees + minutes/60 + seconds/3600


        with open(os.path.join("data", "Canada WS data", self.source_filename()), 'r') as f:
            station_csv = csv.DictReader(f)
            for station in station_csv:

                tx_type = station['service']

                if tx_type in self.ignored_tv_types():
                    continue

                try:
                    # Lat/lon are in format DDDMMSS
                    lat_string = station['lat']
                    lat_sec = float(lat_string[-2:])
                    lat_min = float(lat_string[-4:-2])
                    lat_deg = float(lat_string[:-4])
                    latitude = convert_dms_to_decimal(lat_deg, lat_min, lat_sec)

                    lon_string = station['lon']
                    lon_sec = float(lon_string[-2:])
                    lon_min = float(lon_string[-4:-2])
                    lon_deg = float(lon_string[:-4])
                    longitude = convert_dms_to_decimal(lon_deg, lon_min,
                                                       lon_sec) * -1

                    channel = int(station['channel'])
                    ERP_Watts = float(station['erp']) * 1e3 # comes in kW
                    if ERP_Watts < 0.01:
                        self.log.warning("Skipping station with 0 W ERP: " +
                                         str(station))
                        continue
                    haat_meters = float(station['haat'])
                except Exception as e:
                    self.log.error("Error loading station: ", str(e))
                    continue

                new_station = ProtectedEntityTVStation(self,
                                                       self.get_mutable_region(),
                                                       latitude=latitude,
                                                       longitude=longitude,
                                                       channel=channel,
                                                       ERP_Watts=ERP_Watts,
                                                       HAAT_meters=haat_meters,
                                                       tx_type=tx_type)

                # Add optional information
                new_station.add_facility_id(station['facility_id'])
                new_station.add_callsign(station['fac_callsign'])
                new_station.add_app_id(station['app_id'])

                self._add_entity(new_station)

    def digital_tv_types(self):
        return ['DT']

    def analog_tv_types(self):
        return ['TV']

    def ignored_tv_types(self):
        return ['DD', 'LM']     # distributed digital, land mobile

    def get_max_protected_radius_km(self):
        """
        See
        :meth:`protected_entities.ProtectedEntities.get_max_protected_radius_km`
        for more details.

        :return: 200.0
        :rtype: float
        """
        return 200.0


class RegionCanadaTvOnly(Region):
    """
    Canada region with only TV stations.
    Protected entities of PLMRS and Radio Astronomy types are just dummy objects.
    """

    def _get_boundary_class(self):
        """Returns the class to be used as the boundary of the region."""
        return BoundaryCanada
    
    def _load_protected_entities(self):
        self.protected_entities[
            protected_entities_tv_stations.ProtectedEntitiesTVStations] = \
            ProtectedEntitiesTVStationsCanadaFromFccLearn(self)

        self.protected_entities[ProtectedEntitiesPLMRS] = \
            ProtectedEntitiesDummy(self)

        self.protected_entities[ProtectedEntitiesRadioAstronomySites] = \
            ProtectedEntitiesDummy(self)

    def get_frequency_bounds(self, channel):
        if channel in [2, 3, 4]:
            low = (channel - 2) * 6 + 54
            high = (channel - 2) * 6 + 60
        elif channel in [5, 6]:
            low = (channel - 5) * 6 + 76
            high = (channel - 5) * 6 + 82
        elif 7 <= channel <= 13:
            low = (channel - 7) * 6 + 174
            high = (channel - 7) * 6 + 180
        elif 14 <= channel <= 69:
            low = (channel - 14) * 6 + 470
            high = (channel - 14) * 6 + 476
        else:
            raise ValueError("Invalid channel number: %d" % channel)
        return low, high

    def get_tvws_channel_list(self):
        # 2, 5-36, 38-51
        return [2] + range(5, 37) + range(38, 52)

    def get_portable_tvws_channel_list(self):
        # 21-36, 38-51
        return range(21, 37) + range(38, 52)

    def get_channel_list(self):
        # 2-51
        return range(2, 52)

    def get_channel_width(self):
        #Same across North America
        return 6e6


class DataMap2DCanada(DataMap2DWithFixedBoundingBox):
    """:class:`DataMap2D` with presets bounds for Canada."""
    latitude_bounds = [41, 84]
    longitude_bounds = [-142, -52]
    default_num_latitude_divisions = 200
    default_num_longitude_divisions = 300


class ProtectedEntitiesTVStationsUnitedStatesIncentiveAuctionAndCanadaFromFccLearn(protected_entities_tv_stations.ProtectedEntitiesTVStations):

    """This class describes all entities from the United States as well as Canada, and is
    used for implementing border protections. Entries for United States TV stations are taken
    from incentive auction baseline file, and for Canadian TV stations from the FCC Learn website.

    """

    _us_stations = ProtectedEntitiesTVStationsUnitedStatesIncentiveAuction_WithRepack(RegionUnitedStates())
    _canadian_stations = ProtectedEntitiesTVStationsCanadaFromFccLearn(RegionCanadaTvOnly())

    def source_filename(self):
        return \
            "**blank**: Reading from already-loaded source data"

    def source_name(self):
        return "**blank**: Reading from already-loaded source data"

    def _load_entities(self):
        #Loading US as well as Canadian entities.
        self._entities = self._us_stations.stations() + self._canadian_stations.stations()
        self._refresh_cached_data()

    def digital_tv_types(self):
        return ['DT']

    def analog_tv_types(self):
        return ['TV']

    def ignored_tv_types(self):
        return ['DD', 'LM']     # distributed digital, land mobile

    def get_max_protected_radius_km(self):
        """
        See
        :meth:`protected_entities.ProtectedEntities.get_max_protected_radius_km`
        for more details.

        :return: 200.0
        :rtype: float
        """
        return 200.0



class RegionUnitedStatesWithUSAndCanadaStations(RegionUnitedStates):

    """This class describes the US region with additional protected entities from
     Canada so as to implement border protections."""

    def _load_protected_entities(self):
        self.protected_entities[
            protected_entities_tv_stations.ProtectedEntitiesTVStations] = \
            ProtectedEntitiesTVStationsUnitedStatesIncentiveAuctionAndCanadaFromFccLearn(self)

        self.protected_entities[ProtectedEntitiesPLMRS] = \
            ProtectedEntitiesDummy(self)

        self.protected_entities[ProtectedEntitiesRadioAstronomySites] = \
            ProtectedEntitiesDummy(self)



class RegionCanadaWithUSAndCanadaStations(RegionCanadaTvOnly):

    """This class describes the Canadian region with additional protected entities
    from the United States so as to implement border protections."""

    def _load_protected_entities(self):
        self.protected_entities[
            protected_entities_tv_stations.ProtectedEntitiesTVStations] = \
            ProtectedEntitiesTVStationsUnitedStatesIncentiveAuctionAndCanadaFromFccLearn(self)

        self.protected_entities[ProtectedEntitiesPLMRS] = \
            ProtectedEntitiesDummy(self)

        self.protected_entities[ProtectedEntitiesRadioAstronomySites] = \
            ProtectedEntitiesDummy(self)


####
#   END OF CLASS DEFINITIONS
####

####
#   MAIN TVWS EVALUATION
####

#Seeing what Australian boundary looks like
kml = simplekml.Kml()
bc = BoundaryCanada()
bc.add_to_kml(kml)
kml.save("canada_boundary_test.kml")


#Seeing where TV stations are located in Australia
r = RegionCanadaTvOnly()
pe = r.get_protected_entities_of_type(protected_entities_tv_stations.ProtectedEntitiesTVStations)
pe.export_to_kml("tv_stations_in_canada.kml")


#Creating specifications for DataMap2D and region in Australia
datamap_spec = SpecificationDataMap(DataMap2DCanada, 200, 300)
regionmap_spec = SpecificationRegionMap(BoundaryCanada, datamap_spec)
region_map = regionmap_spec.fetch_data()

#Making sure Australian region map is correct
plot = region_map.make_map(is_in_region_map=region_map)
plot.add_boundary_outlines(boundary=BoundaryCanada())
plot.set_boundary_color('k')
plot.set_boundary_linewidth('1')
plot.save("canadian_region_map.png")


#Creating specification for whitespace map (fixed devices) and evaluating it
device = Device(is_portable=False, haat_meters=30)
whitespace_map_spec = SpecificationWhitespaceMap(regionmap_spec,
                                                 RegionCanadaWithUSAndCanadaStations,
                                                 RulesetFcc2012, device)
is_whitespace_map = whitespace_map_spec.fetch_data()
total_whitespace_mhz = is_whitespace_map.sum_all_layers()

#Looking at available whitespace in MHz
def convert_channels_to_mhz(latitude, longitude, latitude_index, longitude_index, current_value):
    return 6 * current_value

total_whitespace_mhz.update_all_values_via_function(convert_channels_to_mhz)

#Plotting available whitespace in MHz map
plot = total_whitespace_mhz.make_map(is_in_region_map=region_map)
plot.add_boundary_outlines(boundary=BoundaryCanada())
plot.set_boundary_color('k')
plot.set_boundary_linewidth('1')

# Add a title and colorbar
# plot.set_title("Number of available TVWS channels")
plot.add_colorbar(vmin=0, vmax=300, label="Available Whitespace (MHz)", decimal_precision=0)
plot.set_colorbar_ticks([0, 50, 100, 150, 200, 250, 300])

# Save the plot
plot.save("Amount of available TVWS in Canada_fcc.png")

####
#   END OF MAIN TVWS EVALUATION
####







