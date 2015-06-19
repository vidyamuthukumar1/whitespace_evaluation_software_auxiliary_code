import csv
import os
import simplekml
import sys

from west import region
from west import boundary
from west import protected_entities_tv_stations
from west.protected_entities import ProtectedEntitiesDummy
from west.protected_entities_radio_astronomy_sites import ProtectedEntitiesRadioAstronomySites
from west.protected_entities_plmrs import ProtectedEntitiesPLMRS
from west.protected_entity_tv_station import ProtectedEntityTVStation
from west.data_map import DataMap2DWithFixedBoundingBox, DataMap3D
from west.ruleset_fcc2012 import RulesetFcc2012
from west.protected_entities_tv_stations import ProtectedEntitiesTVStations
from west import helpers


####
    # CLASS DEFINITIONS
####

class BoundaryAustralia(boundary.BoundaryShapefile):
    """
    :class:`Boundary` describing Australia.

    Data source:
    http://www.statsilk.com/files/country/StatPlanet_Australia.zip

    Main page:
    http://www.statsilk.com/maps/download-free-shapefile-maps#download-country-shapefile-maps
    """
    def boundary_filename(self):
        # return os.path.join("province", "PROVINCE.SHP")
        return os.path.join("data", "Region", "Australia", "australia", "web", "map", "map.shp")

    def _geometry_name_field_str(self):
        return "STE_NAME11" # could also be SA4_NAME11




class ProtectedEntitiesTVStationsAustralia2015(
    protected_entities_tv_stations.ProtectedEntitiesTVStations):
    """This class contains Australian TV stations listed at
    http://www.acma.gov.au/~/media/Licence%20Issue%20and%20Allocation/Information/zip%20file/Broadcast%20Transmitter%20Excel%20zip.zip

    Main website:
    http://www.acma.gov.au/Industry/Spectrum/Radiocomms-licensing/Apparatus-licences/list-of-licensed-broadcasting-transmitters
    
    NOTE: The transition to digital stations is complete in Australia as of 10 December 2013. There are NO longer any analog stations
    transmitting in Australia.
    """

    def source_filename(self):
        return {"analog": "data/Region/Australia/TV.csv",
                "digital": "data/Region/Australia/DTV.csv"}

    def source_name(self):
        return "Who knows?"


    def _load_entities(self):
        """
        Example data:


        """
        self.log.debug("Loading TV stations from \"%s\" (%s)" % (
            str(self.source_filename()), str(self.source_name())))

        def convert_dms_to_decimal(degrees, minutes, seconds):
            return degrees + minutes/60 + seconds/3600

        def add_station(station, tx_type):

            try:
                # Example latitude: 42 52 28S
                lat_string = station['Latitude']
                lat_deg = float(lat_string[:2])
                lat_min = float(lat_string[3:5])
                lat_sec = float(lat_string[6:8])
                latitude = convert_dms_to_decimal(lat_deg, lat_min,
                                                  lat_sec) * -1

                # Example longitude: 147 29 55E
                lon_string = station['Longitude']
                # lon_sec = float(lon_string[:2])
                # lon_min = float(lon_string[3:5])
                # lon_deg = float(lon_string[6:8])
                lon_sec = float(lon_string[-3:-1])
                lon_min = float(lon_string[-6:-4])
                lon_deg = float(lon_string[:-7])
                longitude = convert_dms_to_decimal(lon_deg, lon_min,
                                                   lon_sec)

                try:
                    channel = int(station['Channel'])
                except ValueError:
                    # Some channel numbers end in "A". This is a valid channel number and we will just write it as a string channel.
                    # TODO: investigate this
                    #channel = int(station["Channel"][:-1])
                    channel = station["Channel"]
                if channel not in self.region.get_tvws_channel_list():
                    self.log.warning("skipping station on invalid channel: "
                                     "%d" % channel)
                    return

                #Added code to remove station with license status 'Surrendered' or 'Request Pending'
                license_status = station['Status']
                if license_status == 'Renewal Pending':
                    self.log.warning("Skipping station that has renewal pending")
                    return
                if license_status == 'Surrendered':
                    self.log.warning("Skipping station that has surrendered its license")
                    return

                ERP_Watts = float(station['Maximum ERP (W)'])
                # if ERP_Watts < 0.01:
                #     self.log.warning("Skipping station with 0 W ERP: " +
                #                      str(station))
                #     return
                haat_meters = float(station['Antenna Height'])
            except Exception as e:
                self.log.error("Error loading station: " + str(e) +
                               "\n Station data: " + str(station))

                return

            new_station = ProtectedEntityTVStation(self,
                                                   self.get_mutable_region(),
                                                   latitude=latitude,
                                                   longitude=longitude,
                                                   channel=channel,
                                                   ERP_Watts=ERP_Watts,
                                                   HAAT_meters=haat_meters,
                                                   tx_type=tx_type)

            # Add optional information
            new_station.add_callsign(station['Callsign'])

            self._add_entity(new_station)


        # Add stations
        source_filenames = self.source_filename()
        for tx_type in ["analog", "digital"]:
            with open(source_filenames[tx_type], 'rU') as f:
                station_csv = csv.DictReader(f)
                for station_data in station_csv:
                    add_station(station_data, tx_type)

    def digital_tv_types(self):
        return ["digital"]

    def analog_tv_types(self):
        return ["analog"]

    def ignored_tv_types(self):
        return []

    def get_max_protected_radius_km(self):
        """
        See
        :meth:`protected_entities.ProtectedEntities.get_max_protected_radius_km`
        for more details.

        :return: 200.0
        :rtype: float
        """
        return 200.0


class RegionAustraliaTvOnly(region.Region):

    def _get_boundary_class(self):
        """Returns the class to be used as the boundary of the region."""
        return BoundaryAustralia

    def _load_protected_entities(self):
        self.protected_entities[
            protected_entities_tv_stations.ProtectedEntitiesTVStations] = \
            ProtectedEntitiesTVStationsAustralia2015(self)

        self.protected_entities[ProtectedEntitiesPLMRS] = \
            ProtectedEntitiesDummy(self)

        self.protected_entities[ProtectedEntitiesRadioAstronomySites] = \
            ProtectedEntitiesDummy(self)

    def get_center_frequency(self, channel):
        """Note: We approximate the center frequencies of channels if they are outside the frequency range for F curves.
        This has been shown to cause no change in the protected radius of TV stations"""

        low, high = self.get_frequency_bounds(channel)
        freq = (low + high)/2
        #Approximate frequencies between 137 and 174 to 174 MHz
        if 137 <= freq < 174:
            return 177
        #Approximate frequencies between 216 and 230 to 216 Mhz
        elif 216 < freq <= 230:
            return 213
        return freq

    def get_frequency_bounds(self, channel):
        """Correct frequency bounds obtained from
        http://www.acma.gov.au/~/media/Licence%20Issue%20and%20Allocation/Publication/pdf/TVRadio_Handbook_Electronic_edition%20pdf.pdf
        pages 436-438
        """
        if channel == 2:
            low = 63
            high = low + 7
        elif channel == 3:
            low = 85
            high = low + 7
        elif channel == 4:
            low = 94
            high = low + 7
        elif channel == 5:
            low = 101
            high = low + 7
        elif channel == '5A':
            low = 137
            high = low + 7
        elif channel in range(6, 10):
            low = (channel - 6) * 7 + 174
            high = (channel - 6) * 7 + 181
        elif channel == '9A':
            low = 202
            high = 209
        elif channel in range(10, 13):
            low = (channel -10) * 7 + 209
            high = (channel - 10) * 7 + 216
        elif channel in range(28, 36):
            low = (channel - 28) * 7 + 526
            high = (channel - 28) * 7 + 533
        elif channel in range(36, 70):
            low = (channel - 36) * 7 + 582
            high = (channel - 36) * 7 + 589
        else:
            raise ValueError("Invalid channel number: %d" % channel)
        return low, high

    def get_tvws_channel_list(self):

        """We assume that all channels allocated for digital TV in Australia are
        valid TVWS channels, until ACMA develops a candidate ruleset that tells
        us otherwise."""

        return range(6, 13) + range(28, 70) + ['5A', '9A']

    def get_portable_tvws_channel_list(self):
        return self.get_tvws_channel_list()

    def get_channel_list(self):
        #Reference: http://www.acma.gov.au/~/media/Licence%20Issue%20and%20Allocation/Publication/pdf/TVRadio_Handbook_Electronic_edition%20pdf.pdf
        #pages 436-438
        return range(6, 13) + range(28, 70) + ['5A', '9A']

    def get_channel_width(self):

        """The channel width of all channels allocated for digital TV is 7 MHz.
        Some channels below 5 have different widths.
        Therefore, if our region contained entities other than TV stations, we MIGHT need
        a more generic channel width function that return width based on channel."""

        return 7e6


class DataMap2DAustralia(DataMap2DWithFixedBoundingBox):
    """:class:`DataMap2D` with presets bounds for Australia."""
    # NE -9.228820, 159.278717
    # SW -54.640301, 112.921112
    latitude_bounds = [-45, -10]
    longitude_bounds = [110, 155]
    default_num_latitude_divisions = 280
    default_num_longitude_divisions = 360


class RulesetFcc2012ModifiedForAustralia(RulesetFcc2012):
    """
    The important modification that had to be made to RulesetFcc2012
    to apply it to Australia is to accommodate non-integral channels
    in adjacency conditions.
    Now, [8, 9, '9A', 10, 11, ....] is the correct order of channels.
    For instance, this means that channels 9 and 10 are adjacent to '9A',
    channels '9A' and 11 are adjacent to channel 10, and channels 8 and '9A'
    are adjacent to 9.
    This was not accounted for in the original FCC ruleset.
    """

    def location_is_whitespace_tv_stations_only(self, region, location, device_channel, device):
        """
        Determines whether a location is considered whitespace *on the basis
        of TV station protections alone.*

        .. note:: Does not check to see if the location is within the region.

        :param region: region containing the TV stations
        :type region: :class:`region.Region` object
        :param location: (latitude, longitude)
        :type location: tuple of floats
        :param device_channel: channel to be tested for whitespace
        :type device_channel: int
        :param device: device that proposes operating in the whitespaces
        :type device: :class:`device.Device`
        :return: True if the location is whitespace; False otherwise
        :rtype: bool
        """
        if device.is_portable():
            device_haat = 1
        else:
            device_haat = device.get_haat()

        tv_stations_container = region.get_protected_entities_of_type(
            ProtectedEntitiesTVStations, use_fallthrough_if_not_found=True)

        # Check cochannel exclusions
        cochannel_stations = tv_stations_container.get_list_of_entities_on_channel(device_channel)
        for station in cochannel_stations:
            if self.cochannel_tv_station_is_protected(station, location, device_haat):
                return False

        # Portable devices are not subject to adjacent-channel exclusions
        if device.is_portable():
            return True

        # Check adjacent-channel exclusions
        adjacent_channel_stations = []
        if device_channel == '9A':
            adj_channel_list = [9, 10]
        elif device_channel == '5A':
            adj_channel_list = []
        elif device_channel == 10:
            adj_channel_list = ['9A', 11]
        elif device_channel == 9:
            adj_channel_list = [8, '9A']
        else:
            adj_channel_list = [device_channel - 1, device_channel + 1]
        for adj_chan in adj_channel_list:
            if not adj_chan in region.get_channel_list():
                continue
            if helpers.channels_are_adjacent_in_frequency(region, adj_chan, device_channel):
                adjacent_channel_stations += tv_stations_container.get_list_of_entities_on_channel(adj_chan)

        for station in adjacent_channel_stations:
            if self.adjacent_channel_tv_station_is_protected(station, location, device_haat):
                return False

        return True

    def location_is_whitespace_plmrs_only(self, region, location, device_channel):
        """
        Determines whether a location is considered whitespace *on the basis
        of PLMRS protections alone.*

        .. note:: Does not check to see if the location is within the region.

        :param region: region containing the PLMRS entities
        :type region: :class:`region.Region` object
        :param location: (latitude, longitude)
        :type location: tuple of floats
        :param device_channel: channel to be tested for whitespace
        :type device_channel: int
        :return: True if the location is whitespace; False otherwise
        :rtype: bool
        """
        plmrs_container = region.get_protected_entities_of_type(
            ProtectedEntitiesPLMRS, use_fallthrough_if_not_found=True)

        # Check cochannel exclusions
        cochannel_plmrs = plmrs_container.get_list_of_entities_on_channel(device_channel)
        for plmrs_entry in cochannel_plmrs:
            if self.plmrs_is_protected(plmrs_entry, location, device_channel, region):
                return False

        # Check adjacent-channel exclusions
        adjacent_channel_plmrs = []
        adjacent_channel_stations = []
        if device_channel == '9A':
            adj_channel_list = [9, 10]
        elif device_channel == '5A':
            adj_channel_list = []
        elif device_channel == 10:
            adj_channel_list = ['9A', 11]
        elif device_channel == 9:
            adj_channel_list = [8, '9A']
        else:
            adj_channel_list = [device_channel - 1, device_channel + 1]
        for adj_chan in adj_channel_list:
            if not adj_chan in region.get_channel_list():
                continue
            if helpers.channels_are_adjacent_in_frequency(region, adj_chan, device_channel):
                adjacent_channel_plmrs += plmrs_container.get_list_of_entities_on_channel(adj_chan)

        for plmrs_entry in adjacent_channel_plmrs:
            if self.plmrs_is_protected(plmrs_entry, location, device_channel, region):
                return False

        return True

####
#   END OF CLASS DEFINITIONS
####

####
#   MAIN TVWS EVALUATION
####

#Seeing what Australian boundary looks like
kml = simplekml.Kml()
bc = BoundaryAustralia()
bc.add_to_kml(kml)
kml.save("australia_boundary_test.kml")


#Seeing where TV stations are located in Australia
r = RegionAustraliaTvOnly()
pe = r.get_protected_entities_of_type(protected_entities_tv_stations.ProtectedEntitiesTVStations)
pe.export_to_kml("tv_stations_in_australia.kml")


#Creating specifications for DataMap2D and region in Australia
datamap_spec = SpecificationDataMap(DataMap2DAustralia, 35*8, 45*8)
regionmap_spec = SpecificationRegionMap(BoundaryAustralia, datamap_spec)
region_map = regionmap_spec.fetch_data()

#Making sure Australian region map is correct
plot = region_map.make_map(is_in_region_map=region_map)
plot.add_boundary_outlines(boundary=BoundaryAustralia())
plot.set_boundary_color('k')
plot.set_boundary_linewidth('1')
plot.save("australian_region_map.png")


#Creating specification for whitespace map (fixed devices) and evaluating it
device = Device(is_portable=False, haat_meters=30)
whitespace_map_spec = SpecificationWhitespaceMap(regionmap_spec,
                                                 RegionAustraliaTvOnly,
                                                 RulesetFcc2012ModifiedForAustralia, device)
is_whitespace_map = whitespace_map_spec.fetch_data()
total_whitespace_mhz = is_whitespace_map.sum_all_layers()

#Looking at available whitespace in MHz
def convert_channels_to_mhz(latitude, longitude, latitude_index, longitude_index, current_value):
    return 7 * current_value

total_whitespace_mhz.update_all_values_via_function(convert_channels_to_mhz)

#Plotting available whitespace in MHz map
plot = total_whitespace_mhz.make_map(is_in_region_map=region_map)
plot.add_boundary_outlines(boundary=BoundaryAustralia())
plot.set_boundary_color('k')
plot.set_boundary_linewidth('1')

# Add a title and colorbar
# plot.set_title("Number of available TVWS channels")
plot.add_colorbar(vmin=0, vmax=51*7, label="Available Whitespace (MHz)", decimal_precision=0) #Length of the TVWS channel list is 51
plot.set_colorbar_ticks([0, 50, 100, 150, 200, 250, 300, 350])

# Save the plot
plot.save("Amount of available TVWS in Australia_fcc.png")

####
#   END OF MAIN TVWS EVALUATION
####
