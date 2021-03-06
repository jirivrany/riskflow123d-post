'''
Created on 28 Nov 2013

@author: albert
'''
from PyQt4.QtGui import QWidget, QSizePolicy, QVBoxLayout

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
from ruzne import value_set


class MapCanvas(QWidget):
    def __init__(self, triangulation, options, parent=None):
        super(MapCanvas, self).__init__(parent)
        self.triang = triangulation
        self.first_run = True
        
        self.lab_x = options['xlabel'] if value_set(options, 'xlabel') else 'mesh X coord'
        self.lab_y = options['ylabel'] if value_set(options, 'ylabel') else 'mesh Y coord'
        self.title = options['title'] if value_set(options, 'title') else 'Map of concentrations'
        
        self.setWindowTitle(self.title)
        self.create_main_frame()
        self.on_draw()
        
    def create_main_frame(self):
        '''
        main frame of the window creates sublots and toolbar
        '''
        
        self.fig, self.axes = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self)
        self.canvas.setSizePolicy(QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.mpl_toolbar = NavigationToolbar(self.canvas, self)
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        
        self.setLayout(vbox)
            
        
    def on_draw(self):
        '''
        draw the chart
        '''
        
        
        
        self.axes.clear()        
        self.axes.set_aspect('equal')
        tri = self.axes.tripcolor(self.triang['x_np'],
                  self.triang['y_np'],
                  self.triang['triangles'],
                  facecolors=self.triang['zfaces'],
                  edgecolors='k')
        self.axes.set_title(self.title)
        self.axes.set_xlabel(self.lab_x)
        self.axes.set_ylabel(self.lab_y)
        if self.first_run:
            self.fig.colorbar(tri)
            self.first_run = False
       
        self.canvas.draw()