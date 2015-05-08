"""Wavy main window.

Wavy is a simple program that allows you to acquire sound from mic and save as .wav or .dat.

:authors: Daniel Cosmo Pizetta
:contact: daniel.pizetta@usp.br
:since: 27/02/2015

"""


from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication, QPixmap, QSplashScreen, QMainWindow, QMessageBox
import collections
import math
import random
import time

import numpy as np
import pyqtgraph as pg
import wavy.images.rc_wavy_rc

from wavy.core_wavy import AudioRecord
from wavy.gui_wav2dat import ConvertWave2Data
from wavy.mw_wavy import Ui_MainWindow


__version__ = "0.1"
__app_name__ = "Wavy"

about = '<h3>{} v.{}</h3><p>Author: Daniel Cosmo Pizetta<br/>Sao Carlos Institute of Physics<br/>University of Sao Paulo</p><p>Wavy is a simple program that allows you to acquire sound from  mic and save as .wav or .dat.<p>For more information and new versions, please, visit: <a href="https://github.com/dpizetta/wavy">Wavy on GitHub</a>.</p><p>This software is under <a href="http://choosealicense.com/licenses/mit/">MIT</a> license. 2015.</p>'.format(__app_name__, __version__)


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
    splash.repaint()
    splash.showMessage("Loading...")
    wavy.processEvents()
    splash.showMessage("Starting...")
    wavy.processEvents()
    window = MainWindow()
    window.showMaximized()
    time.sleep(0)
    splash.finish(window)
    return wavy.exec_()

# recording plotter


class Plotter(pg.PlotWidget):

    def __init__(self, sample_interval=0.01, time_window=20., parent=None):
        super(Plotter, self).__init__(parent)
        self.sample_interval = sample_interval
        self.time_window = time_window
        self.showGrid(x=True, y=True)
        self.setLabel('top', 'Recorded data')
        self.setLabel('left', 'Amplitude', 'V')
        self.setLabel('bottom', 'Time', 's')
        self.curve = None

    def initData(self):
        self._interval = int(self.sample_interval * 1000)
        self._bufsize = int(self.time_window / self.sample_interval)
        self.x = np.linspace(0.0, self.time_window, self._bufsize)
        self.setDownsampling(mode='peak')
        self.setClipToView(True)
        self.data = np.empty(5)
        self.ptr = 0
        self.curve = self.plot(self.x[:self.ptr], self.data[:self.ptr], antialias=True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def setSampleInterval(self, sample_interval):
        self.sample_interval = sample_interval
        self.curve.clear()
        self.initData()

    def setTimeWindow(self, time_window):
        self.time_window = time_window
        self.curve.clear()
        self.initData()

    def getdata(self):
        frequency = 0.5
        noise = random.normalvariate(0., 1.)
        new = 20. * math.sin(time.time() * frequency * 2 * math.pi) + noise
        return new

    def updateplot(self):
        self.data[self.ptr] = self.getdata()
        self.x[self.ptr + 1] = self.x[self.ptr] + self.sample_interval
        self.ptr += 1
        if self.ptr >= self.data.shape[0]:
            tmp = self.data
            xtmp = self.x
            self.data = np.empty(self.data.shape[0] + 10)
            self.x = np.empty(self.x.shape[0] + 10)
            self.data[:tmp.shape[0]] = tmp
            self.x[:xtmp.shape[0]] = xtmp
            self.curve.setData(self.x[:self.ptr], self.data[:self.ptr])

    def setCurveColor(self, r, g, b):
        self.curve.setPen(pg.mkPen(color=(r, g, b)))

# realtime plotter


class DynamicPlotter(pg.PlotWidget):

    def __init__(self, sample_interval=0.01, time_window=20., parent=None):
        super(DynamicPlotter, self).__init__(parent)
        self.sample_interval = sample_interval
        self.time_window = time_window
        self.showGrid(x=True, y=True)
        self.setLabel('top', 'Input Real Time')
        self.setLabel('left', 'Amplitude', 'V')
        self.setLabel('bottom', 'Time', 's')
        self.curve = None

    def initData(self):
        self._interval = int(self.sample_interval * 1000)
        self._bufsize = int(self.time_window / self.sample_interval)
        self.databuffer = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.x = np.linspace(-self.time_window, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)
        self.audio = AudioRecord("output.wav", 1000, 1)
        self.audio.begin_audio()

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)
        self.curve = self.plot(self.x, self.y, pen=(0, 255, 255), antialias=True)
        self.curve.clear()

    def setSampleInterval(self, sample_interval):
        self.sample_interval = sample_interval
        self.curve.clear()
        self.initData()

    def setTimeWindow(self, time_window):
        self.time_window = time_window
        self.curve.clear()
        self.initData()

    def getdata(self):
        # frequency = 0.5
        # noise = random.normalvariate(0., 1.)
        # new = 10. * math.sin(time.time() * frequency * 2 * math.pi) + noise
        a, b = self.audio.get_data_from_audio()
        new = b[0]
        return new

    def updateplot(self):
        stp = self.getdata()
        self.databuffer.append(stp)
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)

    def setCurveColor(self, r, g, b):
        self.curve.setPen(pg.mkPen(color=(r, g, b)))


class MainWindow(QMainWindow):

    """Main window class."""

    def __init__(self, parent=None):
        """Constructor of the class

        :param parent: parent
        :type param: QWidget()
        """
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle(__app_name__ + '  ' + __version__)
        self.ui.labelAbout.setText(self.tr(about))
        # Connecting actions
        # File actions
        self.ui.actionNew.triggered.connect(self.newFile)
        # For now it cannot open a file
        # self.ui.actionOpen.triggered.connect(self.openFile)
        self.ui.actionSave.triggered.connect(self.saveFile)
        self.ui.actionSave_As.triggered.connect(self.saveFileAs)
        # Acquire actions
        self.ui.actionRecord.triggered.connect(self.record)
        self.ui.actionRecord.setCheckable(True)
        self.ui.actionPause.triggered.connect(self.pause)
        self.ui.actionPause.setCheckable(True)
        self.ui.actionPause.setEnabled(False)
        self.ui.actionStop.triggered.connect(self.stop)
        self.ui.actionStop.setEnabled(False)
        # Tools actions
        self.ui.actionConvert_Wav_to_Dat.triggered.connect(self.callTools)
        # Program actions
        self.ui.actionQuit.triggered.connect(self.close)
        self.ui.actionAbout_Wavy.triggered.connect(self.about)
        # Plot widget

        self.plot_widget = DynamicPlotter(sample_interval=0.01, time_window=20.)
        self.plot_widget.initData()
        self.ui.gridLayout_2.addWidget(self.plot_widget, 0, 1)
        self.plot_widget_rec = Plotter(sample_interval=0.01, time_window=5.)
        self.ui.gridLayout_2.addWidget(self.plot_widget_rec, 1, 1)
        # Inputs
        self.ui.doubleSpinBoxSampleInterval.valueChanged.connect(self.plot_widget.setSampleInterval)
        self.ui.doubleSpinBoxSampleInterval.valueChanged.connect(self.setSampleRate)
        self.ui.doubleSpinBoxSampleRate.valueChanged.connect(self.setSampleInterval)
        self.ui.spinBoxWindowTime.valueChanged.connect(self.plot_widget.setTimeWindow)
        self.setSampleRate(self.ui.doubleSpinBoxSampleInterval.value())

    def setSampleRate(self, sample_interval):
        """Sets sample rate.
        """
        self.ui.doubleSpinBoxSampleRate.setValue(1. / sample_interval)

    def setSampleInterval(self, sample_rate):
        """Sets sample interval.
        """
        self.ui.doubleSpinBoxSampleInterval.setValue(1. / sample_rate)

    def callTools(self):
        dlg = ConvertWave2Data()
        dlg.exec_()

    def record(self):
        """Starts acquiring.
        """

        if self.plot_widget_rec.curve is not None:
            self.plot_widget_rec.curve.clear()
        self.plot_widget_rec.initData()
        self.plot_widget_rec.setCurveColor(255, 0, 0)
        self.plot_widget_rec.setLabel('top', 'Recording ...')
        # Set enabled buttons
        self.ui.actionPause.setEnabled(True)
        self.ui.actionStop.setEnabled(True)
        self.ui.actionRecord.setEnabled(False)
        # Set enabled inputs
        self.ui.spinBoxWindowTime.setEnabled(False)
        self.ui.doubleSpinBoxSampleInterval.setEnabled(False)
        self.ui.doubleSpinBoxSampleRate.setEnabled(False)
        self.ui.spinBoxStopRecordingAfter.setEnabled(False)
        # Set enabled tool bar and menu
        self.ui.toolBarFile.setEnabled(False)
        self.ui.menuFile.setEnabled(False)
        self.ui.menuTools.setEnabled(False)

    def pause(self):
        """Pauses acquiring.
        """

        if self.ui.actionPause.isChecked():
            # Stopping changing color and label
            self.plot_widget_rec.timer.stop()
            self.plot_widget_rec.setCurveColor(255, 153, 0)
            self.plot_widget_rec.setLabel('top', 'Paused ...')
        else:
            # Starting changing color and label
            self.plot_widget_rec.timer.start()
            self.plot_widget_rec.setCurveColor(255, 0, 0)
            self.plot_widget_rec.setLabel('top', 'Recording ...')
        # Set enabled tool bar
        self.ui.toolBarFile.setEnabled(False)
        self.ui.menuFile.setEnabled(False)
        self.ui.menuTools.setEnabled(False)

    def stop(self):
        """Stops acquiring.
        """

        # Stopping changing color and label
        self.plot_widget_rec.timer.stop()
        self.plot_widget_rec.setCurveColor(0, 255, 0)
        self.plot_widget_rec.setLabel('top', 'Stoped ...')
        # Set checked
        self.ui.actionRecord.setChecked(False)
        self.ui.actionPause.setChecked(False)
        # Set enabled buttons
        self.ui.actionPause.setEnabled(False)
        self.ui.actionStop.setEnabled(False)
        self.ui.actionRecord.setEnabled(True)
        # Set enabled inputs
        self.ui.doubleSpinBoxSampleInterval.setEnabled(True)
        self.ui.doubleSpinBoxSampleRate.setEnabled(True)
        self.ui.spinBoxWindowTime.setEnabled(True)
        self.ui.spinBoxStopRecordingAfter.setEnabled(True)
        # Set enabled tool bar
        self.ui.toolBarFile.setEnabled(True)
        self.ui.menuFile.setEnabled(True)
        self.ui.menuTools.setEnabled(True)

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
            self.stop()
            self.plot_widget.audio.end_audio()
            event.accept()
        else:
            event.ignore()
