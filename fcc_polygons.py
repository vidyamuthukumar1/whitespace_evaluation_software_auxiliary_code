import csv
import simplekml
import random

all_colors = [c for c in vars(simplekml.Color).values() if isinstance(c, str) and len(c) == 8]


class FccPolygon(object):
    def __init__(self, app_id, service_type, transmitter_location,
                 lonlat_coordinates, callsign_and_app_file_number):
        self.app_id = app_id
        self.service_type = service_type
        self.transmitter_location = transmitter_location
        self.lonlat_coordinates = lonlat_coordinates
        self.callsign_and_app_file_number = callsign_and_app_file_number

    def get_lonlat_coordinates(self):
        return self.lonlat_coordinates


    def add_to_kml(self, kml):
        polygon = kml.newpolygon(name=self.callsign_and_app_file_number,
                                    outerboundaryis=self.lonlat_coordinates)
        polygon.style.linestyle.color = simplekml.Color.black
        polygon.style.linestyle.width = 3
        polygon.style.polystyle.color = simplekml.Color.changealphaint(100, random.choice(all_colors))
        # polygon.description = """
        #         Channel: %d
        #         Transmitter type: %s
        #         ERP: %.2f kW
        #         HAAT: %.2f meters
        #         Latitude: %.2f
        #         Longitude: %.2f
        #         Callsign: %s
        #         Facility ID: %s
        #         """ % (tv_station.get_channel(), tv_station.get_tx_type(), tv_station.get_erp_kilowatts(),
        #                tv_station.get_haat_meters(), tv_station.get_latitude(), tv_station.get_longitude(),
        #                tv_station.get_callsign(), tv_station.get_facility_id())


class FccPolygons(object):

    def __init__(self, filename):

        self.polygons = {}

        print "*** Reading polygons from %s" % filename

        with open(filename, "r") as f:
            contour_reader = csv.reader(f, delimiter="|")

            """
            Data from:
                http://www.fcc.gov/encyclopedia/tv-service-contour-data-points
            specifically:
                ftp://ftp.fcc.gov/pub/Bureaus/MB/Databases/tv_service_contour_data/TV_service_contour_current.zip
            Example row:

            '8         ', 'TX', 'W04AE BLTT-1002                    ','43.05646 ,-74.92237 ', '43.06873 ,-74.92208 ',
            '43.06873 ,-74.92179 ', '43.06970 ,-74.92142 ', '43.06969 ,-74.92111 ', '43.06967 ,-74.92079 '
            """
            for entry in contour_reader:
                #application_id_number = int(entry[0].strip())
                application_id_number = entry[0].strip()
                service_type = entry[1].strip()
                callsign_and_app_file_number = entry[2].strip()

                transmitter_location = entry[3]

                lonlat_coordinates = []
                for i in range(4, 360+3):
                    try:
                        lat_str, lon_str = entry[i].split(",")
                        lat = float(lat_str)
                        lon = float(lon_str)
                        lonlat_coordinates.append((lon, lat))
                    except Exception as e:
                        print "Could not convert coordinates: ", e

                lonlat_coordinates.append(lonlat_coordinates[0])
                # print lonlat_coordinates


                new_polygon = FccPolygon(application_id_number, service_type,
                                         transmitter_location,
                                         lonlat_coordinates,
                                         callsign_and_app_file_number)
                #self.polygons.append(new_polygon)
                self.polygons[application_id_number] = new_polygon

    def get_poly_by_app_id(self, app_id):
        # try:
        return self.polygons[app_id]
        # except:
        #     return None

    def export_to_kml(self):
        kml = simplekml.Kml()
        for poly in self.polygons.values():
            poly.add_to_kml(kml)
