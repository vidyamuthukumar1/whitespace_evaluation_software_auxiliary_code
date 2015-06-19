from west.ruleset_fcc2012 import RulesetFcc2012
from west.protected_entities_tv_stations import ProtectedEntitiesTVStations
from west import helpers
from west.protected_entity_tv_station import ProtectedEntityTVStation
from west.protected_entity_plmrs import ProtectedEntityPLMRS
from west.protected_entity_radio_astronomy_site import ProtectedEntityRadioAstronomySite

from ruleset_industrycanada2015 import RulesetIndustryCanada2015

import numpy



class RulesetFcc2012WithIndustryCanada2015ProtectedContourRadii(RulesetFcc2012):

    """This class defines a ruleset which is just like the
    FCC 2012 ruleset, except that it defines protected contour radii just
    like those in the IC ruleset.
    """

    _target_ruleset = RulesetIndustryCanada2015()

    def get_tv_target_field_strength_dBu(self, is_digital, freq):
        return self._target_ruleset.get_tv_target_field_strength_dBu(is_digital, freq)



class RulesetIndustryCanada2015HybridThree(RulesetIndustryCanada2015):

    """This class defines a ruleset which is just like the Industry Canada 2015 ruleset,
    except that it does not consider far side separation distance conditions.

    #TODO: Better naming -- this name was created only to make sure the filename
    in SpecificationWhitespaceMap did not become too large
    """

    _apply_far_side_separation_distance_conditions = False


class RulesetIndustryCanada2015HybridTwo(RulesetIndustryCanada2015):

    """This class defines a ruleset which is just like the Industry Canada 2015 ruleset,
    except that it does not consider far side separation distance conditions OR
    apply taboo channel exclusions.

    #TODO: Better naming -- this name was created only to make sure the filename
    in SpecificationWhitespaceMap did not become too large
    """

    _apply_far_side_separation_distance_conditions = False
    _apply_taboo_channel_exclusions = False

class RulesetFcc2012WithTabooChannelExclusions(RulesetFcc2012):

    """This class defines a ruleset which is just like the FCC 2012 ruleset,
    but it additionally defines taboo channel exclusions.
    """

    def taboo_channel_tv_station_is_protected(self, tv_station,
                                              device_location, device_haat):

        if tv_station.is_digital():
            raise ValueError("Taboo channel protections only apply for analog TV stations")


        return self.adjacent_channel_tv_station_is_protected(tv_station, device_location, device_haat)


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
        for adj_chan in [device_channel-1, device_channel+1]:
            if not adj_chan in region.get_channel_list():
                continue
            if helpers.channels_are_adjacent_in_frequency(region, adj_chan, device_channel):
                adjacent_channel_stations += tv_stations_container.get_list_of_entities_on_channel(adj_chan)

        for station in adjacent_channel_stations:
            if self.adjacent_channel_tv_station_is_protected(station, location, device_haat):
                return False


        taboo_channel_stations = []
        list_of_taboo_channels_for_device_channel = self.get_list_of_taboo_channels(region, device_channel)
        for taboo_chan in list_of_taboo_channels_for_device_channel:
            if not taboo_chan in region.get_channel_list():
                continue
            if self.channel_is_taboo(region, taboo_chan, device_channel):
                taboo_channel_stations += tv_stations_container.get_list_of_entities_on_channel(taboo_chan)

        for station in taboo_channel_stations:
            if not station.is_digital() and self.taboo_channel_tv_station_is_protected(station, location, device_haat):
                return False

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
                            not self.cochannel_tv_station_is_protected(entity, location, device.get_haat())
                    # Portable devices are not subjected to adjacent-channel exclusions
                    elif not device.is_portable() and \
                            helpers.channels_are_adjacent_in_frequency(region, entity.get_channel(), channel):
                        location_is_whitespace &= \
                            not self.adjacent_channel_tv_station_is_protected(entity, location, device.get_haat())
                    elif not device.is_portable() and \
                            self.channel_is_taboo(region, entity.get_channel(), channel) and not entity.is_digital():
                        location_is_whitespace &= \
                            not self.taboo_channel_tv_station_is_protected(entity, location, device.get_haat())
                    else:
                        # Not protected if not cochannel or adjacent channel or taboo channel
                        continue
                elif isinstance(entity, ProtectedEntityPLMRS):
                    if channel == entity.get_channel():
                        location_is_whitespace &= not self.plmrs_is_protected(entity, location, channel, region)
                elif isinstance(entity, ProtectedEntityRadioAstronomySite):
                    location_is_whitespace &= not self.radioastronomy_site_is_protected(entity, location)
                else:
                    self.log.error("Could not apply protections for the following entity: %s" % str(entity))
                    continue

                # Don't need to check other entities if the location has already been ruled out as whitespace
                if not location_is_whitespace:
                    break

            return location_is_whitespace

        is_whitespace_datamap2d.update_all_values_via_function(update_function, verbose=verbose)



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



