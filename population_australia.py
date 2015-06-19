from west.population import PopulationNugget, PopulationData, ShapefilePopulationData
from west.custom_logging import getModuleLogger


import os
import csv
import fiona
import shapely

from shapely.geometry import shape

class PopulationDataAustralia2006(ShapefilePopulationData):
    """
    Population data for Australia based on the 2006 census.
    Data was obtained from the Australian Bureau of Statistics
    2064.0 CDATA available online:
    http://www.abs.gov.au/AUSSTATS/abs@.nsf/Lookup/2064.0Main+Features12006?OpenDocument

    ..note:: 17 census tracts do not have valid tract geometries corresponding to them.
    The nuggets corresponding to these tracts are therefore pruned, and we are neglecting
    0.2% of Australia's population in our calculations.

    """

    def data_year(self):
        return 2006

    def geography_source_name(self):
        return "2006 Census - Boundary files"

    def population_source_name(self):
        return "Census profile - Comprehensive download files for a selected geographic level: CSV or TAB"

    def resolution_description(self):
        return "Census tracts"

    def geography_source_filenames(self):

        """
        Data obtained from the Australian Bureau of Statistic's 2006 census:
        http://www.abs.gov.au/AUSSTATS/abs@.nsf/Lookup/2064.0Main+Features12006?OpenDocument

        #TODO: Verify: was the shapefile also obtained from here?
        """

        return [os.path.join("data", "Region", "Australia", "Population", "POA06aAUST_region.shp")]

    def population_source_filenames(self):

        """
        Data obtained from the Australian Bureau of Statistic's 2006 census:
        http://www.abs.gov.au/AUSSTATS/abs@.nsf/Lookup/2064.0Main+Features12006?OpenDocument
        """

        return [os.path.join("data", "Region", "Australia", "Population", "Population2006_corrected.csv")]

    def _load_geography(self):
        geometries_and_properties = []
        for filename in self.geography_source_filenames():
            geometries_and_properties += self._read_shapefile(filename)

        for (geometry, properties) in geometries_and_properties:

            # Sample properties:
            # ([(u'STATE_2006', u'9'), (u'POA_2006', u'6799')])

            # Identifier: 'POA_2006'
            identifier = properties['POA_2006']
            if identifier not in self._population_nuggets_by_identifier:
                self._population_nuggets_by_identifier[
                    identifier] = PopulationNugget(identifier)

            self._population_nuggets_by_identifier[identifier].add_geometry(
                geometry)

    def _load_populations(self):
        population_filename = self.population_source_filenames()[0]
        with open(population_filename, "r") as f:
            population_csv = csv.reader(f)

            for row in population_csv:
                #Sample row: [Identifier: 800, Male population: 1482, Female population: 999]
                #TODO: No headers given in the CSV file so make sure that male and female population are actually in that order. Just made a guess.

                identifier = row[1]
                population = int(row[2]) + int(row[3])

                if identifier not in self._population_nuggets_by_identifier:
                    self._population_nuggets_by_identifier[
                        identifier] = PopulationNugget(identifier)

                try:
                    self._population_nuggets_by_identifier[
                        identifier].add_population(population)
                except ValueError:
                    self._population_nuggets_by_identifier[identifier]._population = None

    def add_to_kml(self, geometry, kml):

        """ Added functionality to visualize geometries of census tracts on Google Earth.

        Inspiration was taking from west.boundary"""
        added_polys = []
        for (lats, lons) in self.get_sets_of_exterior_coordinates_of_a_geometry(geometry):
            coords = zip(lons, lats)
            coords.append(coords[0])    # close the polygon

            poly = kml.newpolygon()
            poly.outerboundaryis.coords = reversed(coords)
            added_polys.append(poly)

        return added_polys

    def get_sets_of_exterior_coordinates_of_a_geometry(self, geometry):

        """Added functionality to support the above function self.add_to_kml() to visualize
        geometries of census tracts on Google Earth.

        Inspiration was taken from west.boundary"""

        polygons = []
        if isinstance(geometry, shapely.geometry.polygon.Polygon):
            polygons.append(geometry)
        elif isinstance(geometry, shapely.geometry.multipolygon.MultiPolygon):
            for poly in geometry:
                polygons.append(poly)

        sets_of_coordinates = []
        for polygon in polygons:
            e = polygon.exterior
            (lons, lats) = e.coords.xy
            sets_of_coordinates.append((lats, lons))

        return sets_of_coordinates
