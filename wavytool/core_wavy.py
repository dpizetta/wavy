#! python
# -*- coding: utf-8 -*-

import wave

import numpy

import pyaudio


class AudioRecord():
    """Class to record audio data."""
    def __init__(self, filename="output.wav", interval=1):
        self.outputFilename = filename
        self.rate = 22050
        self.interval = interval
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.port = None
        self.stream = None

    def begin_audio(self):
        # You must call this before get_data_from_audio, just ONCE
        # Initializes just if there is no self.stream opened yet
        if self.stream is None:
            self.port = pyaudio.PyAudio()

            # Forces the soundcard's prefered sample rate
            self.rate = int(self.port.get_device_info_by_index(0)['defaultSampleRate'])
            self.chunk = int(self.interval * self.rate)

            self.stream = self.port.open(format=self.format, channels=self.channels, rate=self.rate, input=True, frames_per_buffer=self.chunk)
            self.stream.stop_stream()

    def get_data_from_audio(self):
        # Before you call this function, you need to call - ONCE, begin_audio()
        # You will call this function every time you need new data
        # After you call this function you need to call end_audio(), ONCE!

        data_array = numpy.zeros(self.chunk, dtype=numpy.float)
        data_stream = None

        # If there is a self.stream opened
        if self.stream is not None:
            self.stream.start_stream()
            # String of bytes
            data_stream = self.stream.read(self.chunk)
            # Array of float normalized 0 - 5V
            data_array = (numpy.fromstring(data_stream, dtype=numpy.int16) / 32768.0) * 5.0

        return data_stream, data_array

    def end_audio(self):
        # You must call this after get_data_from_audio, just ONCE
        # If there is a self.stream opened
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        # Terminate the self.port connection - important
        try:
            self.port.terminate()
        except AttributeError:
            pass
        else:
            self.port = None

    def save_wave(self, frames):

        wf = wave.open(self.outputFilename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.port.get_sample_size(self.format))
        wf.setframe(self.rate)
        wf.writeframes(b''.join(frames))
        wf.close()
