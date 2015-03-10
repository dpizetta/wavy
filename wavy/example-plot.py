
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

import collections
import random
import time
import math
import numpy as np

import pyqtgraph.examples
pyqtgraph.examples.run()

class DynamicPlotter(QtGui.QWidget):

    def __init__(self, sampleinterval=0.01, timewindow=20., size=(600,350), parent=None):
        super(DynamicPlotter, self).__init__(parent)
        # Data stuff
        self._interval = int(sampleinterval*1000)
        self._bufsize = int(timewindow/sampleinterval)
        self.databuffer = collections.deque([0.0]*self._bufsize, self._bufsize)
        self.x = np.linspace(-timewindow, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)
        # PyQtGraph stuff
        self.plt = pg.plot(title='Dynamic Plotting with PyQtGraph')
        self.plt.resize(*size)
        self.plt.showGrid(x=True, y=True)
        self.plt.setLabel('left', 'Amplitude', 'V')
        self.plt.setLabel('bottom', 'Time', 's')
        self.curve = self.plt.plot(self.x, self.y, pen=(255,255,0))
        # QTimer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def getdata(self):
        frequency = 0.5
        noise = random.normalvariate(0., 1.)
        new = 10.*math.sin(time.time()*frequency*2*math.pi) + noise
        return new

    def updateplot(self):
        self.databuffer.append( self.getdata() )
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)
        #self.app.processEvents()      

if __name__ == '__main__':
    app = QtGui.QApplication([])
    plot_widget = DynamicPlotter(sampleinterval=0.005, timewindow=20.)
    app.exec_()