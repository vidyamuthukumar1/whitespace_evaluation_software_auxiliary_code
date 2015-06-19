from west.population import PopulationNugget, PopulationData, ShapefilePopulationData
from west.custom_logging import getModuleLogger


import os
import csv
import fiona
import shapely

from shapely.geometry import shape

class PopulationDataCanada2011(ShapefilePopulationData):
    """
    Population data for Canada based on the 2011 census.
    All data obtained from the Statistics Canada website:
    http://www.statcan.gc.ca/start-debut-eng.html

    """

    def _read_shapefile(self, filename):
        """
        Read the shapefile specified by :meth:`boundary_filename`. Provides
        support for multi-part polygons.

        .. note:: Had to copy this function from west.population and add
        functionality that allows the creation of clean zero-buffer
        multipolygons.
        """
        geometries_and_properties = []

        with fiona.open(filename, "r") as source:
            for f in source:
                try:
                    geom = shape(f['geometry'])
                    if not geom.is_valid:
                        clean = geom.buffer(0.0)
                        assert clean.is_valid
                        assert clean.geom_type in ['Polygon', 'MultiPolygon']
                        geom = clean
                    geometries_and_properties.append((geom, f['properties']))
                except Exception as e:
                    self.log.error(
                        "Error reading in %s: %s" % (filename, str(e)))

        return geometries_and_properties

    def data_year(self):
        return 2011

    def geography_source_name(self):
        return "2011 Census - Boundary files"

    def population_source_name(self):
        return "Census profile - Comprehensive download files for a selected geographic level: CSV or TAB"

    def resolution_description(self):
        return "Census tracts"

    def geography_source_filenames(self):

        """Data source: Statistics Canada
           http://www12.statcan.gc.ca/census-recensement/2011/geo/bound-limit/bound-limit-2011-eng.cfm
        """

        return [os.path.join("data", "Region", "Canada", "Population", str(self.data_year()), "gct_000b11a_e.shp")]

    def population_source_filenames(self):

        """Data source: Statistics Canada
           http://www12.statcan.gc.ca/census-recensement/2011/dp-pd/prof/details/download-telecharger/comprehensive/comp-csv-tab-dwnld-tlchrgr.cfm?Lang=E#tabs2011
        """

        return [os.path.join("data", "Region", "Canada", "Population", str(self.data_year()), "98-316-XWE2011001-401.CSV")]

    def _load_geography(self):
        geometries_and_properties = []
        for filename in self.geography_source_filenames():
            geometries_and_properties += self._read_shapefile(filename)

        for (geometry, properties) in geometries_and_properties:

            # Sample properties:
            # ([(u'CTUID', u'5750015.00'), (u'CTNAME', u'0015.00'), (u'CMAUID', u'575'), (u'CMANAME', u'North Bay'),
            # (u'CMATYPE', u'K'), (u'CMAPUID', u'35575'), (u'PRUID', u'35'), (u'PRNAME', u'Ontario')])

            # Identifier: 'CTUID'
            identifier = properties['CTUID']
            if identifier not in self._population_nuggets_by_identifier:
                self._population_nuggets_by_identifier[
                    identifier] = PopulationNugget(identifier)

            self._population_nuggets_by_identifier[identifier].add_geometry(
                geometry)

    def _load_populations(self):
        population_filename = self.population_source_filenames()[0]
        with open(population_filename, "r") as f:
            population_csv = csv.DictReader(f)

            for row in population_csv:
                identifier = row['Geo_Code']
                population = row['Total']

                topic = row['Topic']
                if topic != 'Population and dwelling counts':
                    self.log.debug("Skipping entry that does not contain any information about population")
                    continue
                characteristic = row['Characteristic']
                if characteristic != "Population in %s"%self.data_year():
                    self.log.debug("Skipping entry that does not contain information about population in %s"%self.data_year())
                    continue

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






