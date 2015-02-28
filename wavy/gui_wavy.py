"""Wavy main window.

Wavy is a simple program that allows you to acquire sound from mic and save as .dat.

:authors: Daniel Cosmo Pizetta
:contact: daniel.pizetta@usp.br
:since: 27/02/2015

"""


from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication, QPixmap, QSplashScreen, QMainWindow, QMessageBox
from PyQt4 import uic
import collections
import math
import random
import sys
import time

from mw_wavy import Ui_MainWindow
from gui_wav2dat import ConvertWave2Data
import numpy as np
import pyqtgraph as pg
import rc_wavy_rc


__version__ = "0.1"
__app_name__ = "Wavy"

about = '<h3>{} v.{}</h3><p>Author: Daniel Cosmo Pizetta<br/>Sao Carlos Institute of Physics<br/>University of Sao Paulo</p><p>Wavy is a simple program that allows you to acquire sound from  mic and save as .dat.<p>For more information and new versions, please, visit: <a href="https://github.com/dpizetta/wavy">Wavy on GitHub</a></p><p>This software is under <a href="http://choosealicense.com/licenses/mit/">MIT</a> license. 2015</p>'.format(__app_name__, __version__)


def main(argv):
    """The main function."""

    wavy = QApplication(argv)
    wavy.setStyle('Cleanlooks')
    wavy.setApplicationVersion(__version__)
    wavy.setApplicationName(__app_name__)
    wavy.setOrganizationName("Sao Carlos Institute of Physics - University of Sao Paulo")
    wavy.setOrganizationDomain("www.ifsc.usp.br")

    pixmap = QPixmap("images/symbol.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    splash.showMessage("Loading...")
    wavy.processEvents()
    splash.showMessage("Starting...")
    wavy.processEvents()
    window = MainWindow()
    time.sleep(1)
    #window.ui.showMaximized()
    window.showMaximized()
    splash.finish(window)
    return wavy.exec_()


class DynamicPlotter(pg.PlotWidget):

    def __init__(self, sample_interval=0.01, time_window=20., parent=None):
        super(DynamicPlotter, self).__init__(parent)
        self.initData(sample_interval, time_window)
        self.showGrid(x=True, y=True)
        self.setLabel('left', 'Amplitude', 'V')
        self.setLabel('bottom', 'Time', 's')
        self.curve = self.plot(self.x, self.y, pen=(0, 255, 255))

    def initData(self, sample_interval=0.01, time_window=20.):
        self.sample_interval = sample_interval
        self.time_window = time_window
        self._interval = int(self.sample_interval * 1000)
        self._bufsize = int(self.time_window / self.sample_interval)
        self.databuffer = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.x = np.linspace(-self.time_window, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def getdata(self):
        frequency = 0.5
        noise = random.normalvariate(0., 1.)
        new = 10. * math.sin(time.time() * frequency * 2 * math.pi) + noise
        return new

    def updateplot(self):
        self.databuffer.append(self.getdata())
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)


class MainWindow(QMainWindow):

    """Main window class."""

    def __init__(self, parent=None):
        """Constructor of the class

        :param parent: parent
        :type param: QWidget()
        """
        super(MainWindow, self).__init__(parent)
        #self.ui = uic.loadUi('mw_wavy.ui')
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(__app_name__ + '  ' + __version__)
        self.ui.labelAbout.setText(self.tr(about))
        # Connecting actions
        # File actions
        self.ui.actionNew.triggered.connect(self.newFile)
        self.ui.actionOpen.triggered.connect(self.openFile)
        self.ui.actionSave.triggered.connect(self.saveFile)
        self.ui.actionSave_As.triggered.connect(self.saveFileAs)
        # Acquire actions
        self.ui.actionRecord.triggered.connect(self.record)
        self.ui.actionPause.triggered.connect(self.pause)
        self.ui.actionStop.triggered.connect(self.stop)
        # Tools actions
        self.ui.actionConvert_Wav_to_Dat.triggered.connect(self.callTools)
        # Program actions
        self.ui.actionQuit.triggered.connect(self.close)
        self.ui.actionAbout_Wavy.triggered.connect(self.about)
        # Plot widget
        self.plot_widget = DynamicPlotter(sample_interval=0.01, time_window=20.)
        self.ui.horizontalLayout.addWidget(self.plot_widget)
        # Inputs
        #self.ui.doubleSpinBoxSampleInterval.valueChanged.connect()
        
    def callTools(self):
        dlg = ConvertWave2Data()
        dlg.exec_()

    def record(self):
        """Starts acquiring."""

    def stop(self):
        """Stops acquiring."""

    def pause(self):
        """Pauses acquiring."""

    def clearGraph(self):
        """Clear graph"""

    def openFile(self):
        """Opens a file."""

    def newFile(self):
        """Creates a new file."""

    def saveFile(self):
        """Saves a file."""

    def saveFileAs(self, filename=''):
        """Saves file as new name."""

    def about(self):
        """Show the dialog about."""

        QMessageBox.about(self, self.tr('About'),
                          self.tr(about))

    def closeQuestion(self):
        """Asks about to close."""
        answer = QMessageBox.question(self,
                                      self.tr('Close'),
                                      self.tr('Do you want to exit ?'),
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.No)

        return answer == QMessageBox.Yes

    def closeEvent(self, event):
        """Re implements close event."""
        if self.closeQuestion():
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    sys.exit(main(sys.argv))
