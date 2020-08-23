# Shira Levy
# Guy Chriqui
# Yam Arbel

import sys
from PyQt5 import QtWidgets
from gui import MainWindow

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
