'''
Created on 28 Nov 2013

@author: albert
'''
from PyQt4.QtGui import QWidget, QSizePolicy

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt


class MapCanvas(QWidget):
    def __init__(self, triangles, parent=None):
        super(MapCanvas, self).__init__(parent)
        self.triangles = triangles
        self.first_run = True
        
        self.fig, self.axes = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        
        
    def paintEvent(self, e):
        self.axes.clear()        
         
        xy = np.asarray([(0, 0), (1, 1), (2,2), (1,0), (2, 1), (2, 0), (0, 1), (0, 2), (0, 0), (0, 2)])
        
        x = xy[:,0]
        y = xy[:,1]
        
        triangles = np.asarray([
            [8, 2, 9], [1,9, 3], [2, 4, 6] ])
        
        zfaces = np.asarray([0, 4.42, 130000.20])
    
    
        self.axes.set_aspect('equal')
        tri = self.axes.tripcolor(x, y, triangles, facecolors=zfaces, edgecolors='k')
        self.axes.set_title('tripcolor of user-specified triangulation')
        self.axes.set_xlabel('Longitude (degrees)')
        self.axes.set_ylabel('Latitude (degrees)')
        if self.first_run:
            self.fig.colorbar(tri)
            self.first_run = False
       
        self.canvas.draw()