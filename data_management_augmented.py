import west.data_management
from west.propagation_model import PropagationModel


class SpecificationPLMRSMap(west.data_management.Specification):
    """
    This Specification describes a :class:`data_map.DataMap2D` which contains
    boolean data. Values will be True (or truthy) if the pixel is NOT in a location that has PLMRS exclusions applied to it.
    (Equivalently, values will be False if the pixel is in a location that has PLMRS exclusions alone applied.)
    """

    def __init__(self, region_map_spec, region_object, ruleset_object, propagation_model = None):
        # Type checking
        self._expect_of_type(region_map_spec, west.data_management.SpecificationRegionMap)
        self._expect_of_type(region_object, west.region_united_states.RegionUnitedStates)
        self._expect_of_type(ruleset_object, west.ruleset_fcc2012.RulesetFcc2012)

        # Store data
        self.region_map_spec = region_map_spec
        self._store_at_least_class("region", region_object)
        self._store_at_least_class("ruleset", ruleset_object)

        # Propagation model needs special handling
        if propagation_model is None:
            self._create_obj_if_needed("ruleset")
            propagation_model = self.ruleset_object.get_default_propagation_model()
        self._expect_of_type(propagation_model, PropagationModel)
        self._store_at_least_class("propagation_model", propagation_model)

    def to_string(self):
        return " ".join(["PLMRS_EXCLUSIONS_MAP",
                         "(%s)" % self.region_map_spec.to_string(),
                         west.data_management._make_string(self.region_class),
                         west.data_management._make_string(self.ruleset_class),
                         west.data_management._make_string(self.propagation_model_class)])

    @property
    def subdirectory(self):
        return "PLMRS_EXCLUSIONS_MAP"

    def make_data(self):
        self._create_obj_if_needed("region")
        self._create_obj_if_needed("propagation_model")
        self.ruleset_object.set_propagation_model(self.propagation_model_object)

        region_datamap = self.region_map_spec.fetch_data()

        channel_list = self.region_object.get_tvws_channel_list()
        #Hack-y
        channel_list.append(3)
        channel_list.append(4)
        channel_list = sorted(channel_list)
        plmrs_datamap3d = west.data_map.DataMap3D.from_DataMap2D(region_datamap, channel_list)
        for channel in channel_list:
            print channel
            channel_layer = plmrs_datamap3d.get_layer(channel)
            self.ruleset_object.apply_plmrs_exclusions_to_map(self.region_object, channel_layer, channel)

        self.save_data(plmrs_datamap3d)
        return plmrs_datamap3d

    def get_map(self):
        """Creates a linear-scale :class:`map.Map` with boundary outlines, a
        white background, and a colorbar. The title is automatically set
        using the Specification information but can be reset with
        :meth:`map.Map.set_title`. Returns a handle to the map object; does
        not save or show the map."""
        datamap3d = self.fetch_data()
        datamap2d = datamap3d.sum_all_layers()

        region_map = self.region_map_spec.fetch_data()
        self.region_map_spec._create_obj_if_needed("boundary")
        boundary = self.region_map_spec.boundary_object

        map = datamap2d.make_map(is_in_region_map=region_map)
        map.add_boundary_outlines(boundary)
        map.add_colorbar(decimal_precision=0)
        map.set_colorbar_label("Number of available whitespace channels (only PLMRS exclusions)")
        self._set_map_title(map)
        return map

