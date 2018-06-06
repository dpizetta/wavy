#! python
# -*- coding: utf-8 -*-

"""
WavyTool is a simple program that allows you to acquire data from input devices,
i.e microphones, and save them as file (csv, png). Also, you can perform
some simple processing as spectral analysis.

:authors: Daniel Cosmo Pizetta, Wesley Daflita
:contact: daniel.pizetta@usp.br, wesley.daflita@usp.br
:since: 2015/02/27

"""

import collections
import json
import logging
import os
import sys
import time
import urllib.request

import numpy as np

# QtPy must be imported before pyqtgraph
from qtpy.QtCore import QTimer
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import (QApplication, QFileDialog, QMainWindow,
                            QMessageBox, QSplashScreen)

# Must be set to the same binding here
api_names = {'pyqt5': 'PyQt5', 'pyside2': 'PySide2', 'pyqt4': 'PyQt4', 'pyside': 'PySide'}
os.environ['PYQTGRAPH_QT_LIB'] = api_names[os.environ['QT_API']]

# PyQtGraph must be imported after QtPy
import pyqtgraph as pg

# Then import the own interface
from wavytool import __version__ as version
from wavytool import app_name
from wavytool.core_wavy import AudioRecord
from wavytool.gui_wav2dat import ConvertWave2Data
from wavytool.mw_wavy import Ui_MainWindow

logging.basicConfig(level=logging.DEBUG)

# Informing about used binding
logging.info('Using Qt binding (QtPy/PyQtGraph): %s', (os.environ['QT_API'],
                                                       os.environ['PYQTGRAPH_QT_LIB']))


about = ("<h3>{} v.{}</h3>"
         "<p>&copy Daniel C. Pizetta, Wesley Daflita<br/>"
         "Sao Carlos Institute of Physics<br/>"
         "University of Sao Paulo<br/>"
         "<a href='https://github.com/dpizetta/wavy'>WavyTool on GitHub</a><br/>"
         "<a href='https://pypi.org/project/wavytool'>WavyTool on PyPI</a><br/>"
         "<a href='http://choosealicense.com/licenses/mit'>MIT License</a><br/></p>").format(app_name, version)


def main():
    """The main function."""

    args = sys.argv[1:]

    wavy = QApplication(args)
    wavy.setApplicationVersion(version)
    wavy.setApplicationName(app_name)
    wavy.setOrganizationName("Sao Carlos Institute of Physics - University of Sao Paulo")
    wavy.setOrganizationDomain("www.ifsc.usp.br")

    try:
        import qdarkstyle
    except ImportError:
        logging.warning("No dark theme installed, use 'pip install qdarkstyle' to install.")
    else:
        try:
            wavy.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())
        except Exception as err:
            logging.warning("Problems using qdarkstyle.\nError: %s", str(err))

    pixmap = QPixmap("wavytool/images/symbol.png")
    splash = QSplashScreen(pixmap)

    start = time.time()
    splash.show()
    splash.repaint()

    splash.showMessage("Loading...")
    wavy.processEvents()

    while time.time() - start < 1:
        time.sleep(0.001)
        wavy.processEvents()
        splash.showMessage("Starting...")
    window = MainWindow()
    window.showMaximized()
    splash.finish(window)

    try:
        with open('wavytool.config', 'r') as json_file:
            data = json.load(json_file)
            window.base_path = data['data_folder']
            logging.info('Data folder is: %s', window.base_path)
    except IOError:
        window.getDataFolder()

    return wavy.exec_()


class GlobalBuffer():
    """Allows real-time data transfer between plots."""

    def __init__(self, buffer_size=1024):
        self.recording = False
        self.buffer_size = buffer_size
        self.data = np.empty(self.buffer_size)
        self.counter = 0
        self.timestamp = 0
        self.time_limit = 0

    def startRecording(self):
        self.timestamp = time.time()
        self.recording = True

    def stopRecording(self):
        self.timestamp = 0
        self.recording = False
        self.counter = 0

    def clear(self):
        tmp = self.data
        self.data[:self.buffer_size] = tmp
        self.counter = 0


global_buffer = GlobalBuffer()


class RecordingPlotter(pg.PlotWidget):
    """Plots sub data from real time plotter.

    Parameters:
        sample_interval (float): sample interval. Default 0.02 seconds.
        time_window (float): size (in time) for the main window. Default 20 seconds.
        main_window (MainWindow): main_window.
        parent (QWidget): parent.
    """

    def __init__(self, sample_interval=0.02, time_window=20., main_window=None, parent=None):
        super(RecordingPlotter, self).__init__(parent)
        self.sample_interval = sample_interval
        self.time_window = time_window
        self.showGrid(x=True, y=True)
        self.setLabel('top', 'Recorded data')
        self.setLabel('left', 'Amplitude', 'V')
        self.setLabel('bottom', 'Time', 's')
        self.curve = None
        self.main_window = main_window
        global global_buffer

    def initData(self):
        # Forces update at 20 FPS, shouldn't be taxing to most systems
        self._interval = int(1 / 20 * 1000)
        self._bufsize = int(self.time_window / self.sample_interval)
        self.x = np.linspace(0.0, self.time_window, self._bufsize)
        self.setDownsampling(mode='peak')
        self.databuffer = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.setClipToView(True)
        self.data = np.empty(5)
        self.ptr = 0
        self.counter = 0
        self.curve = self.plot(self.x[:self.ptr], self.data[:self.ptr], antialias=True)
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)

    def setSampleInterval(self, sample_interval):
        self.sample_interval = sample_interval

    def setTimeWindow(self, time_window):
        self.time_window = time_window
        self.curve.clear()
        self.initData()

    def getdata(self):
        if global_buffer.time_limit != 0 and self.x[self.ptr] >= global_buffer.time_limit:
            # TODO: this is not a good way to stop because you need the parent,
            # and the parents stop method calls your methods.
            # We need to thing about something different here.
            self.main_window.stop()

        while (self.counter > global_buffer.counter and self.counter > 0):
            self.counter -= 1

        return global_buffer.data[(self.counter % global_buffer.buffer_size)]

    def updateplot(self):
        """Update plot."""
        self.data[self.ptr] = self.getdata()
        self.x[self.ptr + 1] = self.x[self.ptr] + self.sample_interval
        self.ptr += 1
        self.counter += 1

        if self.ptr >= self.data.shape[0]:
            tmp = self.data
            xtmp = self.x
            self.data = np.empty(self.data.shape[0] + 5)
            self.x = np.empty(self.x.shape[0] + 5)
            self.data[:tmp.shape[0]] = tmp
            self.x[:xtmp.shape[0]] = xtmp
            self.curve.setData(self.x[:self.ptr], self.data[:self.ptr])

    def setCurveColor(self, r, g, b):
        """Set curve color"""
        self.curve.setPen(pg.mkPen(color=(r, g, b)))


class RealTimeRecordingPlotter(pg.PlotWidget):
    """Plots data (audio) in real time.

    Parameters:
        sample_interval (float): sample interval. Default 0.02 seconds.
        time_window (float): size (in time) for the main window. Default 20 seconds.
        main_window (MainWindow): main_window.
        parent (QWidget): parent.
    """

    def __init__(self, sample_interval=0.02, time_window=20., parent=None):
        super(RealTimeRecordingPlotter, self).__init__(parent)
        self.sample_interval = sample_interval
        self.time_window = time_window
        self.showGrid(x=True, y=True)
        self.setLabel('top', 'Input Real Time')
        self.setLabel('left', 'Amplitude', 'V')
        self.setLabel('bottom', 'Time', 's')
        self.curve = None
        global global_buffer

    def initData(self):
        """Initialize data for for plotting."""
        # self.sample_interval = 0.01
        # Forces update at 20 FPS, shouldn't be taxing to most systems
        self._interval = int(1 / 20 * 1000)

        self._bufsize = int(self.time_window / self.sample_interval)
        self.databuffer = collections.deque([0.0] * self._bufsize, self._bufsize)
        self.x = np.linspace(-self.time_window, 0.0, self._bufsize)
        self.y = np.zeros(self._bufsize, dtype=np.float)

        # Initializes audio listener
        self.audio = AudioRecord("output.wav", self.sample_interval)

        try:
            self.audio.begin_audio()
        except IOError as e:
            QMessageBox.information(self,
                                    self.tr('Information'),
                                    self.tr('No input device found, please make sure to plug it before open the '
                                            'program. Please, restart the program and try again.\n{}'.format(e)),
                                    QMessageBox.Ok)
            exit(1)

        # :TODO: needs to be separated the interval of plotting data from the acquire data.

        # Initializes the timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateplot)
        self.timer.start(self._interval)
        # Plot for the first time
        self.curve = self.plot(self.x, self.y, pen=(0, 255, 255), antialias=True)
        self.curve.clear()

    def setSampleInterval(self, sample_interval):
        """Sets the sample interval for plotting.

        Parameters:
            sample_interval (float): sample interval in seconds
        """
        self.sample_interval = sample_interval
        self.curve.clear()
        self.initData()

    def setTimeWindow(self, time_window):
        """Sets the time window for plotting.

        Parameters:
            time_window (float): size (in time) for the main window, in seconds.
        """
        self.time_window = time_window
        self.curve.clear()
        self.initData()

    def getdata(self):
        """Gets data for plotting."""
        b = self.audio.get_data_from_audio()[1]
        new = b[0]

        # This clipping of the signal prevents pyqtgraph from breaking due
        # to large random noise when some soundcards are initiated.
        # Prevents input overflow when program starts.
        if new > 1e+150:
            new = 1e+150

        if global_buffer.recording is True:
            global_buffer.counter += 1
            if global_buffer.counter >= global_buffer.buffer_size:
                global_buffer.clear()

            global_buffer.data[global_buffer.counter] = new

        return new

    def updateplot(self):
        """Update plot."""
        stp = self.getdata()
        self.databuffer.append(stp)
        self.y[:] = self.databuffer
        self.curve.setData(self.x, self.y)


class MainWindow(QMainWindow):
    """Main window class.
    Parameters:
        parent (QWidget): parent
    """

    def __init__(self, parent=None):
        global global_buffer

        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # Check new version
        self.setWindowTitle(app_name + '  ' + version)
        self.update = "NOT CHECKED ..."
        self.checkUpdate()
        self.filepath = ""
        # Initial state is none because there is no data acquired yet
        self.isSaved = None
        # Sample interval should be 0.02s to not overflow in XP
        self.ui.doubleSpinBoxSampleInterval.setMinimum(0.02)
        self.ui.doubleSpinBoxSampleInterval.setMaximum(0.5)
        self.ui.doubleSpinBoxSampleInterval.setValue(0.02)
        self.ui.doubleSpinBoxSampleInterval.setSingleStep(0.01)

        # Connecting actions
        # File actions
        # self.ui.actionNew.triggered.connect(self.newFile)
        # For now it cannot open a file
        # self.ui.actionOpen.triggered.connect(self.openFile)
        # self.ui.actionSave.triggered.connect(self.saveFile)

        self.ui.actionSave_As.triggered.connect(self.saveFileAs)
        self.ui.actionSave_As.setEnabled(False)
        self.ui.actionPrint_graph.triggered.connect(self.saveImageAs)
        self.ui.actionPrint_graph.setEnabled(False)

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
        self.plot_widget = RealTimeRecordingPlotter(sample_interval=0.02, time_window=20.)
        self.plot_widget.initData()
        self.ui.gridLayout_2.addWidget(self.plot_widget, 0, 1)
        self.plot_widget_rec = RecordingPlotter(sample_interval=0.02, time_window=5., main_window=self)
        self.ui.gridLayout_2.addWidget(self.plot_widget_rec, 1, 1)

        # Inputs
        self.ui.doubleSpinBoxSampleInterval.valueChanged.connect(self.plot_widget.setSampleInterval)
        self.ui.doubleSpinBoxSampleInterval.valueChanged.connect(self.plot_widget_rec.setSampleInterval)
        self.ui.doubleSpinBoxSampleInterval.valueChanged.connect(self.setSampleRate)

        # self.ui.doubleSpinBoxSampleRate.valueChanged.connect(self.setSampleInterval)
        self.ui.spinBoxWindowTime.valueChanged.connect(self.plot_widget.setTimeWindow)
        self.setSampleRate(self.ui.doubleSpinBoxSampleInterval.value())

    def checkUpdate(self):
        """Check update from internet."""

        url = 'https://api.github.com/repos/dpizetta/wavy/releases/latest'

        try:
            response = urllib.request.urlopen(url, timeout=20)
            tag_version = json.loads(response.read())
        except Exception:
            pass
        else:
            if str(version) >= str(tag_version['tag_name'][1:]):
                self.update = "Up to date!"
            else:
                self.update = "New version ({}) is available!".format(str(tag_version['tag_name']))
                QMessageBox.information(self,
                                        self.tr('Information'),
                                        self.tr('<p>Oh, there is a new version ({}) avaliable.\n'
                                                'Go to <a href="https://github.com/dpizetta/wavy/releases/latest">'
                                                'download!</a></p>.'.format(tag_version['tag_name'])),
                                        QMessageBox.Ok)

        self.ui.labelAbout.setText(self.tr(about + "\nVersion status: " + self.update))

    def setSampleRate(self, sample_interval):
        """Sets sample rate."""
        self.ui.doubleSpinBoxSampleRate.setValue(1. / sample_interval)

    def setSampleInterval(self, sample_rate):
        """Sets sample interval."""
        self.ui.doubleSpinBoxSampleInterval.setValue(1. / sample_rate)

    def callTools(self):
        """Call converting tool."""
        dlg = ConvertWave2Data()
        dlg.exec_()

    def createFileName(self):
        """Construct a new file name to save the data."""
        # Creates auto naming filename
        filename = 'new_wavy_data_' + time.strftime("%Y%m%d%H%M%S", time.gmtime())
        # Gets the current directory
        # base_path = os.path.abspath(".")
        self.filepath = os.path.join(self.base_path, filename)
        self.setWindowFilePath(self.filepath)

    def record(self):
        """Starts acquiring."""
        # Create a new filename for the current acquisition
        self.createFileName()
        # Checks if is saved before start a new recording
        if self.isSaved is False:
            answer = QMessageBox.question(
                self,
                self.tr('Question'),
                self.tr('Do you want to save your data before start a new record?'),
                QMessageBox.Yes | QMessageBox.No)
            if answer == QMessageBox.Yes:
                self.saveFileAs()

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

        global_buffer.time_limit = self.ui.spinBoxStopRecordingAfter.value()
        global_buffer.startRecording()

        self.isSaved = False

    def pause(self):
        """Pauses acquiring."""
        # TODO: We need to discuss if this is needed
        # because the time is not correctly saved

        if self.ui.actionPause.isChecked():
            # Stopping changing color and label
            self.plot_widget_rec.timer.stop()
            self.plot_widget_rec.setCurveColor(255, 153, 0)
            self.plot_widget_rec.setLabel('top', 'Paused ...')
            global_buffer.stopRecording()
        else:
            # Starting changing color and label
            self.plot_widget_rec.timer.start()
            self.plot_widget_rec.setCurveColor(255, 0, 0)
            self.plot_widget_rec.setLabel('top', 'Recording ...')
            global_buffer.startRecording()
        # Set enabled tool bar
        self.ui.toolBarFile.setEnabled(False)
        self.ui.menuFile.setEnabled(False)
        self.ui.menuTools.setEnabled(False)

    def stop(self):
        """Stops acquiring."""
        # Stopping changing color and label
        self.plot_widget_rec.timer.stop()
        self.plot_widget_rec.setCurveColor(0, 255, 0)
        self.plot_widget_rec.setLabel('top', 'Stopped ...')
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

        self.ui.actionSave_As.setEnabled(True)
        self.ui.actionPrint_graph.setEnabled(True)

        global_buffer.stopRecording()

    def savePNGFile(self, filepath):
        """Saves an image."""
        # This extension should not be removed
        # Exporter needs the extension to save correctly.
        filepath += ".png"
        logging.info('File path to save image: %s', filepath)
        self.plot_widget_rec.setBackground('w')
        exporter = pg.exporters.ImageExporter(self.plot_widget_rec.plotItem)
        self.plot_widget_rec.setBackground('k')
        exporter.export(filepath)

    def saveCSVFile(self, filepath):
        """Saves a data file."""
        # This extension should not be removed
        # Exporter needs the extension to save correctly.
        filepath += ".csv"
        logging.info('File path to save data: %s', filepath)
        exporter = pg.exporters.CSVExporter(self.plot_widget_rec.plotItem)
        exporter.export(filepath)

    def getDataFolder(self):
        """Get data folder option."""

        answer = QMessageBox.question(self,
                                      self.tr('Question'),
                                      self.tr('It seems the first time you run WavyTool. Do you want to choose '
                                              'a folder to keep exported data?'),
                                      QMessageBox.Yes | QMessageBox.No)
        if answer == QMessageBox.Yes:
            path = QFileDialog.getExistingDirectory(self,
                                                    self.tr('Data folder'),
                                                    os.path.expanduser('~'))
            if path:
                try:
                    # This string converting is needed because the return is a QString
                    self.base_path = os.path.splitext(str(path))[0]
                    with open('wavytool.config', 'w') as outfile:
                        json.dump({'data_folder': self.base_path}, outfile)
                except Exception as e:
                    QMessageBox.critical(self,
                                         self.tr('Critical'),
                                         self.tr('There was a problem set the default folder to save data:\n '
                                                 '{}'.format(str(e))),
                                         QMessageBox.Ok)
                else:
                    logging.info('The default folder is: %s', self.base_path)
                    QMessageBox.information(self,
                                            self.tr('Information'),
                                            self.tr('Default folder to save data was set up to:\n'
                                                    '{}.'.format(self.base_path)),
                                            QMessageBox.Ok)
        else:
            self.base_path = '.'

    def saveImageAs(self):
        """Saves image as."""

        path = QFileDialog.getSaveFileName(self,
                                           self.tr('Export recorded image ...'),
                                           os.path.splitext(self.filepath)[0] + '.png',
                                           self.tr("Image File (*.png)"))
        if path:
            try:
                # This string converting is needed because the return is a QString
                self.filepath = os.path.splitext(str(path))[0]
                self.savePNGFile(self.filepath)
            except Exception as e:
                QMessageBox.critical(self,
                                     self.tr('Critical'),
                                     self.tr('There was a problem to save image:\n {}'.format(str(e))),
                                     QMessageBox.Ok)
            else:
                logging.info('The image was saved in the file: %s', self.filepath)
                QMessageBox.information(self,
                                        self.tr('Information'),
                                        self.tr('Image was successfully exported.'),
                                        QMessageBox.Ok)

    def saveFileAs(self):
        """Saves data file as."""

        path = QFileDialog.getSaveFileName(self,
                                           self.tr('Save recorded data ...'),
                                           os.path.splitext(self.filepath)[0] + '.csv',
                                           self.tr("Data File (*.csv)"))
        if path:
            try:
                # This string converting is needed because the return is a QString
                self.filepath = os.path.splitext(str(path))[0]
                self.saveCSVFile(self.filepath)
            except Exception as e:
                self.isSaved = False
                QMessageBox.critical(self,
                                     self.tr('Critical'),
                                     self.tr('There was a problem to save data\n {}'.format(str(e))),
                                     QMessageBox.Ok)
            else:
                self.isSaved = True
                # self.ui.actionSave_As.setEnabled(False)
                logging.info('The data was saved in the file: %s', self.filepath)
                QMessageBox.information(self,
                                        self.tr('Information'),
                                        self.tr('Data was successfully saved.\n\nDATA SAVED IS REPRESENTED '
                                                'BY THE WINDOW RECORDING, IF YOU APPLY ZOOM ON IT, JUST '
                                                'DATA VISIBLE WILL BE SAVED!'),
                                        QMessageBox.Ok)

    def about(self):
        """Show the dialog about."""

        QMessageBox.about(self, self.tr('About'),
                          self.tr(about))

    def closeQuestion(self):
        """Asks about to close."""

        if self.isSaved is False:
            answer = QMessageBox.question(
                self,
                self.tr('Question'),
                self.tr('Do you want to save your data before exit?'),
                QMessageBox.Yes | QMessageBox.No)

            if answer == QMessageBox.Yes:
                self.saveFileAs()

        answer = QMessageBox.question(self,
                                      self.tr('Close'),
                                      self.tr('Do you want to exit?'),
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.No)

        return answer == QMessageBox.Yes

    def closeEvent(self, event):
        """Re implements close event."""
        if self.closeQuestion():
            self.plot_widget.timer.stop()
            self.plot_widget.audio.end_audio()

            if self.plot_widget_rec.curve is not None:
                self.plot_widget_rec.timer.stop()

            event.accept()
        else:
            event.ignore()
