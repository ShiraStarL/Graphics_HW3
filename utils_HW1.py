# Shira Levy 305451833
# Guy Chriqui 203137641
# Yam Arbel  204209332

import sys
import math
import numpy as np
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor, QPainter, QPen


class Draw():

    def __init__(self):
        super().__init__()
        self.CurrentDraw = []

    # Check if there is anything to paint
    def update(self, painter, points, mode, color, width, addAction=True):
        # Save points for of action
        _points = np.array(points, copy=True)
        # Check mode status and draw
        if mode == 'Point':
            self.PutPixel(painter, points.pop())
            if addAction : self.SaveAction(_points, mode, QColor(color), width)
        elif mode == 'Line':
            action = self.MyLine(painter, points)
            if action and addAction : self.SaveAction(_points, mode, QColor(color), width)
        elif mode == 'Circel':
            action = self.MyCircle(painter, points)
            if action and addAction : self.SaveAction(_points, mode, QColor(color), width)
        elif mode == 'Curve':
            action = self.MyCurve(painter, points)
            if action and addAction : self.SaveAction(_points, mode, QColor(color), width)
        elif mode == 'Undo':
            self.UndoAction(painter, points.pop())
            

    # Save the last action/draw
    def SaveAction(self, points, action, color, width):
        # Init action string
        actionString = ''
        # Add action mode
        actionString += action + '='
        # Run over points and add to action string
        for point in points:
            actionString += str(point.x()) + ',' + str(point.y()) + '&'
        # Add action to CurrentDraw
        self.CurrentDraw.append(actionString[:-1] + '=' + str(color.name()) + '=' + str(width) + '\n')


    # Draw point/pixel in (x,y) position
    def PutPixel(self, painter, point):
        painter.drawPoint(point.x(), point.y())


    # Round corners from top
    def RoundUp(self, p):
        return int(p + 0.5)


    # Round corners from down
    def RoundDown(self, p):
        return int(p - 0.5)


    # Draw line between 2 points
    def MyLine(self, painter, points):
        # If we dont have 2 points yet return
        if len(points) < 2 : return False

        # pop the first point and save it as x1,y1
        point = points.pop()
        x1, y1 = point.x(), point.y()

        # pop the seconde point and save it as x2,y2
        point = points.pop()
        x2, y2 = point.x(), point.y()

        # Start point (x,y)
        x,y = x1,y1

        # Check the length of the line (using abs to draw lines from both sides)
        if abs(x2-x1) > abs(y2-y1) : length = abs(x2-x1)
        else : length = abs(y2-y1)

        # In case of 0 length (in curve line) continue (avoid devision by zero)
        if length == 0 : return

        # Claculate the derivatives
        dx = (x2-x1)/float(length)
        dy = (y2-y1)/float(length)

        # Run over the lines points and draw them + add round corners
        for _ in range(length):
            # Promot the position to the next point
            x += dx
            y += dy
            # Draw the pixel
            self.PutPixel(painter, QPoint(x,y))
            # Draw the corners (Making the line more smooth)
            self.PutPixel(painter, QPoint(self.RoundDown(x), self.RoundDown(y)))
            self.PutPixel(painter, QPoint(self.RoundUp(x), self.RoundUp(y)))

        return True


    # Draw circel by one pixel on the circel
    def drawPixelInCircle(self, painter, xc, yc, x, y):
        # Take point on the circel from 1/8 and draw it on other 7/8
        self.PutPixel(painter, QPoint(xc+x, yc+y))
        self.PutPixel(painter, QPoint(xc-x, yc+y))
        self.PutPixel(painter, QPoint(xc+x, yc-y))
        self.PutPixel(painter, QPoint(xc-x, yc-y))
        self.PutPixel(painter, QPoint(xc+y, yc+x))
        self.PutPixel(painter, QPoint(xc-y, yc+x))
        self.PutPixel(painter, QPoint(xc+y, yc-x))
        self.PutPixel(painter, QPoint(xc-y, yc-x))


    # Draw circel frome center to outside point
    def MyCircle(self, painter, points):
        # If we dont have 2 points yet return
        if len(points) < 2 : return False

        # pop the outside point and save it as x1,y1
        point = points.pop()
        x1, y1 = point.x(), point.y()

        # pop the center point and save it as xc,yc
        point = points.pop()
        xc, yc = point.x(), point.y()

        # Calculate the radius
        radius = math.sqrt((xc - x1)**2 + (yc - y1)**2)

        # Init parameters
        teta = 0
        d = 3 - 2 * radius
        x = 0
        y = radius

        # Draw with first point
        self.drawPixelInCircle(painter, xc, yc, x, y)

        # Run over all points on 1/8 of the outside circel
        while y > x :
            x += 1
            if d > 0 :
                y -= 1
                d = d + 4 * (x -y) + 10
            else :
                d = d + 4 * x + 6
            # Draw point to other 7/8 of the circel
            self.drawPixelInCircle(painter, xc, yc, x, y)

        return True


    # Draw circel frome center to outside point
    def MyCurve(self, painter, points, n=100):
        if len(points) < 4 :
            # Draw the guide points of the curve line
            p = painter.pen()
            p.setWidth(4)
            painter.setPen(p)
            for point in points : self.PutPixel(painter, point)
            # Return pen width to default
            p.setWidth(1)
            painter.setPen(p)
            return False

        # pop the last point and save it as x4,y4
        point = points.pop()
        self.erasePoint(painter, point, 4)
        x4, y4 = point.x(), point.y()
        # pop the on of the center points and save it as x3,y3
        point = points.pop()
        self.erasePoint(painter, point, 4)
        x3, y3 = point.x(), point.y()
        # pop the on of the center points and save it as x2,y2
        point = points.pop()
        self.erasePoint(painter, point, 4)
        x2, y2 = point.x(), point.y()
        # pop the first point and save it as x1,y1
        point = points.pop()
        self.erasePoint(painter, point, 4)
        x1, y1 = point.x(), point.y()

        # Init bezier matrix
        bezierMatrix = np.array([[-1, 3, -3, 1],
                                [3, -6, 3, 0],
                                [-3, 3, 0, 0],
                                [1, 0, 0, 0]])

        # Create X,Y vectors from our 4 points
        X = bezierMatrix.dot(np.array([x1, x2, x3, x4]))
        Y = bezierMatrix.dot(np.array([y1, y2, y3, y4]))

        prevPoint = None
        # Run over t from 0 to 1 in n steps
        for t in np.linspace(0.0, 1.0, n):
            # Calculate X(t)
            Xt = np.array([math.pow(t,3), math.pow(t,2), t, 1]).dot(X)
            # Calculate Y(t)
            Yt = np.array([math.pow(t,3), math.pow(t,2), t, 1]).dot(Y)
            # Check if there is prev point to make a line from it to current point
            if prevPoint :
                self.MyLine(painter, [prevPoint, QPoint(Xt,Yt)])
            # Save current point as prev point and continue
            prevPoint = QPoint(Xt,Yt)

        return True

    def UndoAction(self, painter):

        if len(self.CurrentDraw) == 0 : return
        # Save current pen data
        p = painter.pen()

        # Parse last action
        actionString = self.CurrentDraw.pop()[:-1]
        mode, pointsString, color, width = actionString.split('=')
        # Create undo pen
        uPen = QPen()
        uPen.setColor(QColor('#000000'))
        uPen.setWidth(int(width))
        painter.setPen(uPen)

        points = []

        # Make array of points
        pointsString = pointsString.split('&')
        for point in pointsString:
            x, y = point.split(',')
            points.append(QPoint(int(x), int(y)))

        # Undo
        self.update(painter, points, mode, color, width, False)
        # Return prev pen
        painter.setPen(p)


    # Erase pixel in point position
    def erasePoint(self, painter, point, penW=30):
        # Save current pen data
        p = painter.pen()
        # Create eraser pen
        ePen = QPen()
        ePen.setColor(QColor('#000000'))
        ePen.setWidth(penW)
        painter.setPen(ePen)
        # Erase
        self.PutPixel(painter, point)
        # Return prev pen
        painter.setPen(p)