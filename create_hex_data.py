"""
Create hex data.
Use it to study capacity.

Creating hex data:
Height of TV tower = ?
Radius limits = (50 m, 100 km)
Power = 1 (?? no, actually ?)
Number of points (i.e. number of devices in one cell) = 250
List of areas of hex we consider is in area_array:
area_array = logspace(log10(pi*(.05)^2), log10(pi*(100)^2), 65);
Create datamap3Ds for signal as well as noise. Layers: channels, each layer: axb matrix where a - area index, b - point index

Now iterate through the area array. Get hex parameters for area array - hex area, hex side length, hex width, hex height.
Get the set of hexagons which will interfere the center one. Set the center one as the one where transmission occurs. Look in get_hexagon_grid.m
Get the uniformly distributed set of points around the tower area (if regular whitespace devices, if WiFi devices, uniformly distributed around a radius of 0.1 km.)

We can now get signal strengths as function of distance from the hex center.

Now, for calculation of noise, add in more points outside the immediate range of hexagons. Add 10 points each at different outer radii from the origin, equally spaced in angles.
Compute noise.
"""


from west.propagation_model_fcurves import PropagationModelFcurvesWithoutTerrain, PropagationCurve
import west.region_united_states
import west.device
import numpy
import math
from shapely.geometry import Point, MultiPoint, Polygon
from copy import copy

class Hexagon(object):
    def __init__(self, sidelength, width, height):
        self._sidelength = sidelength
        self._width = width
        self._height = height
        #Default xcoord and ycoord = 0.
        self._center = (0, 0)
        self._xv = numpy.array([-(self._width/2 - self._sidelength/2), self._width/2 - self._sidelength/2, self._width/2, self._width/2 - self._sidelength/2, -(self._width/2 - self._sidelength/2), -self._width/2, -(self._width/2 - self._sidelength/2)])
        self._yv = numpy.array([self._height/2, self._height/2, 0, -self._height/2, -self._height/2, 0, self._height/2])
        self._polygon = Polygon(self._xv, self._yv)
        self._active = 1 #default
        self._power = 1 #default

    def get_x_and_y_coordinates_individually(self):
        return self._xv, self._yv

    def get_x_and_y_coordinates_as_points(self):
        extpoints = []
        for i in range(len(self._xv)):
            extpoints.append(Point(self._xv[i], self._yv[i]))

        return extpoints

    def translate_polygon(self):
        self._xv = self._xv + self._center[0]
        self._yv = self._yv + self._center[1]
        self._polygon = Polygon(self._xv, self._yv)

    def get_polygon(self):
        return self._polygon




    def get_sidelength(self):
        return self._sidelength

    def get_width(self):
        return self._width

    def get_height(self):
        return self._height

    def get_center(self):
        return self._center



    def set_center(self, center_x, center_y):
        self._center = (center_x, center_y)

class HexagonData(object):
    def __init__(self, txheight = 100, rmin = 0.05, rmax = 100, power = 1, num_points = 250, size_of_area_array = 65):
        self._tx_tower_height = txheight
        self._min_area = numpy.pi * rmin * rmin
        self._max_area = numpy.pi * rmax * rmax
        self._tx_power = power
        self._num_points_in_hexagon = num_points
        self._array_of_areas = numpy.zeros(1, size_of_area_array)
        self._hex_sidelengths = numpy.zeros(1, size_of_area_array)
        self._hex_widths = numpy.zeros(1, size_of_area_array)
        self._hex_heights = numpy.zeros(1, size_of_area_array)
        self._hexagons = {}

    def load_and_clip_area_array(self, area_array):
        clipmintrue = area_array < self._min_area
        clipmin = numpy.ones(1, len(area_array)) * self._min_area
        clipmaxtrue = area_array > self._max_area
        clipmax = numpy.ones(1, len(area_array)) * self._max_area
        self._array_of_areas = clipmintrue * clipmin + clipmaxtrue * clipmax + (1 - clipmintrue) * (1 - clipmaxtrue) * area_array



    def set_hex_parameters(self):
        self._hex_sidelengths = numpy.sqrt(self._array_of_areas * 2/(3 * numpy.sqrt(3)))
        self._hex_widths = 2 * self._hex_sidelengths
        self._hex_heights = numpy.sqrt(3) * self._hex_sidelengths

    def get_area_array(self):
        return self._array_of_areas

    def get_hex_sidelengths(self):
        return self._hex_sidelengths

    def get_hex_widths(self):
        return self._hex_widths

    def get_hex_heights(self):
        return self._hex_heights

    def get_num_points(self):
        return self._num_points_in_hexagon



    def get_hexagon_grid(self, center, area, x_width, y_width):
        hexagons = []
        sidelength = self.get_hex_sidelengths()[list(self.get_area_array()).index(area)]
        height = self.get_hex_heights()[list(self.get_area_array()).index(area)]
        width = self.get_hex_widths()[list(self.get_area_array()).index(area)]

        distance_limit = max(x_width, y_width)

        #Understand these equations
        grid_size = numpy.ceil(distance_limit/height) * 2 + 1
        grid_height = height * grid_size
        grid_width = (width + sidelength)/2 * grid_size

        for i in range(grid_size):
            for j in range(grid_size):
                idx = (i - 1) * grid_size + j
                hexagon = Hexagon(sidelength, width, height)


                #Understand these equations
                tower_x = (width - sidelength/2) * (i - 1/2)
                tower_y = height*(j - 1/2 * numpy.mod(i,2))

                center_x = tower_x + center[0] - grid_width / 2
                center_y = tower_y + center[1] - grid_height / 2
                hexagon.set_center(center_x, center_y)
                hexagon.translate_polygon()
                hexagons.append(hexagon)

        return hexagons

    def get_hexagon_points(self, num_points, area):
        sidelength = numpy.sqrt(self._array_of_areas * 2/(3 * numpy.sqrt(3)))
        height = 2 * self._hex_sidelengths
        width = numpy.sqrt(3) * self._hex_sidelengths
        xmin = -width/2
        xmax = width/2

        ymin = -height/2
        ymax = height/2

        hexagon = Hexagon(sidelength, width, height)
        xpoints = numpy.zeros(1, num_points)
        ypoints = numpy.zeros(1, num_points)
        count = 0
        while count < num_points:
            xpt = xmin + (xmax - xmin) * numpy.random.rand()
            ypt = ymin + (ymax - ymin) * numpy.random.rand()
            pt = Point((xpt, ypt))
            if pt.within(hexagon.get_polygon()):
                xpoints[count] = xpt
                ypoints[count] = ypt
                count = count + 1
            else:
                continue

        xpoints = xpoints / width
        ypoints = ypoints/ height

        return xpoints, ypoints

    def add_points_outside(self, num_angle_points, max_inner_radius, tower_area):

        def rect(r, theta):
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            return x, y

        inner_radii = numpy.logspace(numpy.log(max_inner_radius)/numpy.log(10), numpy.log(900)/numpy.log(10), 10)
        outer_radii = numpy.concatenate(inner_radii[1:], [1000])
        ring_widths = outer_radii - inner_radii

        outer_areas = numpy.pi * outer_radii * outer_radii
        inner_areas = numpy.pi * inner_radii * inner_radii
        ring_areas = outer_areas - inner_areas

        avg_distance_of_rings_to_origin = outer_radii - ring_widths/2

        angle_array = numpy.linspace(0, 2 * numpy.pi, num_angle_points)

        points_radii = numpy.zeros(1, num_angle_points * len(avg_distance_of_rings_to_origin))
        points_ring_areas = numpy.zeros(1, len(points_radii))
        count = 0
        for i in range(len(avg_distance_of_rings_to_origin)):
            for j in range(len(angle_array)):
                points_ring_areas[count] = ring_areas[i]
                points_radii[count] = avg_distance_of_rings_to_origin[i]
                count = count + 1
            count = count + 1

        points_angles = numpy.zeros(1, len(points_radii))
        count = 0
        for d in avg_distance_of_rings_to_origin:
            for j in range(len(angle_array)):
                points_angles[i] = angle_array[j]
                count = count + 1
            count = count + 1

        #Did not understand this.
        points_ring_powers = (points_ring_areas / num_angle_points) / tower_area

        points_x = numpy.zeros(1, len(points_radii))
        points_y = numpy.zeros(1, len(points_radii))

        for i in range(len(points_radii)):
            points_x[i], points_y[i] = rect(points_radii[i], points_angles[i])

        return points_x, points_y, points_ring_powers











is_wifi = False

channel_list = range(2, 52)
channel_list.remove(37)
testreg = west.region_united_states.RegionUnitedStates()
device = west.device.Device(0, 30, 1)
pm = PropagationModelFcurvesWithoutTerrain()
pl_function = lambda *args, **kwargs: pm.get_pathloss_coefficient(*args, curve_enum=PropagationCurve.curve_50_90, **kwargs)


hexdata = HexagonData()
areaarray = numpy.logspace(numpy.log(numpy.pi * 0.05 * 0.05)/numpy.log(10), numpy.log(numpy.pi * 100 * 100)/numpy.log(10), 65)

noises = {}
signals = {}

for c in channel_list:
    noises[c] = {}
    signals[c] = {}
    for a in areaarray:
        noises[c][a] = numpy.zeros(1, hexdata.get_num_points())
        signals[c][a] = numpy.zeros(1, hexdata.get_num_points())


hexdata.load_and_clip_area_array(areaarray)
hexdata.set_hex_parameters()
grid_size = 8
for i in range(65):
    hexagons = hexdata.get_hexagon_grid([0, 0], areaarray[i], hexdata.get_hex_widths()[i] * grid_size, hexdata.get_hex_heights()[i] * grid_size)
    num_towers = len(hexagons)
    hexcenters_x = numpy.zeros(1, num_towers)
    hexcenters_y = numpy.zeros(1, num_towers)
    for i in range(num_towers):
        hexcenters_x[i] = hexagons[i].get_center()[0]
        hexcenters_y[i] = hexagons[i].get_center()[1]
    tx_idx = numpy.ceil(num_towers/2)
    tx_center_x = hexcenters_x[tx_idx]
    tx_center_y = hexcenters_y[tx_idx]
    if is_wifi:
        wifi_radius = 0.1
        xpoints, ypoints = hexdata.get_hexagon_points(num_points, numpy.pi * wifi_radius * wifi_radius)
    else:
        xpoints, ypoints = hexdata.get_hexagon_points(hexdata.get_num_points(), areaarray[i])

    xpoints = xpoints + tx_center_x
    ypoints = ypoints + tx_center_y

    hexcenters_x_for_calculation = copy(hexcenters_x)
    hexcenters_y_for_calculation = copy(hexcenters_y)
    numpy.delete(hexcenters_x_for_calculation, tx_idx)
    numpy.delete(hexcenters_y_for_calculation, tx_idx)

    num_angle_points = 10
    max_inner_radius = numpy.sqrt(math.pow(max(hexcenters_x_for_calculation), 2) + math.pow(max(hexcenters_y_for_calculation), 2))
    xpoints_outsidehex, ypoints_outsidehex, powers_outsidehex = hexdata.add_points_outside(num_angle_points, max_inner_radius, areaarray[i])
    hexcenters_x_for_calculation = numpy.concatenate(hexcenters_x_for_calculation, xpoints_outsidehex)
    hexcenters_y_for_calculation = numpy.concatenate(hexcenters_y_for_calculation, ypoints_outsidehex)
    powers_of_hexes = numpy.concatenate(numpy.ones(1, num_towers - 1), powers_outsidehex)

    distance_of_devices_to_center =  numpy.sqrt((tx_center_x - xpoints) * (tx_center_x - xpoints) + (tx_center_y - ypoints) * (tx_center_y - ypoints))

    for p in range(hexdata.get_num_points()):
        distances_of_interfering_towers_to_point = numpy.sqrt(math.pow(hexcenters_x_for_calculation - xpoints[p], 2) + math.pow(hexcenters_y_for_calculation - ypoints[p], 2))
        for c in channel_list:
            noises[c][areaarray[i]][p] = 0
            signals[c][areaarray[i]][p] = pl_function(distance_of_devices_to_center[p], frequency = testreg.get_center_frequency(c),
                                                      tx_height = device.get_haat_meters(),
                                                      rx_height = None)
            for d in distances_of_interfering_towers_to_point:
                noises[c][areaarray[i][p]] += pl_function(d, frequency=testreg.get_center_frequency(c),
                                                            tx_height= device.get_haat_meters(),
                                                          rx_height=None)


with open("noisestrength_hex_data.pkl", 'w') as f:
    pickle.dump(noises, f)

with open("signalstrength_hex_data.pkl", 'w') as f:
    pickle.dump(signals, f)



















































