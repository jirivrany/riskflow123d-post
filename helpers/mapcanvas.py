'''
Created on 28 Nov 2013

@author: albert
'''
from PyQt4.QtGui import QWidget, QPainter


class MapCanvas(QWidget):
    def __init__(self, triangles):
        super(MapCanvas, self).__init__()
        self.triangles = triangles

    def paintEvent(self, e):
        dc = QPainter(self)
        dc.drawLine(0, 0, 100, 100)
        dc.drawLine(100, 0, 0, 100)