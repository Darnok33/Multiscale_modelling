from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtGui import QApplication, QMainWindow, QColor, QPixmap
import time
import sys
import numpy as np
class Ui_promotedWidget(object):
    def setupWUi(self, promotedWidget):
        promotedWidget.setGeometry(QtCore.QRect(110, 140, promotedWidget.widget_x, promotedWidget.widget_y))


class promotedWidget(QtGui.QWidget, Ui_promotedWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.widget_x = 300
        self.widget_y = 300
        self.colors = [255,255,255]
        self.setupWUi(self)

    def set_Widget(self, widget_x, widget_y, colors = [255,255,255]):
        self.widget_x = widget_x
        self.widget_y = widget_y
        self.colors = colors
        self.resize(self.widget_x, self.widget_y)
        self.update()

    def paintEvent(self, e):
        self.paint = QtGui.QPainter()
        self.paint.begin(self)
        for j in range(self.widget_y):
            for i in range(self.widget_x):
                if isinstance(self.colors[0], (list, np.ndarray)):
                    if self.colors[j,i] in [[1,1,1,0], [1,1,1,1]]:
                        self.paint.setPen(QColor(1, 1, 1))
                    else:
                        self.paint.setPen(QColor(*self.colors[j, i]))

                    self.paint.drawPoint(i, j)
                else:
                    self.paint.setPen(QColor(*self.colors))
                    self.paint.drawPoint(i, j)
        self.paint.end()

    def paint_grid(self, x, y, colors):
        self.widget_x = x
        self.widget_y = y
        self.colors = colors
        self.update()

if __name__ == "__main__":
    sys.setrecursionlimit(1500)
    app = QtGui.QApplication(sys.argv)
    mainscreen = promotedWidget()

    mainscreen.show()
    time.sleep(10)

    mainscreen.set_Widget(100, 100, [50, 22, 255])
    mainscreen.updateGeometry()
    mainscreen.show()
    app.exec_()