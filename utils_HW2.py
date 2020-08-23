# Shira Levy 305451833
# Guy Chriqui 203137641
# Yam Arbel  204209332

import sys
import math
import numpy as np
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor, QPainter, QPen
from utils_HW1 import Draw


class Shape:
    def __init__(self, points, color, width, shape):
        super().__init__()
        self.points = points
        self.color = color
        self.width = width
        self.shape = shape


class TransformationImage:

    def __init__(self, draw):
        super().__init__()

        self.originImage = []
        self.currentImage = []
        self.Draw = draw
        self.mouseLastPoint = 0

    # Draw image from text file
    def DrawFromFile(self, painter, file):

        # Reset last click
        self.mouseLastPoint = 0
        # Open text file to  read from
        textFile = open(file, "r")
        # Read all string from it
        DrawString = textFile.read()
        # Split string to arrays of pixels
        actions = DrawString.split('\n')
        # Create image from  actions
        try: self.CreateImage(painter, actions)
        except : return False
        # Save origin to current
        self.currentImage = self.originImage
        # Draw image
        self.DrawFromImage(painter, self.originImage)
        return True

    # Create Image from actions/shapes and save it to origin
    def CreateImage(self, painter, actions):
        # Run over all actions and create shapes
        for action in actions:
            # Parse last action
            actionString = action
            mode, pointsString, color, width = actionString.split('=')
            # Init points
            points = []
            # Make array of points
            pointsString = pointsString.split('&')
            # Create QPoints
            for point in pointsString:
                x, y = point.split(',')
                points.append(QPoint(int(x), int(y)))
            # Add Shape
            self.originImage.append(Shape(points, color, int(width), mode))

    # Draw image from array of shapes
    def DrawFromImage(self, painter, image, save=False):
        # Save current pen data
        p = painter.pen()
        # Run over shapes and draw them
        for shape in image:
            # Create action pen
            aPen = QPen()
            aPen.setColor(QColor(shape.color))
            aPen.setWidth(shape.width)
            painter.setPen(aPen)
            # Draw shape
            self.Draw.update(painter, shape.points.copy(), shape.shape , shape.color, shape.width, save)
        # Return prev pen
        painter.setPen(p)


    # Return image center and bottom left point 
    def GetCurrentImageCenter(self):
        # Init
        points = []
        maxY = 0
        minX = 1280
        # Join  all x and y points
        for shape in self.currentImage:
            for point in shape.points:
                # Add point to point array
                points.append(point)
                # Save max y and min x for bottom left point
                if point.y() > maxY : maxY = point.y()
                if point.x() < minX : minX = point.x()
        # Creat vectors of x and y
        x = [p.x() for p in points]
        y = [p.y() for p in points]
        # Sum and divide to get center
        centroid = (int(sum(x) / len(points)), int(sum(y) / len(points)))
        # Return
        return centroid, QPoint(minX, maxY)


    # Move image to (0,0) point
    def MoveImageToOrigin(self, painter):
        center, _ = self.GetCurrentImageCenter()
        self.Move(painter,-(center[0]),-(center[1]), draw=False)
        return center
    

    # Multiple all shapes in matrix
    def UpdatePoints(self, matrix, dim=3, mirror=False, center=(1280,720)):
        # Run on shapes
        for shape in self.currentImage:
            newPoints = []
            for point in shape.points :
                x = point.x()
                y = point.y()
                if dim ==3 :
                    x, y, _ = np.dot([x, y, 1], matrix)
                else : x, y = np.dot([x, y], matrix)
                if mirror: x += center[0]
                newPoints.append(QPoint(x, y))
            shape.points = newPoints


    def Scaling(self, painter, _size):
        # Update size to scale to
        if _size == '+': size = 0.95
        else: size = 1.05

        # Get image origin and save center
        center = self.MoveImageToOrigin(painter)
        # Create scaling matrix
        matrix = np.array(((1/size, 0, 0), (0, 1/size, 0), (0, 0, 1)))
        # Mutiple all shapes in matrix
        self.UpdatePoints(matrix)
        # Move back image to it center
        self.Move(painter, center[0], center[1], draw=False)
        # Draw new image
        self.DrawFromImage(painter, self.currentImage)


    def Move(self, painter, moveX=20, moveY=0, draw=True):
        # Create transletion matrix
        matrix = np.array(((1, 0, 0), (0, 1, 0), (moveX, moveY, 1)))
        # Mutiple all shapes in matrix
        self.UpdatePoints(matrix)
        # Draw new image
        if draw : self.DrawFromImage(painter, self.currentImage)

    def Rotation(self, painter, radius=5):
        # Get image origin and save center
        center = self.MoveImageToOrigin(painter)
        # Make radians
        radius = np.radians(radius)
        # Create rotation matrix
        matrix = np.array(((np.cos(radius), np.sin(radius)), (-(np.sin(radius)), np.cos(radius))))
        # Mutiple all shapes in matrix
        self.UpdatePoints(matrix, dim=2)
        # Move back image to it center
        self.Move(painter, center[0], center[1], draw=False)
        # Draw new image
        self.DrawFromImage(painter, self.currentImage)


    def Mirroring(self, painter):
        # Get image origin and save center
        center, _ = self.GetCurrentImageCenter()
        # Create Mirroring matrix
        matrix = np.array(((-1, 0), (0, 1)))        
        # Mutiple all shapes in matrix
        self.UpdatePoints(matrix, 2, True, center)
        # Move back image to it center X
        self.Move(painter, center[0], 0, draw=False)
        # Draw new image
        self.DrawFromImage(painter, self.currentImage)


    def Shearing(self, painter, point):
        # Save clicked mouse
        if self.mouseLastPoint == 0 : self.mouseLastPoint = point.x()
        # Get left bottom point of image
        _ , leftBottomPoint = self.GetCurrentImageCenter()
        # Calculate a
        a = -np.tanh((point.x() - self.mouseLastPoint) / (1280 / 10))
        # Save new release as last clicked mouse
        self.mouseLastPoint = point.x()
        # Move image to origin
        self.Move(painter, -(leftBottomPoint.x()), -(leftBottomPoint.y()), draw=False)
        # Create Shearing matrix
        matrix = np.array(((1, 0, 0), (a, 1, 0), (0, 0, 1)))
        # Mutiple all shapes in matrix
        self.UpdatePoints(matrix)
        # Move back image to it center
        self.Move(painter, leftBottomPoint.x(), leftBottomPoint.y(), draw=False)
        # Draw new image
        self.DrawFromImage(painter, self.currentImage)