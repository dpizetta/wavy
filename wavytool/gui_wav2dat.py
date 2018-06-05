#! python
# -*- coding: utf-8 -*-

"""
This program has been used to translate the wav file to dat format.

:author: Daniel C. Pizetta
:contact: daniel.pizetta@usp.br
:since: 2013/05/17

"""

import array
import os
import wave
import sys

from qtpy.QtCore import QObject, Qt
from qtpy.QtWidgets import QDialog, QFileDialog, QMessageBox, QApplication
from wavytool.dlg_wav2dat import Ui_Dialog

qobject = QObject()


class ConvertWave2Data(QDialog):

    def __init__(self, parent=None):
        """Constructor."""

        # graphical interface
        super(ConvertWave2Data, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # properties
        self.path_to_read = ''
        self.path_to_write = ''
        self.number_of_channels = 0
        self.sample_width = 0
        self.frame_rate = 0
        self.number_of_frames = 0
        self.compression_name = None
        self.frames = []

        # link actions and signals to methods and slots

        # to read
        self.ui.pushButton_path_to_read.clicked.connect(lambda: self.setPathToReadWave(''))

        # options
        self.ui.checkBox_same_name.stateChanged.connect(self.changePathToWrite)

        # to write
        self.ui.pushButton_path_to_write.clicked.connect(lambda: self.setPathToWriteData(''))
        self.ui.pushButtonConvert.clicked.connect(lambda: self.writeData(self.path_to_write))
        self.ui.pushButtonCancel.clicked.connect(self.close)

    def changePathToWrite(self, use_same_path=0):
        """Change the path on the interface."""
        # construct the path based on the path to read
        if use_same_path == 2:
            path = os.path.join(os.path.dirname(self.path_to_read),
                                os.path.splitext(os.path.basename(self.path_to_read))[0]) + '.dat'
            self.setPathToWriteData(os.path.abspath(path))
            self.ui.lineEdit_path_to_write.setText(self.path_to_write)
            self.ui.lineEdit_path_to_write.setEnabled(False)
            self.ui.pushButton_path_to_write.setEnabled(False)
        else:
            self.ui.lineEdit_path_to_write.setText('')
            self.ui.lineEdit_path_to_write.setEnabled(True)
            self.ui.pushButton_path_to_write.setEnabled(True)

    def setPathToReadWave(self, path=''):
        """Set path to read."""

        if not path:
            path = QFileDialog.getOpenFileName(self,
                                               self.tr("Load WAVE file"),
                                               self.tr("WAVE File (*.wav)"))[0]
        # set path
        self.path_to_read = os.path.abspath(path)
        # set path on the graphical interface
        self.ui.lineEdit_path_to_read.setText(self.path_to_read)
        # read the wav file
        self.readWave()

    def setPathToWriteData(self, path=''):
        """Set path to write."""

        if not path:
            path = QFileDialog.getOpenFileName(self,
                                               self.tr("Create DATA file"),
                                               self.path_to_read,
                                               self.tr("DATA File (*.dat)"))[0]
        # set path
        self.path_to_write = os.path.abspath(path)
        # set path on the graphical interface
        self.ui.lineEdit_path_to_write.setText(self.path_to_write)

    def readWave(self):
        """Read the wav file."""

        # Reading the file and load the values
        try:
            wav_file = wave.open(self.path_to_read, 'rb')
        except Exception as e:
            QMessageBox.critical(QApplication.topLevelWidgets()[0],
                                 qobject.tr('Problem to read WAVE file.'),
                                 qobject.tr('Error: {}').format(str(e)),
                                 QMessageBox.Ok)

        # Extracting informations
        try:
            self.number_of_channels = wav_file.getnchannels()
            self.sample_width = wav_file.getsampwidth()
            self.frame_rate = wav_file.getframerate()
            self.number_of_frames = wav_file.getnframes()
            self.compression_name = wav_file.getcompname()

        except Exception as e:
            QMessageBox.critical(QApplication.topLevelWidgets()[0],
                                 qobject.tr('Problem with WAVE properties.'),
                                 qobject.tr('Error: {}').format(str(e)),
                                 QMessageBox.Ok)

        # Extracting data
        try:
            self.frames = wav_file.readframes(self.number_of_frames)
        except Exception as e:
            QMessageBox.critical(QApplication.topLevelWidgets()[0],
                                 qobject.tr('Problem with WAVE data.'),
                                 qobject.tr('Error: {}').format(str(e)),
                                 QMessageBox.Ok)

        # set information on the interface
        self.ui.label_file_name.setText(str(os.path.splitext(os.path.basename(self.path_to_read))[0]))
        self.ui.label_size.setText(str(self.sample_width * self.number_of_frames + 44))
        self.ui.label_number_of_channels.setText(str(self.number_of_channels))
        self.ui.label_frame_rate.setText(str(self.frame_rate))
        self.ui.label_number_of_frames.setText(str(self.number_of_frames))
        self.ui.label_sample_width.setText(str(self.sample_width))
        self.ui.label_compression.setText(str(self.compression_name))

        wav_file.close()

    def information(self):
        """Get information about the file."""

        dic_information = {}
        dic_information['Number of Channels'] = self.number_of_channels
        dic_information['Sample Width'] = self.sample_width
        dic_information['Frame Rate'] = self.frame_rate
        dic_information['Number of Frames'] = self.number_of_frames
        dic_information['Compression Name'] = self.compression_name

        return dic_information

    def data(self):
        """Get data in the file."""

        return array.array('f', self.frames)

    def writeData(self, path=''):
        """Write dat file."""

        self.ui.progressBar.setRange(0, self.number_of_frames)

        if self.path_to_write == '':
            self.setPathToWriteData()

        file_ = open(self.path_to_write, 'wb')

        for index in range(0, self.number_of_frames + 2, 2):
            self.ui.progressBar.setValue(index)
            file_.write(str(float(index) * (1.0 / self.frame_rate)) +
                        '    ' + str(SLInt16("foo").parse(self.frames[index:index + 2])))

        QMessageBox.information(QApplication.topLevelWidgets()[0],
                                qobject.tr('Information.'),
                                qobject.tr('Conversion concluded successfully.'),
                                QMessageBox.Ok)

        file_.close()

        if self.ui.checkBox_information.isChecked is True:
            return True

        return True


def main():

    app = QApplication(sys.argv)
    window = ConvertWave2Data()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
