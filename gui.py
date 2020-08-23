# Shira Levy
# Guy Chriqui
# Yam Arbel

from PyQt5 import QtCore
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QStackedWidget, \
    QPushButton, QMenu, QAction, QLabel, QMainWindow, QMessageBox, QLineEdit, QApplication
from PyQt5.QtGui import QColor, QPainter, QPixmap, QKeySequence
import functions
import time

# Avilable modes
MODES = ['Parallel Orthographic', 'Parallel Oblique', 'Perspective', 'Reset']
MODES_DOWN = ['Rotate Degree', '⟳ - X', '⟳ - Ƴ', '⟳ - Ȥ', '✚', '–']

DEGREES = ['-270', '-180', '-120', '-90', '-60', '-45', '0', '45', '60', '90', '120', '150', '180', '220', '270', '320', '360']

DISTANCES = ['50', '100', '150', '200', '250', '300']

LETTERS = [' ', ' ', '🅿', '🅰', '🅸', '🅽', '🆃', ' ']


# Main window class
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # rotate degree angle
        self.rotate_degree = 0

        # chosen projection: 1=Parallel Orthographic, 2=Parallel Oblique, 3=Perspective
        self.projection = 1

        # Set size and prevent from user change size
        self.setFixedSize(1300, 830)

        # Create the drawing canvas
        self.canvas = DrawCanvas()

        # Create the main window widget
        self.widget = QWidget()

        # Create widget layout
        self.layout = QVBoxLayout()

        self.isRotating = False

        # Add draw modes buttons to draw layout
        self.DrawPalette = QHBoxLayout()
        self.add_modes_buttons()

        # Add window colors buttons to draw layout
        self.DrawPaletteDown = QHBoxLayout()
        self.add_modes_buttons_down()

        self.layout.addLayout(self.DrawPalette)
        self.layout.addWidget(self.canvas)
        self.layout.addLayout(self.DrawPaletteDown)

        # Create the main window widgets
        self.widget.setLayout(self.layout)

        # Create central widget to hold our widget
        self.central_widget = QWidget(self)

        # Insert our widgets to stackwidget
        self.stacked_widget = QStackedWidget(self.central_widget)
        self.stacked_widget.addWidget(self.widget)

        # Set the window and default widget as DrawWidget
        self.setCentralWidget(self.central_widget)

        # class Actions - all projections, scale and rotate.
        self.actions = functions.Actions(self.canvas.painter)

    # Build modes buttons
    def add_modes_buttons(self):
        # For each mode type make a button in this mode
        for mode in MODES:
            button = ModesButton(mode, size=QtCore.QSize(200, 32))

            if mode == 'Parallel Orthographic':
                button.pressed.connect(self.parallel_orthographic)
            elif mode == 'Parallel Oblique':
                button.setMenu(self.add_degrees_menu())
            elif mode == 'Perspective':
                button.setMenu(self.add_distance_menu())
            elif mode == 'Reset':
                button = ModesButton(mode, size=QtCore.QSize(100, 32))
                button.pressed.connect(self.clear)
            # Add the buttun to layout widget
            self.DrawPalette.addWidget(button)

    # Build modes buttons down
    def add_modes_buttons_down(self):
        # For each mode type make a button in this mode
        for mode in MODES_DOWN:
            button = ModesButton(mode)

            if mode == 'Rotate Degree':
                self.degreeWid = QHBoxLayout()
                self.text = QLabel(text='∠°')
                self.rotate_degree = QLineEdit(self, text='90')
                self.rotate_degree.setFixedSize(45, 32)
                self.text.setFixedSize(25, 32)
                self.degreeWid.addWidget(self.text)
                self.degreeWid.addWidget(self.rotate_degree)

                self.DrawPaletteDown.addLayout(self.degreeWid)
                continue
            elif mode == '⟳ - X':
                button.pressed.connect(lambda x='x': self.rotate(x))
            elif mode == '⟳ - Ƴ':
                button.pressed.connect(lambda y='y': self.rotate(y))
            elif mode == '⟳ - Ȥ':
                button.pressed.connect(lambda z='z': self.rotate(z))
            elif mode == '✚':
                button.pressed.connect(lambda op='+': self.scale(op))
            elif mode == '–':
                button.pressed.connect(lambda op='-': self.scale(op))
            # Add the buttun to layout widget
            self.DrawPaletteDown.addWidget(button)

    # Create pen width menu
    def add_degrees_menu(self):
        menu = QMenu()
        # Get row on menu for each PEN_WIDTHS
        for degree in DEGREES:
            # Connect menu option to setWidth function
            menu.addAction(degree, lambda degree=degree: self.parallel_oblique(degree))
            menu.addSeparator()
        # Return menu
        return menu

    def add_distance_menu(self):
        menu = QMenu()
        # Get row on menu for each PEN_WIDTHS
        for distance in DISTANCES:
            # Connect menu option to setWidth function
            menu.addAction(distance, lambda distance=distance: self.perspective(distance))
            menu.addSeparator()
        # Return menu
        return menu

    def parallel_orthographic(self):
        self.projection = 1
        self.refresh_canvas()
        self.actions.parallel_orthographic()
        self.canvas.update()

    def parallel_oblique(self, degree):
        self.projection = 2
        self.refresh_canvas()
        self.actions.parallel_oblique(degree)
        self.canvas.update()

    def perspective(self, d):
        self.projection = 3
        self.refresh_canvas()
        self.actions.perspective(d)
        self.canvas.update()

    def rotate(self, axis):

        if self.isRotating:
            return

        txt = self.rotate_degree.text()
        if txt == '':
            self.show_error_message('Please Enter Degrees')
            return
        if len(txt) > 1:
            if not txt.isnumeric() and ((txt[0] != '-') or not txt[1:].isnumeric()):
                self.show_error_message('Text is not allowed! \n Please Enter Degree number between -360 and 360')
                return
        elif not txt.isnumeric():
            self.show_error_message('Text is not allowed! \n Please Enter Degree number between -360 and 360')
            return
        d = 1
        if txt[0] == '-':
            txt_num = int(txt[1:])
            d = -1
        else:
            txt_num = int(txt)
        if not (0 <= txt_num < 361):
            self.show_error_message('Please Enter Degree number between -360 and 360')
            return
        self.isRotating = True
        
        for _ in range(txt_num):
            if self.rotate_degree.text() != txt:
                break
            self.refresh_canvas()
            self.actions.rotate(d, axis)
            self.canvas.update()
            QApplication.processEvents()
            time.sleep(0.01)

        self.isRotating = False

    def scale(self, op):
        self.refresh_canvas()
        self.actions.scale(op)
        self.canvas.update()

    # Delete all drawing
    def refresh_canvas(self):
        # Paint all pixels back to black
        self.canvas.painter.fillRect(0, 0, self.canvas.width, self.canvas.height, QColor('#000000'))
        # Update canvas
        self.canvas.update()

    def clear(self):
        self.refresh_canvas()
        self.actions.initialize()

    # Popup error message
    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(message)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        msg.show()


# Class that control the drawing canvas
class DrawCanvas(QLabel):

    def __init__(self):
        super().__init__()

        # Canvas size
        self.width = 1280
        self.height = 720
        # Color of painter (Default is white)
        self.currentColor = QColor('#ffffff')
        # Width of painter (Default 3px)
        self.currentWidth = 3
        # Remember previous mouse clicks positions (Default is None)
        self.previousClicks = []
        # Current painting mode (Default is point)
        self.currentMode = MODES[1]

        # Create the canvas window
        self.create_canvas()
        # Create the painter
        self.painter = None
        self.create_painter()

    # Create canvas
    def create_canvas(self):
        canvas = QPixmap(self.width, self.height)
        self.setPixmap(canvas)

    # Create painter that make it able to paint on QPixmap
    def create_painter(self):
        # Create QPainter from the QLabel pixmap
        self.painter = QPainter(self.pixmap())
        p = self.painter.pen()
        # Set painter color to default color
        p.setColor(QColor(self.currentColor))
        # Set painter width to default width
        p.setWidth(self.currentWidth)
        self.painter.setPen(p)


# Modes button class
class ModesButton(QPushButton):
    def __init__(self, text, size=QtCore.QSize(100, 32)):
        super().__init__()
        # Set button text
        self.setText(text)
        # Set button size
        self.setFixedSize(size)
