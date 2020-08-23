# Shira Levy
# Guy Chriqui
# Yam Arbel

from math import cos, sin, radians
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QBrush, QPen, QPolygon, QColor

X = Y = Z = 76

points = [

    # Cube
    [-X, -Y, -Z],
    [X, -Y, -Z],
    [-X, Y, -Z],
    [X, Y, -Z],
    [-X, -Y, Z],
    [X, -Y, Z],
    [-X, Y, Z],
    [X, Y, Z],

    # Pyramid
    [0, -Y*1.5, 0],
    [X*1.5, 0, 0],
    [0, 0, -Z*1.5],
    [-X*1.5, 0, 0],
    [0, 0, Z*1.5],
    [0, Y*1.5, 0]
]

polygons = [

    # Cube
    {"edges": [0, 1, 3, 2], "color": '#FF8399'},
    {"edges": [1, 5, 7, 3], "color": '#FFE983'},
    {"edges": [2, 3, 7, 6], "color": '#00EBC1'},
    {"edges": [4, 0, 2, 6], "color": '#8399FF'},
    {"edges": [5, 4, 6, 7], "color": '#4B00EB'},
    {"edges": [0, 4, 5, 1], "color": '#00a0eb'},

    # Pyramid
    {"edges": [8, 9, 10], "color": '#FF8399'},
    {"edges": [11, 8, 10], "color": '#FFE983'},
    {"edges": [10, 9, 13], "color": '#00EBC1'},
    {"edges": [11, 10, 13], "color": '#8399FF'},
    {"edges": [12, 11, 13], "color": '#4B00EB'},
    {"edges": [9, 12, 13], "color": '#00a0eb'},
    {"edges": [9, 8, 12], "color": '#C100EB'},
    {"edges": [8, 11, 12], "color": '#7939FF'},
]


# Polygon Object
class Polygon:
    def __init__(self, xyz_points, color):
        # points of real world coordinates
        self.xyz_points = xyz_points

        # points of projections
        self.proj_points = []

        # cube and pyramid location on canvas
        self.c_cube = [400, 350]
        self.c_pyramid = [800, 350]

        # Polygon fill color
        self.color = color

    def normal(self):
        # calculate normal of the polygon
        a = np.subtract(self.proj_points[2], self.proj_points[1])
        b = np.subtract(self.proj_points[1], self.proj_points[0])
        x = a[1] * b[2] - a[2] * b[1]
        y = a[2] * b[0] - a[0] * b[2]
        z = a[0] * b[1] - a[1] * b[0]
        return [x, y, z]

    def visibility(self):
        # Check if polygon should be visible by it's normal
        n = self.normal()
        vis = np.dot(n, [0, 0, 1])
        return vis

    def max_z(self):
        # return max z of real world coordinates
        z = []
        for p in self.xyz_points:
            z.append(p[-1])
        return max(z)

    def get_poly(self):
        # return polygon object to draw on canvas
        if len(self.proj_points) == 4:
            c = self.c_cube
        else:
            c = self.c_pyramid
        polygon_points = []
        for p in self.proj_points:
            polygon_points.append(QPoint(p[0] + c[0], p[1] + c[1]))
        return QPolygon(polygon_points)

    def parallel_orthographic(self):
        # Calculate polygon projection points by parallel orthographic method
        self.proj_points.clear()
        matrix = np.array(((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 0), (0, 0, 0, 1)))
        for p in self.xyz_points:
            self.proj_points.append(np.dot(p + [1], matrix)[:3])

    def parallel_oblique(self, degree):
        # Calculate polygon projection points by parallel oblique method
        self.proj_points.clear()
        alpha = radians(int(degree))
        matrix = np.array(((1, 0, 0, 0), (0, 1, 0, 0), (cos(alpha) * 0.5, sin(alpha) * 0.5, 1, 0), (0, 0, 0, 1)))
        for p in self.xyz_points:
            self.proj_points.append(np.dot(p + [1], matrix)[:3])

    def perspective(self, d):
        # Calculate polygon projection points by perspective method
        self.proj_points.clear()
        d = int(d)
        for p in self.xyz_points:
            z = p[2]
            s = 1 / ((z / (-500 + d)) + 1)
            matrix = np.array(((s, 0, 0, 0), (0, s, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))
            self.proj_points.append(np.dot(p + [1], matrix)[:3])


class Actions:
    def __init__(self, painter):
        # chosen projection: 1=Parallel Orthographic, 2=Parallel Oblique, 3=Perspective
        self.projection = 1
        # chosen by user parallel oblique degree
        self.parallel_oblique_degree = 0
        # chosen by user perspective degree
        self.perspective_degree = 0

        # Arrays that hold the current polygons and current points (Updates after every action/projection)
        self.current_polys = []
        self.current_points = []

        self.painter = painter

        # Initialize the first points and draw shapes
        self.initialize()

    def initialize(self):
        # save the first points at current points
        global points
        self.projection = 2
        self.parallel_oblique_degree = 150

        self.current_points.clear()
        for point in points:
            self.current_points.append(point)

        # draw shapes:
        self.sort_polys()

        for p in self.current_polys:
            # project points by parallel oblique
            p.parallel_oblique(150)
            self.draw_poly(p)

    def parallel_orthographic(self):
        # Project points to image plane by parallel orthographic method

        # flag to remember that the projection the user chooses
        self.projection = 1

        # create and sort by Z axis polygons array
        self.sort_polys()

        # draw sorted polygons
        for p in self.current_polys:

            # project points by parallel orthographic
            p.parallel_orthographic()

            self.draw_poly(p)

    def parallel_oblique(self, degree):
        self.projection = 2
        self.parallel_oblique_degree = degree

        # create and sort by Z axis polygons array
        self.sort_polys()

        # draw sorted polygons
        for p in self.current_polys:

            # project points by parallel oblique
            p.parallel_oblique(self.parallel_oblique_degree)

            self.draw_poly(p)

    def perspective(self, d):
        self.projection = 3
        self.perspective_degree = d

        # create and sort by Z axis polygons array
        self.sort_polys()
        # draw sorted polygons
        for p in self.current_polys:

            # project points by parallel oblique
            p.perspective(self.perspective_degree)

            self.draw_poly(p)

    def rotate(self, alpha, axis):
        # Rotate the shapes on the canvas by the chosen axis

        # The angle chosen by user
        alpha = radians(alpha)

        # The axis chosen by user
        if axis == 'x':
            matrix = np.array(((1, 0, 0, 0), (0, cos(alpha), sin(alpha), 0), (0, -sin(alpha), cos(alpha), 0), (0, 0, 0, 1)))
        if axis == 'y':
            matrix = np.array(((cos(alpha), 0, -sin(alpha), 0), (0, 1, 0, 0), (sin(alpha), 0, cos(alpha), 0), (0, 0, 0, 1)))
        if axis == 'z':
            matrix = np.array(((cos(alpha), sin(alpha), 0, 0), (-sin(alpha), cos(alpha), 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)))

        self.update_xyz(matrix)

        # Draw shapes on canvas by the projection chosen by user
        self.draw()

    def scale(self, op):
        # Update size to scale to
        if op == '+':
            size = 0.95
        elif op == '-':
            size = 1.05

        # Scale matrix
        matrix = np.array(((1 / size, 0, 0, 0), (0, 1 / size, 0, 0), (0, 0, 1 / size, 0), (0, 0, 0, 1)))

        self.update_xyz(matrix)

        # draw
        self.draw()

    def sort_polys(self):
        # sort the polygons by z axis and create array of Polygon object
        global polygons
        self.current_polys.clear()

        for pol in polygons:
            # Create polygon object
            polygon_points = []
            for i in pol["edges"]:
                polygon_points.append(self.current_points[i])
            self.current_polys.append(Polygon(polygon_points, pol["color"]))

        self.current_polys.sort(key=lambda x: x.max_z())

    def draw(self):
        if self.projection == 1:
            self.parallel_orthographic()
        elif self.projection == 2:
            self.parallel_oblique(self.parallel_oblique_degree)
        elif self.projection == 3:
            self.perspective(self.perspective_degree)

    def draw_poly(self, poly):
        # check visibility
        if poly.visibility() >= 0:
            # set pen to draw
            self.painter.setBrush(QBrush(QColor(poly.color), Qt.Dense4Pattern))
            pen = QPen(Qt.transparent, 0, Qt.SolidLine)
            self.painter.setPen(pen)

            # draw polygon
            self.painter.drawPolygon(poly.get_poly())

    def update_xyz(self, matrix):
        new_points = []
        # calculate new XYZ points in real world coordinates
        for point in self.current_points:
            point = np.dot(point + [1], matrix)[:3]
            new_points.append([point[0], point[1], point[2]])

        # Update current points with the new points
        self.current_points.clear()
        self.current_points = new_points
