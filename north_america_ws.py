from west.data_map import DataMap2DWithFixedBoundingBox
from west.boundary import BoundaryContinentalUnitedStatesWithStateBoundaries
import west.boundary
from west.custom_logging import getModuleLogger
import west.region
from west import protected_entities_tv_stations
from west import protected_entities_plmrs
from west import protected_entities_radio_astronomy_sites
from west.protected_entities import ProtectedEntitiesDummy

from ruleset_industrycanada2015 import *
from canada import *

class DataMap2DContinentalNorthAmerica(DataMap2DWithFixedBoundingBox):

    """:class: DataMap2D with preset bounds for continental North America,
    including Alaska."""

    latitude_bounds = [24, 84]
    longitude_bounds = [-170, -52]
    default_num_latitude_divisions = 800
    default_num_longitude_divisions = 600


class BoundaryContinentalUnitedStatesWithStateBoundariesPlusAlaska(BoundaryContinentalUnitedStatesWithStateBoundaries):
    """Continental US with Alaska"""

    def _omitted_shapes(self):
        return ["Hawaii", "Puerto Rico", "American Samoa", "Guam",
                    "Commonwealth of the Northern Mariana Islands", "United States Virgin Islands"]



class BoundaryContinentalNorthAmerica(west.boundary.BoundaryShapefile):

    """:class: BoundaryShapeFile with geometries describing
        continental North America, including Alaska
    """

    def __init__(self, *args, **kwargs):
        self.log = getModuleLogger(self)
        boundary_us_object = BoundaryContinentalUnitedStatesWithStateBoundariesPlusAlaska()
        boundary_canada_object = BoundaryCanada()
        self._geometries = boundary_us_object._geometries + boundary_canada_object._geometries

    def _geometry_name_field_str(self):
        return "NAME"

    def boundary_filename(self):
        return ""


class RegionNorthAmericaTvOnly(west.region.Region):
    """Class describing entire continental North American region."""

    # If the device's height is not specified, this height will be used.
    default_device_haat_meters = 10

    def _get_boundary_class(self):
        #North America boundary
        return BoundaryContinentalNorthAmerica

    def _load_protected_entities(self):
        self.protected_entities[
            protected_entities_tv_stations.ProtectedEntitiesTVStations] = \
            ProtectedEntitiesTVStationsUnitedStatesIncentiveAuctionAndCanadaFromFccLearn(self)

        self.protected_entities[protected_entities_plmrs.ProtectedEntitiesPLMRS] = \
            ProtectedEntitiesDummy(self)

        self.protected_entities[protected_entities_radio_astronomy_sites.ProtectedEntitiesRadioAstronomySites] = \
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
        return 6e6




