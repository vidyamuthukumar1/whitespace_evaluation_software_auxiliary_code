from west.ruleset import Ruleset
from west.protected_entity_tv_station import ProtectedEntityTVStation
from west.protected_entities_tv_stations import ProtectedEntitiesTVStations
from west.propagation_model_fcurves import PropagationModelFcurves
from west.propagation_model import PropagationCurve
import west.data_map

import helpers_augmented
import numpy

from geopy.distance import vincenty

class RulesetIndustryCanada2015(Ruleset):
    """Ruleset for Industry Canada rules, released Feb 2015"""

    # Note: The frequency range of the TV bands is the same across North
    # America.

    _low_vhf_lower_frequency_mhz = 54 # North America channel 2 (lower edge)
    _low_vhf_upper_frequency_mhz = 88 # North America channel 6 (upper edge)

    _high_vhf_lower_frequency_mhz = 174 # North America channel 7 (lower edge)
    _high_vhf_upper_frequency_mhz = 216 # North America channel 13 (upper edge)

    _uhf_lower_frequency_mhz = 470 # North America channel 14 (lower edge)
    _uhf_upper_frequency_mhz = 890 # North America channel 83 (upper edge)

    _apply_taboo_channel_exclusions = True
    _apply_far_side_separation_distance_conditions = True

    def name(self):
        return "Industry Canada 2015 regulations"

    def classes_of_protected_entities(self):
        #Only ProtectedEntityTVStation for now
        return [ProtectedEntityTVStation]

    def get_default_propagation_model(self):
        return PropagationModelFcurves()



####
#   BASIC WHITESPACE CALCULATIONS
####
    def _is_permissible_channel(self, region, channel, device):
        """
        Checks that ``channel`` is permissible for whitespace operation by
        ``device``. In particular, returns False if:

          * ``channel`` is not a TVWS channel in the ``region`` or
          * ``device`` is portable and ``channel`` is not in the portable
            TVWS channel list for the ``region``

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :return: True if whitespace operation is allowed on this channel; \
            False otherwise
        :rtype: bool
        """
        if channel not in region.get_tvws_channel_list():
            return False


        if device.is_portable() and (channel not in
                                         region.get_portable_tvws_channel_list()):
            return False

        return True
####
#   END BASIC WHITESPACE CALCULATIONS
####

####
#   TV STATION PROTECTION CALCULATIONS
#   (separate section for protection tables)
####
    def get_tv_protected_radius_km(self, tv_station, device_location):
        """
        Determines the protected radius of the TV station in the direction of
        `device_location`.

        :param tv_station: the TV station of interest
        :type tv_station: \
            :class:`protected_entity_tv_station.ProtectedEntityTVStation`
        :param device_location: (latitude, longitude)
        :type device_location: tuple of floats
        :return: the protected radius of the TV station in kilometers
        :rtype: float
        """
        freq = tv_station.get_center_frequency()

        curve = self.get_tv_curve(tv_station.is_digital())
        target_field_strength_dbu = self.get_tv_target_field_strength_dBu(
            tv_station.is_digital(), freq)

        tv_location = tv_station.get_location()

        desired_watts = self._propagation_model.dBu_to_Watts(
            target_field_strength_dbu, freq)
        tv_power_watts = tv_station.get_erp_watts()
        pathloss_coefficient = desired_watts / tv_power_watts
        protection_distance_km = \
            self._propagation_model.get_distance(pathloss_coefficient,
                                                 frequency=freq,
                                                 tx_height=tv_station.get_haat_meters(),
                                                 tx_location=tv_location,
                                                 rx_location=device_location,
                                                 curve_enum=curve)
        return protection_distance_km

    def cochannel_tv_station_is_protected(self, tv_station, device,
                                          device_location):
        """
        Determines whether or not the TV station is protected on a cochannel basis.


        .. warning:: Uses the TV station's bounding box (whose dimensions are \
            set in \
            :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`\
            ) to speed up computations. If these dimensions are too small, TV \
            stations will be erroneously excluded from this computation.

        :param tv_station:
        :type tv_station: \
            :class:`west.protected_entity_tv_station.ProtectedEntityTVStation`
        :param device:
        :type device: \
            :class:`west.device.Device'
        :param device_location: (latitude, longitude)
        :type device_location: tuple of floats
        :return: True if the station is protected on a cochannel basis; False \
            otherwise
        :rtype: bool
        """

        if not tv_station.location_in_bounding_box(device_location):
            return False

        actual_distance_to_station_km = vincenty(tv_station.get_location(),
                                      device_location).kilometers
        protection_distance_km = self.get_tv_protected_radius_km(tv_station,
                                                                 device_location)

        if device.is_portable():
            separation_distance_km = \
            self.get_tv_cochannel_separation_distance_km_for_portable_devices(tv_station.is_digital())
            far_side_separation_distance_km = \
            self.get_tv_cochannel_far_side_separation_distance_km_for_portable_devices(tv_station.is_digital())
        else:
            separation_distance_km = \
            self.get_tv_cochannel_separation_distance_km_for_fixed_devices(device.get_haat(), tv_station.get_center_frequency(), tv_station.is_digital())
            far_side_separation_distance_km = \
            self.get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(device.get_haat(), tv_station.get_center_frequency(), tv_station.is_digital())

        # Check if we are inside the protected contour or inside the separation distance from far side of the protected contour.
        sep_distance_condition_valid = actual_distance_to_station_km <= protection_distance_km + separation_distance_km
        far_side_sep_distance_condition_valid = self._apply_far_side_separation_distance_conditions and actual_distance_to_station_km + protection_distance_km <= far_side_separation_distance_km
        return sep_distance_condition_valid or far_side_sep_distance_condition_valid


    def adjacent_channel_tv_station_is_protected(self, tv_station, device,
                                                 device_location):
        """
        Determines whether or not the TV station is protected on an
        adjacent-channel basis.


        .. warning:: Uses the TV station's bounding box (whose dimensions are \
            set in \
            :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`\
            ) to speed up computations. If these dimensions are too small, \
            TV stations will be erroneously excluded from this computation.

        :param tv_station:
        :type tv_station: \
            :class:`protected_entity_tv_station.ProtectedEntityTVStation`
        :param device_location: (latitude, longitude)
        :type device_location: tuple of floats
        :param device_haat: the height above average terrain (HAAT) of the \
            device in meters
        :type device_haat: float
        :return: True if the station is protected on an adjacent-channel \
            basis; False otherwise
        :rtype: bool
        """

        if not tv_station.location_in_bounding_box(device_location):
            return False

        actual_distance_to_station_km = vincenty(tv_station.get_location(), device_location).kilometers
        protection_distance_km = self.get_tv_protected_radius_km(tv_station, device_location)

        if device.is_portable():
            separation_distance_km = self.get_tv_adjacent_channel_separation_distance_km_for_portable_devices(tv_station.is_digital())
            far_side_separation_distance_km = self.get_tv_adjacent_channel_far_side_separation_distance_km_for_portable_devices(tv_station.is_digital())
        else:
            separation_distance_km = self.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(device.get_haat(), tv_station.get_center_frequency(), tv_station.is_digital())
            far_side_separation_distance_km = self.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(device.get_haat(), tv_station.get_center_frequency(), tv_station.is_digital())


        # Check if we are inside the protected contour or inside the separation distance from far side of the contour
        sep_distance_condition_valid = actual_distance_to_station_km <= protection_distance_km + separation_distance_km
        far_side_sep_distance_condition_valid = self._apply_far_side_separation_distance_conditions and actual_distance_to_station_km + protection_distance_km <= far_side_separation_distance_km
        return sep_distance_condition_valid or far_side_sep_distance_condition_valid

    def taboo_channel_tv_station_is_protected(self, tv_station, device,
                                                 device_location):
        """
        Determines whether or not the TV station is protected on an
        taboo-channel basis.


        .. note:: We assume that the user has already checked that the channel
        is indeed a taboo channel.

        .. warning:: Uses the TV station's bounding box (whose dimensions are \
            set in \
            :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`\
            ) to speed up computations. If these dimensions are too small, \
            TV stations will be erroneously excluded from this computation.
        .. note:: We assume that the user has already checked that the channel
        is indeed a taboo channel.
        .. note:: Taboo channel exclusions are only applied for analog TV stations.

        :param tv_station:
        :type tv_station: \
            :class:`protected_entity_tv_station.ProtectedEntityTVStation`
        :param device_location: (latitude, longitude)
        :type device_location: tuple of floats
        :param device_haat: the height above average terrain (HAAT) of the \
            device in meters
        :type device_haat: float
        :return: True if the station is protected on an adjacent-channel \
            basis; False otherwise
        :rtype: bool
        """



        if not self._apply_taboo_channel_exclusions:
            raise ValueError("We are not supposed to be applying taboo channel exclusions for this class. Please check.")

        if tv_station.is_digital():
            raise ValueError("Taboo channel protections do not apply for digital TV")

        if not tv_station.location_in_bounding_box(device_location):
            return False

        actual_distance_to_station_km = vincenty(tv_station.get_location(), device_location).kilometers
        protection_distance_km = self.get_tv_protected_radius_km(tv_station, device_location)

        if device.is_portable():
            separation_distance_km = self.get_tv_taboo_channel_separation_distance_km_for_portable_devices(tv_station.is_digital())
            far_side_separation_distance_km = self.get_tv_taboo_channel_far_side_separation_distance_km_for_portable_devices(tv_station.is_digital())
        else:
            separation_distance_km = self.get_tv_taboo_channel_separation_distance_km_for_fixed_devices(device.get_haat(), tv_station.get_center_frequency(), tv_station.is_digital())
            far_side_separation_distance_km = self.get_tv_taboo_channel_far_side_separation_distance_km_for_fixed_devices(device.get_haat(), tv_station.get_center_frequency(), tv_station.is_digital())


        # Check if we are inside the protected contour or inside the separation distance from far side of the contour

        sep_distance_condition_valid = actual_distance_to_station_km <= protection_distance_km + separation_distance_km
        far_side_sep_distance_condition_valid = self._apply_far_side_separation_distance_conditions and actual_distance_to_station_km + protection_distance_km <= far_side_separation_distance_km
        return sep_distance_condition_valid or far_side_sep_distance_condition_valid

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

        tv_stations_container = region.get_protected_entities_of_type(
            ProtectedEntitiesTVStations)

        # Check cochannel exclusions
        cochannel_stations = tv_stations_container.get_list_of_entities_on_channel(device_channel)
        for station in cochannel_stations:
            if self.cochannel_tv_station_is_protected(station, device, location):
                return False


        # Check adjacent-channel exclusions
        list_of_adj_channels = [device_channel - 1, device_channel + 1]
        adjacent_channel_stations = []
        for adj_chan in list_of_adj_channels:
            if not adj_chan in region.get_channel_list():
                continue
            if west.helpers.channels_are_adjacent_in_frequency(region, adj_chan, device_channel):
                adjacent_channel_stations += tv_stations_container.get_list_of_entities_on_channel(adj_chan)

        for station in adjacent_channel_stations:
            if self.adjacent_channel_tv_station_is_protected(station, device, location):
                return False

        if self._apply_taboo_channel_exclusions:
            taboo_channel_stations = []
            list_of_taboo_channels_for_device_channel = self.get_list_of_taboo_channels(region, device_channel)
            for taboo_chan in list_of_taboo_channels_for_device_channel:
                if not taboo_chan in region.get_channel_list():
                    continue
                if self.channel_is_taboo(region, taboo_chan, device_channel):
                    taboo_channel_stations += tv_stations_container.get_list_of_entities_on_channel(taboo_chan)

            for station in taboo_channel_stations:
                if not station.is_digital() and self.taboo_channel_tv_station_is_protected(station, device, location):
                    return False

        return True
####
#   END TV STATION PROTECTION CALCULATIONS
####



####
#   GENERAL WHITESPACE CALCULATIONS
####

    def location_is_whitespace(self, region, location, channel, device):
        """
        Determines whether a location is considered whitespace, taking all
        protections into account (*except* wireless microphones).

        .. warning:: Does not include wireless microphone protections.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param location: (latitude, longitude)
        :type location: tuple of floats
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :return: True if the location is whitespace; False otherwise
        :rtype: bool
        """

        # TODO: think about how to add wireless microphone protections (the 2 extra channels)

        device_haat = device.get_haat()

        if not self._is_permissible_channel(region, channel, device):
            return False

        if not self.location_is_whitespace_tv_stations_only(region, location,
                                                            channel,
                                                            device_haat):
            return False


        return True

    def apply_all_protections_to_map(self, region, is_whitespace_datamap2d,
                                     channel, device,
                                     ignore_channel_restrictions=False,
                                     reset_datamap=False, verbose=False):
        """
        Turns the input :class:`data_map.DataMap2D` into a map of whitespace
        availability. A value of `True` means that whitespace is available in
        that location, whereas a value of `False` means that that location is
        not considered whitespace for the supplied device.

        .. note:: Any entries which are already `False` will not be evaluated \
            unless `reset_datamap=True`.

        Recommended usage is to initialize is_whitespace_datamap2d to an
        is_in_region DataMap2D to avoid computations on locations which are
        outside of the region. No in-region testing is done otherwise.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_datamap2d: DataMap2D to be filled with the output
        :type is_whitespace_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :param ignore_channel_restrictions: if True, skips checks relating to \
            permissible channels of operation for the specified device
        :type ignore_channel_restrictions: bool
        :param reset_datamap: if True, the DataMap2D is reset to `True` \
            (i.e. "evaluate all") before computations begin
        :type reset_datamap: bool
        :param verbose: if True, progress updates will be logged \
            (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: None
        """
        if reset_datamap:
            # Initialize to True so that all points will be evaluated
            is_whitespace_datamap2d.reset_all_values(True)

        if not ignore_channel_restrictions:
            self.apply_channel_restrictions_to_map(region, is_whitespace_datamap2d, channel, device)

        self.apply_tv_exclusions_to_map(region, is_whitespace_datamap2d, channel, device, verbose=verbose)

    def apply_entity_protections_to_map(self, region, is_whitespace_datamap2d,
                                        channel, device,
                                        protected_entities_list,
                                        ignore_channel_restrictions=False,
                                        reset_datamap=False, verbose=False):
        """
        Turns the input :class:`data_map.DataMap2D` into a map of whitespace
        availability `based on only the provided list of protected entities`. A
        value of `True` means that whitespace is available in that location,
        whereas a value of `False` means that that location is not considered
        whitespace for the supplied device.

        .. note:: Any entries which are already `False` will not be evaluated \
            unless `reset_datamap=True`.

        .. note:: Channel restrictions (see \
            :meth:`apply_channel_restrictions_to_map`) are still applied.

        .. note:: Logs an error but continues computation if an unrecognized \
            protected entity is found.

        Recommended usage is to initialize is_whitespace_datamap2d to an
        is_in_region DataMap2D to avoid computations on locations which are
        outside of the region. No in-region testing is done otherwise.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_datamap2d: DataMap2D to be filled with the output
        :type is_whitespace_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :param protected_entities_list: list of protected entities to be used \
            when calculating the whitespace map
        :type protected_entities_list: list of \
            :class:`protected_entities.ProtectedEntities` objects
        :param ignore_channel_restrictions: if True, skips checks relating to \
            permissible channels of operation for the specified device
        :type ignore_channel_restrictions: bool
        :param reset_datamap: if True, the DataMap2D is reset to `True` \
            (i.e. "evaluate all") before computations begin
        :type reset_datamap: bool
        :param verbose: if True, progress updates will be logged \
            (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: None

        """
        if reset_datamap:
            # Initialize to True so that all points will be evaluated
            is_whitespace_datamap2d.reset_all_values(True)

        if not ignore_channel_restrictions:
            self.apply_channel_restrictions_to_map(region, is_whitespace_datamap2d, channel, device)

        def update_function(latitude, longitude, latitude_index, longitude_index, currently_whitespace):
            if not currently_whitespace:       # already known to not be whitespace
                return None

            location = (latitude, longitude)

            # Check to see if any entity is protected
            location_is_whitespace = True
            for entity in protected_entities_list:
                if isinstance(entity, ProtectedEntityTVStation):
                    if channel == entity.get_channel():
                        location_is_whitespace &= \
                            not self.cochannel_tv_station_is_protected(entity, device, location)
                    # Portable devices are not subjected to adjacent-channel exclusions
                    elif helpers.channels_are_adjacent_in_frequency(region, entity.get_channel(), channel):
                        location_is_whitespace &= \
                            not self.adjacent_channel_tv_station_is_protected(entity, device, location)
                    elif self.channel_is_taboo(region, entity.get_channel(), channel) and self._apply_taboo_channel_exclusions and not entity.is_digital():
                        location_is_whitespace &= \
                            not self.taboo_channel_tv_station_is_protected(entity, device, location)
                    else:
                        # Not protected if not cochannel or adjacent channel or taboo channel
                        continue
                else:
                    self.log.error("Could not apply protections for the following entity: %s" % str(entity))
                    continue

                # Don't need to check other entities if the location has already been ruled out as whitespace
                if not location_is_whitespace:
                    break

            return location_is_whitespace

        is_whitespace_datamap2d.update_all_values_via_function(update_function, verbose=verbose)

    def apply_channel_restrictions_to_map(self, region,
                                          is_whitespace_datamap2d, channel, device):
        """
        Applies simple channel-based restrictions to the map. In particular,
        resets the :class:`data_map.DataMap2D` to False values if:

          * ``channel`` is not a TVWS channel in the ``region`` or
          * ``device`` is portable and ``channel`` is not in the portable
            TVWS channel list for the ``region``

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_datamap2d: DataMap2D to be filled with the output
        :type is_whitespace_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :return: None
        """
        if not self._is_permissible_channel(region, channel, device):
            is_whitespace_datamap2d.reset_all_values(False)

    def apply_tv_exclusions_to_map(self, region, is_whitespace_datamap2d,
                                   channel, device, verbose=False):
        """
        Applies TV exclusions to the given :class:`data_map.DataMap2D`.
        Entries will be marked `True` if they are whitespace and `False`
        otherwise.

        .. note:: Any entries which are already `False` will not be evaluated.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_whitespace_datamap2d: DataMap2D to be filled with the output
        :type is_whitespace_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for whitespace
        :type channel: int
        :param device: the device which desires whitespace access
        :type device: :class:`device.Device` object
        :param verbose: if True, progress updates will be logged \
            (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: None
        """
        def tv_station_update_function(latitude, longitude, latitude_index,
                                       longitude_index, currently_whitespace):
            if not currently_whitespace:       # already known to not be whitespace
                return None
            return self.location_is_whitespace_tv_stations_only(region,
                                                                (latitude,
                                                                 longitude),
                                                                channel,
                                                                device)

        if verbose:
            self.log.info("Applying TV exclusions")
        is_whitespace_datamap2d.update_all_values_via_function(tv_station_update_function, verbose=verbose)
####
#   END GENERAL WHITESPACE CALCULATIONS
####

####
#   TV STATION PROTECTION -- TABLE IMPLEMENTATIONS
####
    def get_tv_curve(self, is_digital):
        """
        Analog and digital TV stations use slightly different propagation
        models (the F(50,50) vs. the F(50,90) curves). This function returns
        the enum for the appropriate curve.

        :param is_digital: indicates whether the station is digital or analog
        :type is_digital: boolean
        :return: the propagation curve to use
        :rtype: :class:`PropagationCurve` member
        """
        if is_digital:
            return PropagationCurve.curve_50_90
        else:
            return PropagationCurve.curve_50_50

    def get_tv_target_field_strength_dBu(self, is_digital, freq):
        """
        TV stations have varying target field strengths depending on their
        assigned channel and whether they are digital or analog. This
        information can be found in Section 9 (Table 2) of Industry
        Canada's TVWS rules. This function simply implements the table found in that
        section.

        :param is_digital: indicates whether the station is digital or analog
        :type is_digital: bool
        :param freq: the center frequency of the station's channel
        :type freq: float
        :return: target field strength in dBu
        :rtype: float
        """
        if is_digital:
            if self._low_vhf_lower_frequency_mhz <= freq <= self._low_vhf_upper_frequency_mhz:
                return 28.0
            elif self._high_vhf_lower_frequency_mhz <= freq <= self._high_vhf_upper_frequency_mhz:
                return 36.0
            elif self._uhf_lower_frequency_mhz <= freq <= self._uhf_upper_frequency_mhz:
                return 41.0 - 20.0 *numpy.log10(615.0/freq)
            else:
                self.log.warning("Unsupported frequency: %d. Defaulting to UHF parameters." % freq)
                return 41.0
        else:
            if self._low_vhf_lower_frequency_mhz <= freq <= self._low_vhf_upper_frequency_mhz:
                return 47.0
            elif self._high_vhf_lower_frequency_mhz <= freq <= self._high_vhf_upper_frequency_mhz:
                return 56.0
            elif self._uhf_lower_frequency_mhz <= freq <= self._uhf_upper_frequency_mhz:
                return 64.0 - 20.0 *numpy.log10(615.0/freq)
            else:
                self.log.warning("Unsupported frequency: %d. Defaulting to UHF parameters." % freq)
                return 64.0


    def get_tv_cochannel_separation_distance_km_for_portable_devices(self, station_is_digital):
        """
        The cochannel separation distance mandated by Industry Canada for personal/portable
        whitespace devices depends on whether the TV station to be protected is digital or
        analog. The values are given in Table 4, Section 9 of Industry Canada's rules
        and this table is implemented in this function.

        :param station_is_digital: Variable indicating whether a station is digital. If False,
                    the station is assumed to be analog.
        :type station_is_digital: boolean
        :return: IC-mandated cochannel separation distance in kilometers
        :rtype: float
        """

        if station_is_digital:
            return 14.4
        else:
            return 11.4


    def get_tv_cochannel_separation_distance_km_for_fixed_devices(self, device_haat, station_center_frequency, station_is_digital):
        """
        The cochannel separation distance mandated by Industry Canada for fixed
        whitespace devices depends on the whitespace device's height above average
        terrain (HAAT). It also depends on the center frequency of the station to be
        protected, and whether the station is digital or analog.
        The values are given in Table 3, Section 9 of Industry Canada's rules
        and this table is implemented in this function.

         .. note:: Values outside of the defined table (i.e. HAAT > 250 meters)\
            will log a warning and return the value for 250 meters.
         .. note:: If a station's center frequency is not within the frequency
         ranges for low VHF, high VHF or UHF, the default separation distance
         on UHF channels is returned.

        :param device_haat: whitespace device's height above average terrain \
            (HAAT) in meters
        :type device_haat: float
        :param station_center_frequency: station's center frequency
        :type station_center_frequency: float
        :param station_is_digital: Variable indicating whether a station is digital. If False,
                            the station is assumed to be analog.
        :return: IC-mandated cochannel separation distance in kilometers
        :rtype: float
        """

        if device_haat < 3:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 37.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 23.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 14.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 14.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 28.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 19.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 11.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 11.4

        elif 3 <= device_haat <= 10:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 37.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 23.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 14.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 14.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 28.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 19.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 11.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 11.4

        elif 10 <= device_haat < 30:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 37.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 23.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 14.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 14.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 28.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 19.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 11.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 11.4

        elif 30 <= device_haat < 50:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 47.9
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 30.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 18.7
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 18.7
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 36.5
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 25.1
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 14.7
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 14.7

        elif 50 <= device_haat < 75:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 57.5
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 37.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 23.2
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 23.2
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 44.8
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 31.1
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 18.5
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 18.5

        elif 75 <= device_haat < 100:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 63.6
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 42.9
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 27.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 27.0
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 51.5
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 36.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 21.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 21.4

        elif 100 <= device_haat < 150:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 73.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 51.7
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 33.1
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 33.1
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 60.7
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 43.9
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 26.3
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 26.3

        elif 150 <= device_haat < 200:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 80.4
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 58.3
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 37.1
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 37.1
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 67.8
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 49.9
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 30.3
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 30.3

        elif 200 <= device_haat <= 250:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 87.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 63.5
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 40.3
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 40.3
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 74.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 55.6
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 33.7
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 33.7
        else:
            self.log.warning("Attempted to get TV cochannel separation "
                             "distance for a device HAAT out of bounds: "
                             "%.2f." % device_haat + "Reverting to value for "
                                                     "largest valid HAAT.")
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 87.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 63.5
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 40.3
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 40.3
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 74.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 55.6
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 33.7
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 33.7

    def get_tv_cochannel_far_side_separation_distance_km_for_portable_devices(self, station_is_digital):
        """
        The cochannel separation distance from the far side of the station's protected contour
        mandated by Industry Canada for personal/portable whitespace devices
        depends on whether the TV station to be protected is digital or
        analog. The values are given in Table 4bis, Section 9 of Industry Canada's rules
        and this table is implemented in this function.

        :param station_is_digital: Variable indicating whether a station is digital. If False,
                    the station is assumed to be analog.
        :type station_is_digital: boolean
        :return: IC-mandated cochannel separation distance in kilometers
        :rtype: float
        """

        if station_is_digital:
            return 35.1
        else:
            return 21.1

    def get_tv_cochannel_far_side_separation_distance_km_for_fixed_devices(self, device_haat, station_center_frequency, station_is_digital):
        """
        The cochannel separation distance from the far side of the station's protected contour
        mandated by Industry Canada for fixed whitespace devices depends on the
        whitespace device's height above average terrain (HAAT). It also depends
        on the center frequency of the station to be protected,
        and whether the station is digital or analog.
        The values are given in Table 3bis, Section 9 of Industry Canada's rules
        and this table is implemented in this function.

         .. note:: Values outside of the defined table (i.e. HAAT > 250 meters)\
            will log a warning and return the value for 250 meters.
         .. note:: If a station's center frequency is not within the frequency
         ranges for low VHF, high VHF or UHF, the default separation distance
         on UHF channels is returned.

        :param device_haat: whitespace device's height above average terrain \
            (HAAT) in meters
        :type device_haat: float
        :param station_center_frequency: station's center frequency
        :type station_center_frequency: float
        :param station_is_digital: Variable indicating whether a station is digital. If False,
                            the station is assumed to be analog.
        :return: IC-mandated cochannel separation distance in kilometers
        :rtype: float
        """
        if device_haat < 3:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 82.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 53.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 35.1
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 35.1
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 43.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 28.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 21.1
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 21.1

        elif 3 <= device_haat < 10:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 82.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 53.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 35.1
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 35.1
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 43.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 28.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 21.1
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 21.1

        elif 10 <= device_haat < 30:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 82.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 53.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 35.1
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 35.1
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 43.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 28.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 21.1
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 21.1

        elif 30 <= device_haat < 50:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 90.3
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 63.3
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 42.2
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 42.2
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 55.4
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 36.3
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 21.1
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 21.1

        elif 50 <= device_haat < 75:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 96
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 71.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 48.3
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 23.2
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 64.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 44.5
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 26.1
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 26.1

        elif 75 <= device_haat < 100:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 101.3
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 77.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 53
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 27.0
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 70.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 50.7
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 30.3
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 30.3

        elif 100 <= device_haat < 150:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 110.5
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 85.3
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 59.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 59.8
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 79.8
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 59.9
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 36.2
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 36.2

        elif 150 <= device_haat < 200:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 117.9
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 91.1
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 64.2
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 64.2
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 87.2
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 66.5
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 40.5
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 40.5

        elif 200 <= device_haat <= 250:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 124.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 96.5
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 69.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 69.0
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 93.7
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 71.6
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 44.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 44.0
        else:
            self.log.warning("Attempted to get TV cochannel separation "
                             "distance for a device HAAT out of bounds: "
                             "%.2f." % device_haat + "Reverting to value for "
                                                     "largest valid HAAT.")
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 124.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 96.5
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 69.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 69.0
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 93.7
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 71.6
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 44.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 44.0

    def get_tv_adjacent_channel_separation_distance_km_for_portable_devices(self, station_is_digital):
        """
        The adjacent channel separation distance mandated by Industry Canada for personal/portable
        whitespace devices depends on whether the TV station to be protected is digital or
        analog. The values are given in Table 4, Section 9 of Industry Canada's rules
        and this table is implemented in this function.

        :param station_is_digital: Variable indicating whether a station is digital. If False,
                    the station is assumed to be analog.
        :type station_is_digital: boolean
        :return: IC-mandated cochannel separation distance in kilometers
        :rtype: float
        """

        if station_is_digital:
            return 1.1
        else:
            return 1.0

    def get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(self, device_haat, station_center_frequency, station_is_digital):
        """
        The adjacent channel separation distance mandated by Industry Canada for fixed
        whitespace devices depends on the whitespace device's height above average
        terrain (HAAT). It also depends on the center frequency of the station to be
        protected, and whether the station is digital or analog.
        The values are given in Table 3, Section 9 of Industry Canada's rules
        and this table is implemented in this function.

         .. note:: Values outside of the defined table (i.e. HAAT > 250 meters)\
            will log a warning and return the value for 250 meters.
         .. note:: If a station's center frequency is not within the frequency
         ranges for low VHF, high VHF or UHF, the default separation distance
         on UHF channels is returned.

        :param device_haat: whitespace device's height above average terrain \
            (HAAT) in meters
        :type device_haat: float
        :param station_center_frequency: station's center frequency
        :type station_center_frequency: float
        :param station_is_digital: Variable indicating whether a station is digital. If False,
                            the station is assumed to be analog.
        :return: IC-mandated cochannel separation distance in kilometers
        :rtype: float
        """
        if device_haat < 3:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.7
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.2
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.0
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.0

        elif 3 <= device_haat <= 10:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.7
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.2
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.0
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.0

        elif 10 <= device_haat < 30:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.7
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.2
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.0
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.0

        elif 30 <= device_haat < 50:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.5
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.7
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.2
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.0
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.0

        elif 50 <= device_haat < 75:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 3.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.9
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.6
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.7
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.0

        elif 75 <= device_haat < 100:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 3.5
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.0
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.9
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.7
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.0

        elif 100 <= device_haat < 150:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 4.2
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.1
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 3.4
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.8
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.0

        elif 150 <= device_haat < 200:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 4.7
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.1
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 3.8
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.8
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.0

        elif 200 <= device_haat <= 250:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 5.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 4.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.8
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.0
        else:
            self.log.warning("Attempted to get TV cochannel separation "
                             "distance for a device HAAT out of bounds: "
                             "%.2f." % device_haat + "Reverting to value for "
                                                     "largest valid HAAT.")
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 5.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 4.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 1.8
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.0

    def get_tv_adjacent_channel_far_side_separation_distance_km_for_portable_devices(self, station_is_digital):
        """
        The adjacent channel separation distance from the far side of the station's protected contour
        mandated by Industry Canada for personal/portable whitespace devices
        depends on whether the TV station to be protected is digital or
        analog. The values are given in Table 4bis, Section 9 of Industry Canada's rules
        and this table is implemented in this function.

        :param station_is_digital: Variable indicating whether a station is digital. If False,
                    the station is assumed to be analog.
        :type station_is_digital: boolean
        :return: IC-mandated cochannel separation distance in kilometers
        :rtype: float
        """

        if station_is_digital:
            return 1.9
        else:
            return 1.8

    def get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(self, device_haat, station_center_frequency, station_is_digital):
        """
        The adjacent channel separation distance from the far side of the station's protected contour
        mandated by Industry Canada for fixed whitespace devices depends on the
        whitespace device's height above average terrain (HAAT). It also depends
        on the center frequency of the station to be protected,
        and whether the station is digital or analog.
        The values are given in Table 3bis, Section 9 of Industry Canada's rules
        and this table is implemented in this function.

         .. note:: Values outside of the defined table (i.e. HAAT > 250 meters)\
            will log a warning and return the value for 250 meters.
         .. note:: If a station's center frequency is not within the frequency
         ranges for low VHF, high VHF or UHF, the default separation distance
         on UHF channels is returned.

        :param device_haat: whitespace device's height above average terrain \
            (HAAT) in meters
        :type device_haat: float
        :param station_center_frequency: station's center frequency
        :type station_center_frequency: float
        :param station_is_digital: Variable indicating whether a station is digital. If False,
                            the station is assumed to be analog.
        :return: IC-mandated cochannel separation distance in kilometers
        :rtype: float
        """
        if device_haat < 3:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 3.5
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.6
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.9
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.9
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.3
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.8

        elif 3 <= device_haat <= 10:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 3.5
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.6
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.9
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.9
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.3
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.8

        elif 10 <= device_haat < 30:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 3.5
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.6
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.9
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.9
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 2.3
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.8

        elif 30 <= device_haat < 50:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 4.5
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 3.4
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 2.5
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 2.5
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 3.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.8

        elif 50 <= device_haat < 75:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 5.6
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 4.1
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 3.0
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 3.0
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 3.7
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.5
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.8

        elif 75 <= device_haat < 100:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 6.4
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 4.5
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 3.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 3.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 4.2
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.6
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.8

        elif 100 <= device_haat < 150:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 7.9
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 5.3
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 3.9
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 3.9
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 5.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 2.8
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.8

        elif 150 <= device_haat < 200:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 9.0
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 5.9
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 4.4
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 4.4
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 5.8
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 3.0
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.8

        elif 200 <= device_haat <= 250:
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 10.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 6.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 4.7
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 4.7
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 6.4
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 3.1
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.8
        else:
            self.log.warning("Attempted to get TV cochannel separation "
                             "distance for a device HAAT out of bounds: "
                             "%.2f." % device_haat + "Reverting to value for "
                                                     "largest valid HAAT.")
            if station_is_digital:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 10.1
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 6.2
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 4.7
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 4.7
            else:
                if self._low_vhf_lower_frequency_mhz <= station_center_frequency <= self._low_vhf_upper_frequency_mhz:
                    return 6.4
                elif self._high_vhf_lower_frequency_mhz <= station_center_frequency <= self._high_vhf_upper_frequency_mhz:
                    return 3.1
                elif self._uhf_lower_frequency_mhz <= station_center_frequency <= self._uhf_upper_frequency_mhz:
                    return 1.8
                else:
                    self.log.warning("Defaulting to value for UHF")
                    return 1.8


    def get_tv_taboo_channel_separation_distance_km_for_portable_devices(self, station_is_digital):

        """
         The taboo channel separation distance mandated by Industry Canada for personal/portable
         whitespace devices depends on whether the TV station to be protected is digital or
         analog. The values are given in Table 4, Section 9 of Industry Canada's rules
         and this table is implemented in this function.

         .. note:: We assume for this function that it has already been checked that
         the device channel and station channel are taboo with respect to one another.
         .. note:: Taboo channel restrictions only apply for analog TV stations. If the
         station is digital, this function will raise an error.

         :param station_is_digital: Variable indicating whether a station is digital. If False,
                     the station is assumed to be analog.
         :type station_is_digital: boolean
         :return: IC-mandated cochannel separation distance in kilometers
         :rtype: float
         """

        if station_is_digital:
            self.log.error("Taboo channel protections do not apply for digital TV")
        else:
            return 1.0

    def get_tv_taboo_channel_separation_distance_km_for_fixed_devices(self, device_haat, station_center_frequency, station_is_digital):

        """
        The taboo channel separation distance from the station's protected contour
        mandated by Industry Canada for fixed whitespace devices depends on the
        whitespace device's height above average terrain (HAAT). It also depends
        on the center frequency of the station to be protected,
        and whether the station is digital or analog.
        The values are given in Table 3, Section 9 of Industry Canada's rules
        and this table is implemented in this function.

         .. note:: We assume for this function that it has already been checked
         that the device channel and station channel are taboo with respect
         to one another.
         .. note:: Taboo channel restrictions only apply for analog TV stations.
         If the station is digital, this function will raise an error.
         .. note:: Values outside of the defined table (i.e. HAAT > 250 meters)\
            will log a warning and return the value for 250 meters.
         .. note:: If a station's center frequency is not within the frequency
         ranges for low VHF, high VHF or UHF, the default separation distance
         on UHF channels is returned.

        :param device_haat: whitespace device's height above average terrain \
            (HAAT) in meters
        :type device_haat: float
        :param station_center_frequency: station's center frequency
        :type station_center_frequency: float
        :param station_is_digital: Variable indicating whether a station is digital. If False,
                            the station is assumed to be analog.
        :return: IC-mandated cochannel separation distance in kilometers
        :rtype: float
        """
        if station_is_digital:
            self.log.error("Taboo channel protections do not apply for digital TV")
        else:
            return self.get_tv_adjacent_channel_separation_distance_km_for_fixed_devices(device_haat, station_center_frequency, station_is_digital)

    def get_tv_taboo_channel_far_side_separation_distance_km_for_portable_devices(self, station_is_digital):

        """
      The taboo channel separation distance from the far side of the station's protected contour
      mandated by Industry Canada for personal/portable whitespace devices
      depends on whether the TV station to be protected is digital or
      analog. The values are given in Table 4bis, Section 9 of Industry Canada's rules
      and this table is implemented in this function.

      ..note:: We assume for this function that it has already been checked that the
      device channel and station channel are taboo with respect to one another.
      ..note:: Taboo channel restrictions only apply for analog TV stations. If the
      station is digital, this function will raise an error.

      :param station_is_digital: Variable indicating whether a station is digital. If False,
                  the station is assumed to be analog.
      :type station_is_digital: boolean
      :return: IC-mandated cochannel separation distance in kilometers
      :rtype: float
      """
        if station_is_digital:
            self.log.error("Taboo channel far side protections do not apply for digital TV")
        else:
            return 1.8

    def get_tv_taboo_channel_far_side_separation_distance_km_for_fixed_devices(self, device_haat, station_center_frequency, station_is_digital):

        """
        The taboo channel separation distance from the far side of the station's protected contour
        mandated by Industry Canada for fixed whitespace devices depends on the
        whitespace device's height above average terrain (HAAT). It also depends
        on the center frequency of the station to be protected,
        and whether the station is digital or analog.
        The values are given in Table 3bis, Section 9 of Industry Canada's rules
        and this table is implemented in this function.

         .. note:: We assume for this function that it has already been checked that the
         device channel and station channel are taboo with respect to one another.
         .. note:: Taboo channel restrictions only apply for analog TV stations. If the
         station is digital, this function will raise an error.
         .. note:: Values outside of the defined table (i.e. HAAT > 250 meters)\
            will log a warning and return the value for 250 meters.
         .. note:: If a station's center frequency is not within the frequency
         ranges for low VHF, high VHF or UHF, the default separation distance
         on UHF channels is returned.

        :param device_haat: whitespace device's height above average terrain \
            (HAAT) in meters
        :type device_haat: float
        :param station_center_frequency: station's center frequency
        :type station_center_frequency: float
        :param station_is_digital: Variable indicating whether a station is digital. If False,
                            the station is assumed to be analog.
        :return: IC-mandated cochannel separation distance in kilometers
        :rtype: float
        """

        if station_is_digital:
            self.log.error("Taboo channel far side protections do not apply for digital TV")
        else:
            return self.get_tv_adjacent_channel_far_side_separation_distance_km_for_fixed_devices(device_haat, station_center_frequency, station_is_digital)

####
#   END TV STATION PROTECTION -- TABLE IMPLEMENTATIONS
####

####
#   TV VIEWERSHIP CALCULATIONS
####

    def tv_station_is_viewable(self, tv_station, location):
        """
        Determines if a particular TV station is viewable at the given location.

        .. note:: The TV station's channel is not checked. It is assumed that \
            the TV station is on the channel of interest.

        .. warning:: Uses the TV station's bounding box (whose dimensions are \
            set in \
            :class:`protected_entities_tv_stations.ProtectedEntitiesTVStations`\
            ) to speed up computations. If these dimensions are too small, \
            TV stations will be erroneously excluded from this computation.
        """
        if not tv_station.location_in_bounding_box(location):
            return False

        actual_distance_to_station_km = vincenty(tv_station.get_location(),
                                      location).kilometers
        protection_distance_km = self.get_tv_protected_radius_km(tv_station,
                                                                 location)

        return actual_distance_to_station_km <= protection_distance_km

    def create_tv_viewership_datamap(self, region, is_in_region_datamap2d,
                                     channel, list_of_tv_stations=None,
                                     verbose=False):
        """
        Creates a :class:`data_map.DataMap2D` which is True (or truthy) where TV
        can be viewed and False elsewhere (including outside the region). If not
        specified, the list of TV stations is taken from ``region``. If
        specified, only the TV stations in the list are considered.

        The output DataMap2D properties will be taken from
        ``is_in_region_datamap2d``. No input data is modified in this
        calculation.

        :param region: region containing the protected entities
        :type region: :class:`region.Region` object
        :param is_in_region_datamap2d: DataMap2D which has value True (or a \
            truthy value) inside the region's boundary and False outside. This \
            is purely to speed up computations by skipping locations that do \
            not matter.
        :type is_in_region_datamap2d: :class:`data_map.DataMap2D` object
        :param channel: channel to be tested for viewership
        :type channel: int
        :param verbose: if True, progress updates will be logged \
            (level = INFO); otherwise, nothing will be logged
        :type verbose: bool
        :return: datamap holding values representing TV viewership
        :rtype: :class:`data_map.DataMap2D`
        """

        viewership_map = west.data_map.DataMap2D.get_copy_of(is_in_region_datamap2d)
        viewership_map.reset_all_values(0)

        # Use the TV stations from the region if no list is provided
        if list_of_tv_stations is None:
            all_tv_stations = region.get_protected_entities_of_type(ProtectedEntitiesTVStations)
            list_of_tv_stations = all_tv_stations.get_list_of_entities_on_channel(channel)

        def tv_station_viewership_update_function(latitude, longitude,
                                                  latitude_index,
                                                  longitude_index,
                                                  currently_viewable):
            """Returns True if TV can be viewed at this location and False
            otherwise. Returns None if the location is already listed as
            viewable."""
            if not is_in_region_datamap2d.get_value_by_index(latitude_index,
                                                             longitude_index):

                return False        # outside of the region is defined as not
                                    # viewable
            if currently_viewable:
                return None         # don't update if it is already known that TV is viewable at this location

            for station in list_of_tv_stations:
                if not station.get_channel() == channel:
                    continue
                if self.tv_station_is_viewable(station, (latitude, longitude)):
                    return True

            return False

        viewership_map.update_all_values_via_function(tv_station_viewership_update_function, verbose=verbose)
        return viewership_map

####
#   END TV VIEWERSHIP CALCULATIONS
####

####
#   HELPER FUNCTIONS: To check if channels are taboo
# with respect to one another according to this ruleset.
####

    def get_list_of_taboo_channels(self, region, device_channel):
        """
        This function returns the list of taboo channels for a
        particular channel on which a device will operate, in a
        particular region.
        """

        list_of_taboo_channels = []
        for channel in region.get_tv_channel_list():
            if self.channel_is_taboo(region, channel, device_channel):
                list_of_taboo_channels.append(channel)

        return list_of_taboo_channels


    def channel_is_taboo(self, region, chan1, chan2):

        """
        This function tells us whether two channels are taboo with respect to one
        another in a particular region.

        Note:: We assume perfect differences in frequency. I was not able to think of
        conditions similar to the ones we use to check if two channels are adjacent in
        frequency.
        """
        if chan1 not in region.get_tv_channel_list() or chan2 not in region.get_tv_channel_list():
            # If either of the channels is undefined for the region,
            # the channels are not taboo wrt one another.
            return False

        taboo_channel_diffs = self.get_taboo_channel_diffs()
        (low1, high1) = region.get_frequency_bounds(chan1)
        (low2, high2) = region.get_frequency_bounds(chan2)
        return abs(low2 - low1) in region.get_channel_width()/1e6 * taboo_channel_diffs



    def get_taboo_channel_diffs(self):
        """
        This function tells us what the difference between numbers of
        two channels needs to be for one of them to be considered taboo
        with respect to another.

        Note:: We have only defined this for the North American region so far.
        We believe it won't be different for other regions, but this function
        and all the others are subject to change once we learn more about the
        other rulesets.

        """

        return numpy.array([2, 3, 4, 7, 8, 14, 15])

####
#   END HELPER FUNCTIONS
####







