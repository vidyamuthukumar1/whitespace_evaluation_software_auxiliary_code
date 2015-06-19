from osgeo import ogr, osr



class BufferMaker(object):

    def __init__(self):
        # EPSG:4326 : WGS84 lat/lon : http://spatialreference.org/ref/epsg/4326/
        self.wgs = osr.SpatialReference()
        self.wgs.ImportFromEPSG(4326)
        self.coord_trans_cache = {}


    def utm_zone(self, lat, lon):
        """Args for osr.SpatialReference.SetUTM(int zone, int north = 1)"""
        return int(round(((float(lon) - 180) % 360)/6)), int(lat > 0)


    def add_buffer(self, original_lonlat_points, buffer_dist_km):

        lon1, lat1 = original_lonlat_points[0]

        # Get projections sorted out for that UTM zone
        cur_utm_zone = self.utm_zone(lat1, lon1)
        if cur_utm_zone in self.coord_trans_cache:
            self.wgs2utm, self.utm2wgs = self.coord_trans_cache[cur_utm_zone]
        else: # define new UTM Zone
            utm = osr.SpatialReference()
            utm.SetUTM(*cur_utm_zone)
            # Define spatial transformations to/from UTM and lat/lon
            self.wgs2utm = osr.CoordinateTransformation(self.wgs, utm)
            self.utm2wgs = osr.CoordinateTransformation(utm, self.wgs)
            self.coord_trans_cache[cur_utm_zone] = self.wgs2utm, self.utm2wgs

        ring = ogr.Geometry(ogr.wkbLinearRing)
        for (lon, lat) in original_lonlat_points:
            ring.AddPoint(lon, lat)
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(ring)

        original_wkt = poly.ExportToWkt()

        # Project to UTM
        res = poly.Transform(self.wgs2utm)
        if res != 0:
            print("spatial transform failed with code " + str(res))
        # print(original_wkt + " -> " + poly.ExportToWkt())
        #
        # print("Original area: " + str(poly.GetArea()/1e6) + " km^2")


        # Compute a 15 km buffer
        buff = poly.Buffer(buffer_dist_km*1000)
        # print("Area: " + str(buff.GetArea()/1e6) + " km^2")
        # Transform UTM buffer back to lat/long
        res = buff.Transform(self.utm2wgs)
        if res != 0:
            print("spatial transform failed with code " + str(res))
        # print("Envelope: " + str(buff.GetEnvelope()))
        # print("WKT: " + buff.ExportToWkt())

        # print "New polygon: ", buff

        buffer_coordinates = []
        for coord in self.get_coordinates(buff)[0]:
            buffer_coordinates.append((coord[0], coord[1]))

        return buffer_coordinates




    def get_coordinates(self, geometry):
        gtype = geometry.GetGeometryType()
        geom_count = geometry.GetGeometryCount()
        coordinates = []

        if gtype == ogr.wkbPoint or gtype == ogr.wkbPoint25D:
            return [geometry.GetX(0), geometry.GetY(0)]

        if gtype == ogr.wkbMultiPoint or gtype == ogr.wkbMultiPoint25D:
            geom_count = geometry.GetGeometryCount()
            for g in range(geom_count):
                geom = geometry.GetGeometryRef(g)
                coordinates.append(self.get_coordinates(geom))
            return coordinates

        if gtype == ogr.wkbLineString or gtype == ogr.wkbLineString25D:
            points = []
            point_count = geometry.GetPointCount()
            for i in range(point_count):
                points.append([geometry.GetX(i), geometry.GetY(i)])
            return points

        if gtype == ogr.wkbMultiLineString or gtype == ogr.wkbMultiLineString25D:
            coordinates = []
            geom_count = geometry.GetGeometryCount()
            for g in range(geom_count):
                geom = geometry.GetGeometryRef(g)
                coordinates.append(self.get_coordinates(geom))
            return coordinates

        if gtype == ogr.wkbPolygon or gtype == ogr.wkbPolygon25D:
            geom = geometry.GetGeometryRef(0)
            coordinates = self.get_coordinates(geom)
            return [coordinates]

        if gtype == ogr.wkbMultiPolygon or gtype == ogr.wkbMultiPolygon25D:

            coordinates = []
            geom_count = geometry.GetGeometryCount()
            for g in range(geom_count):
                geom = geometry.GetGeometryRef(g)
                coordinates.append(self.get_coordinates(geom))
            return coordinates



# import simplekml
# kml = simplekml.Kml()
#
#
# def add_poly_to_kml(kml, name, lonlat_coordinates, color):
#     kml_poly = kml.newpolygon()
#     kml_poly.name = name
#
#     print "Exporting coordinates: ", lonlat_coordinates
#     # lonlat_coordinates.append(lonlat_coordinates[0])
#     kml_poly.outerboundaryis.coords = lonlat_coordinates
#     kml_poly.style.polystyle.color = simplekml.Color.changealphaint(100, color)
#
#     kml_poly.description = name
#
#
# bm = BufferMaker()
#
#
# center_lat = 40
# center_lon = -110
# latitude_width = 1.0
# longitude_width = 1.0
# max_lat = center_lat + latitude_width/2
# min_lat = center_lat - latitude_width/2
# max_lon = center_lon + longitude_width/2
# min_lon = center_lon - longitude_width/2
#
# box = [(min_lon, max_lat), (max_lon, max_lat), (max_lon, min_lat),
#        (min_lon, min_lat)]
# box.append(box[0])
# lons = [lon for lon, lat in box]
# lats = [lat for lon, lat in box]
#
# print "Box: ", box
#
#
# add_poly_to_kml(kml, "Original polygon", box, simplekml.Color.blue)
#
# buffer_coordinates = bm.add_buffer(box, 25)
# add_poly_to_kml(kml, "Buffered_polygon", buffer_coordinates,
#                 simplekml.Color.red)
#
# kml.save("buffer_test2.kml")
#
