# Yam Arbel  204209332
# Shira Levy 305451833
# Guy Chriqui 203137641

import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QStackedWidget, \
    QPushButton, QMenu, QFileDialog, QAction, QMenuBar, QLabel, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QImage, QKeySequence
from utils_HW1 import Draw
from utils_HW2 import TransformationImage
from functools import partial
import numpy as np

# Avilable colors
COLORS = ['#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49',
'#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245', '#a15c3e', '#a42f3b',
'#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#ffffff',]

# Avilable modes
MODES = ['Pen Width', 'Point', 'Line', 'Circel', 'Curve', 'Undo', 'Export', 'Transformation']

# Avilable transformation modes
TRANS_MODES = ['Load', '+','-', '⟲', '⟳' , '↑' , '←' , '→' , '↓', 'Mirror', 'Shearing', 'Draw']

# Avilable pen size
PEN_WIDTHS = ['1 px', '3 px', '5 px', '7 px', '9 px', '11 px', '15 px']


# Colors button class
class QPaletteButton(QPushButton):

    def __init__(self, color):
        super().__init__()
        # Set button size
        self.setFixedSize(QtCore.QSize(30,30))
        # Set button color
        self.color = color
        self.setStyleSheet("background-color: %s;" % color)



# Modes button class
class ModesButton(QPushButton):

    def __init__(self, text):
        super().__init__()
        # Set button text
        self.setText(text)
        # Set button size
        self.setFixedSize(QtCore.QSize(120, 32))


# Class that control the drawing canvas
class DrawCanvas(QLabel):

    def __init__(self):
        super().__init__()

        # Creat Draw class
        self.Draw = Draw()

        # Canvas size
        self.width = 1280
        self.height = 720
        # Color of painter (Default is white)
        self.currentColor = QColor(COLORS[-1])
        # Width of painter (Default 3px)
        self.currentWidth = 3
        # Remember previous mouse clicks positions (Default is None)
        self.previousClicks = []
        # Current painting mode (Default is point)
        self.currentMode = MODES[1]

        # Create the canvas window
        self.CreateCanvas()
        # Create the painter
        self.CreatePainter()


    # Create canvas window in type of QPixmap
    def CreateCanvas(self):
        canvas = QPixmap(self.width, self.height)
        self.setPixmap(canvas)

    # Create painter thats make it able to paint on QPixmap
    def CreatePainter(self):
        # Create QPainter from the QLabel pixmap
        self.painter = QPainter(self.pixmap())
        p = self.painter.pen()
        # Set painter color to defualt color
        p.setColor(QColor(self.currentColor))
        # Set painter width to defualt width
        p.setWidth(self.currentWidth)
        self.painter.setPen(p)

    # Set the color of the pen
    def setColor(self, color):
        # Update current color
        self.currentColor = QColor(color)
        # Update pen color
        p = self.painter.pen()
        # Set painter color to defualt color
        p.setColor(QColor(self.currentColor))
        self.painter.setPen(p)


    # Set the width of the pen
    def setWidth(self, width):
        # Update current width
        self.currentWidth = width
        # Update pen width
        p = self.painter.pen()
        p.setWidth(width)
        self.painter.setPen(p)


    # Set the current mode
    def setMode(self, mode):
        self.currentMode = mode

    # Undo last action
    def undo(self):
        self.Draw.UndoAction(self.painter)
        self.update()


    # Add mouse click to previousClicks and check for update
    def mousePressEvent(self, e):
        # Dont save clickes in transformation mode
        if self.currentMode == 'Scale' : return
        if self.currentMode == 'Shearing' : return

        # Make sure we use current color and width
        self.setColor(self.currentColor)
        self.setWidth(self.currentWidth)
        # Save position as point
        self.previousClicks.append(QPoint(e.x(), e.y()))
        # Send data to check if draw operation is needed
        self.Draw.update(self.painter, self.previousClicks, self.currentMode, self.currentColor , self.currentWidth)
        # Update the canvas
        self.update()

    
    # Let Eraser get clicked without release mouse left button
    def mouseMoveEvent(self, e):
        if not window.isTransformationMode: return
        
        if self.currentMode  == 'Shearing':
            # Save position
            position = QPoint(e.x(), e.y())
            # Refresh current draw
            window.RefrshCanvas()
            window.TransformationImage.Shearing(self.painter, position)
            window.canvas.update()
            # Update the canvas
            self.update()
        else: self.previousClicks = []


# Main window class
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Create menu bar
        self.CreateMenuBar()

        # Create the drawing canvas
        self.canvas = DrawCanvas()
        self.TransformationImage = TransformationImage(self.canvas.Draw)

        # Create the main window widget
        self.widget = QWidget()
        self.DrawWidget = QWidget()
        self.TransformationWidget = QWidget()

        # Create both main modes layouts
        self.TransformationLayout = QVBoxLayout()
        self.DrawLayout = QVBoxLayout()

        # Set default transformation mode to False
        self.isTransformationMode = False

        # Add draw modes buttons to draw layout
        self.DrawPalette = QHBoxLayout()
        self.AddModesButtons(self.DrawPalette)
        self.DrawLayout.addLayout(self.DrawPalette)

        # Add window transformations modes buttons to transformation layout
        self.TransformationsPalette = QHBoxLayout()
        self.AddTransformationsButtons(self.TransformationsPalette)
        self.TransformationLayout.addLayout(self.TransformationsPalette)

        # Add the drawing canvas to both layouts
        self.DrawLayout.addWidget(self.canvas)

        # Add window colors buttons to draw layout
        self.colorPalette = QHBoxLayout()
        self.AddColorButtons(self.colorPalette)
        self.DrawLayout.addLayout(self.colorPalette)

        # Create the main window widgets
        self.DrawWidget.setLayout(self.DrawLayout)
        self.TransformationWidget.setLayout(self.TransformationLayout)

        # Create centeral widget to hold our widget
        self.centralwidget = QWidget(self)

        # Insert our wigets to stackwidget
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.addWidget(self.DrawWidget)
        self.stackedWidget.addWidget(self.TransformationWidget)

        # Set the window and default widget as DrawWidget
        self.setCentralWidget(self.centralwidget)

        # Set size and prevent from user change size
        self.setFixedSize(1300, 830)


    # Build colors buttons
    def AddColorButtons(self, palette):
        # for each color type make a button in this color
        for color in COLORS:
            button = QPaletteButton(color)
            # Connect the button to setColor function
            button.pressed.connect(lambda color=color: self.canvas.setColor(color))
            # Add the buttun to layout widget
            palette.addWidget(button)


    # Update button text and change widht
    def WidhtSelected(self, width):
        widthNum = int(width.split(' ')[0])
        self.canvas.setWidth(widthNum)
        self.widthBtn.setText(str(self.canvas.currentWidth) + 'px')


    # Create pen width menu
    def AddWidthMenu(self):
        menu = QMenu()
        # Get row on menu for each PEN_WIDTHS
        for width in PEN_WIDTHS:
            # Connect menu option to setWidth function
            menu.addAction(width, lambda width=width: self.WidhtSelected(width))
            menu.addSeparator()
        # Return menu
        return menu


    # Build modes buttons
    def AddModesButtons(self, palette):
        # For each mode type make a button in this mode
        for mode in MODES:
            button = ModesButton(mode)

            if mode == 'Pen Width':
                button.setMenu(self.AddWidthMenu())
                button.setText(str(self.canvas.currentWidth) + 'px')
                self.widthBtn = button
            elif mode == 'Transformation':
                # Connect Transformation button to FlipTransformationMode
                button.pressed.connect(self.FlipTransformationMode)
            elif mode == 'Undo':
                # Connect undo button to undo function
                button.pressed.connect(self.canvas.undo)
            elif mode == 'Export':
                # Connect undo button to undo function
                button.pressed.connect(self.ExportToText)
            else:
                # Connect the button to setMode function
                button.pressed.connect(lambda mode=mode: self.canvas.setMode(mode))
            # Add the buttun to layout widget
            palette.addWidget(button)



    # Delete all drawing 
    def RefrshCanvas(self):
        # Paint all pixels back to black
        self.canvas.painter.fillRect(0, 0, self.canvas.width, self.canvas.height, QColor('#000000'))
        # Update canvas
        self.canvas.update()


    # Set mode to Scale and call function
    def Scale(self, mode):
        self.canvas.setMode('Scale')
        # Refresh the canvas from drawing
        self.RefrshCanvas()
        # Call Scale function
        self.TransformationImage.Scaling(self.canvas.painter, mode)
        # Update canvas
        self.canvas.update()


    # Set mode to Move and call function
    def Move(self, mode):
        self.canvas.setMode('Move')
        # Refresh the canvas from drawing
        self.RefrshCanvas()
        # Call Move function
        if mode == 'U': x, y = 0, -20
        elif mode == 'R': x, y = 20, 0
        elif mode == 'L': x, y = -20, 0
        elif mode == 'D': x, y = 0, 20
        self.TransformationImage.Move(self.canvas.painter, x, y)
        self.canvas.update()


    # Set mode to Rotate and call function
    def Rotate(self, mode):
        self.canvas.setMode('Rotate')
        # Refresh the canvas from drawing
        self.RefrshCanvas()
        # Call Rotate function
        if mode == 'L': r = -5
        elif mode == 'R': r = 5
        self.TransformationImage.Rotation(self.canvas.painter, r)
        self.canvas.update()


    # Set mode to Mirror and call function
    def Mirror(self):
        self.canvas.setMode('Mirror')
        # Refresh the canvas from drawing
        self.RefrshCanvas()
        # Call Mirror function
        self.TransformationImage.Mirroring(self.canvas.painter)
        self.canvas.update()


    # Set mode to Shearing and call function
    def Shearing(self):
        self.canvas.setMode('Shearing')

    def AddTransformationsButtons(self, palette):
         # For each transformation type make a button in this mode
        for mode in TRANS_MODES:
            button = ModesButton(mode)
            button.setFixedWidth(50)
            # Connect Draw button to FlipTransformationMode
            if mode == 'Draw': button.pressed.connect(self.FlipTransformationMode)
            # Connect scale button to scale function
            elif mode == "+": button.pressed.connect(lambda mode=mode: self.Scale('+'))
            elif mode == "-": button.pressed.connect(lambda mode=mode: self.Scale('-'))
            # Connect move button to move function 
            elif mode == '↑': button.pressed.connect(lambda mode=mode: self.Move('U'))
            elif mode == '←': button.pressed.connect(lambda mode=mode: self.Move('L'))
            elif mode == '→': button.pressed.connect(lambda mode=mode: self.Move('R'))
            elif mode == '↓': button.pressed.connect(lambda mode=mode: self.Move('D'))

            # Connect rotate button to rotate function '⟲', '⟳'
            elif mode == '⟲': button.pressed.connect(lambda mode=mode: self.Rotate('L'))
            elif mode == '⟳': button.pressed.connect(lambda mode=mode: self.Rotate('R'))

            # Connect mirror button to mirror function
            elif mode == 'Mirror': 
                button.pressed.connect(self.Mirror)
                button.setFixedWidth(100)

            # Connect mirror button to mirror function
            elif mode == 'Shearing': 
                button.pressed.connect(self.Shearing)
                button.setFixedWidth(100)

            elif mode == 'Load': 
                button.pressed.connect(self.LoadFromText)
                button.setFixedWidth(100)
            # Add the buttun to layout widget
            palette.addWidget(button)

    # Flip between draw mode and transformation mode
    def FlipTransformationMode(self):
        # Flip current transformation mode
        self.isTransformationMode = not self.isTransformationMode

        # If isTransformationMode == ture , replace to TransformationWidget
        if self.isTransformationMode:
            # Add current canvas
            self.TransformationLayout.addWidget(self.canvas)
            # Set mode to scale mode
            self.canvas.currentMode = TRANS_MODES[0]
            # Clean all but image
            self.RefrshCanvas()
            self.TransformationImage.DrawFromImage(self.canvas.painter, self.TransformationImage.currentImage)
            # Replace widget
            self.stackedWidget.setCurrentIndex(1)
        # Else replace to DrawWidget
        else :
            # Remove color layout
            self.DrawLayout.removeItem(self.colorPalette)
            # Add current canvas
            self.DrawLayout.addWidget(self.canvas)
            # Add new color layout
            self.colorPalette = QHBoxLayout()
            self.AddColorButtons(self.colorPalette)
            self.DrawLayout.addLayout(self.colorPalette)
            # Set mode to draw pixel
            self.canvas.currentMode = MODES[1]
            # Replace widget
            self.stackedWidget.setCurrentIndex(0)


    # Create top menue bar
    def CreateMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("File")
        # Creating save action
        saveAction = QAction("Save", self)
        # Setting save action shortcut
        saveAction.setShortcut(QKeySequence("Ctrl+S"))
        # Adding save action
        fileMenu.addAction(saveAction)
        saveAction.triggered.connect(self.SaveToImage)

        exportAction = QAction("Export ('txt')", self)
        # Setting export action shortcut
        exportAction.setShortcut(QKeySequence("Ctrl+E"))
        # Adding export action
        fileMenu.addAction(exportAction)
        exportAction.triggered.connect(self.ExportToText)

        loadAction = QAction("Load ('txt')", self)
        # Setting export action shortcut
        loadAction.setShortcut(QKeySequence("Ctrl+L"))
        # Adding export action
        fileMenu.addAction(loadAction)
        loadAction.triggered.connect(self.LoadFromText)

        clearAction = QAction("Clear", self)
        # Setting clear action shortcut
        clearAction.setShortcut(QKeySequence("Ctrl+C"))
        # Adding clear action
        fileMenu.addAction(clearAction)
        clearAction.triggered.connect(self.ClearCanvas)


    # Save the canvas as png
    def SaveToImage(self):
        # Select file to save to from file selection dialog
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        if filePath == "":
            return
        # Get the pixmap from canvas
        pix = self.canvas.pixmap()
        # Make QImage from pixmap
        image = pix.toImage()
        # Save QImage as png
        image.save(filePath, 'png')


    # Export image to text file
    def ExportToText(self):
        # Open file selection dialog
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "", options=options)
        # Make sure text file has selected. if not return
        if fileName.split('.')[-1] != 'txt':
            # Print error message
            self.ShowErrorMessage('Can\'t export to a none .txt file format')
            return
        # Open text file to write
        textFile = open(fileName, "w")
        # Init string
        actionString = ''
        # Save current transformation image to cuurentDraw
        self.TransformationImage.DrawFromImage(self.canvas.painter, self.TransformationImage.currentImage, True)
        # Create string
        for action in self.canvas.Draw.CurrentDraw:
            actionString += action
        # Remove last '\n' from string
        actionString = actionString[:-1]
        # Write string to selected file
        textFile.write(actionString)
        # Close selected file
        textFile.close()


    def LoadFromText(self):
        # Open file selection dialog
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", options=options)
        # Make sure text file has selected. if not return
        if fileName.split('.')[-1] != 'txt':
            # Print error message
            self.ShowErrorMessage('Please select an .txt file')
            return

        if not self.TransformationImage.DrawFromFile(self.canvas.painter, fileName):
            self.ShowErrorMessage('Text file no in the rigth format')
        self.canvas.update()


    # Clear canvas drawing
    def ClearCanvas(self):
        # paint all pixels back to black
        self.canvas.painter.fillRect(0, 0, self.canvas.width, self.canvas.height, QColor('#000000'))
        # Delete actions array
        self.canvas.Draw.CurrentDraw = []
        # Delete current transfotmation image
        self.TransformationImage.currentImage = []
        self.TransformationImage.originImage = []
        # Update canvas
        self.canvas.update()


    # Popup error message
    def ShowErrorMessage(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()
        msg.show()


# Main function of paint app
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()