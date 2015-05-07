import pyaudio
import wave
import numpy

WAVE_OUTPUT_FILENAME = "output.wav"

RATE = 1000
CHUNK = 1
FORMAT = pyaudio.paInt16
CHANNELS = 1
PORT = None
STREAM = None


def begin_audio():
    # You must call this before get_data_from_audio, just ONCE

    global STREAM, PORT, RATE, CHUNK, FORMAT, CHANNELS
    # Initializes just if there is no stream opened yet
    if STREAM is None:
        PORT = pyaudio.PyAudio()
        STREAM = PORT.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        STREAM.stop_stream()


def get_data_from_audio():
    # Before you call this function, you need to call - ONCE, begin_audio()
    # You will call this function every time you need new data
    # After you call this function you need to call end_audio(), ONCE!

    global STREAM, PORT, RATE, CHUNK
    # If there is a stream opened
    if STREAM is not None:
        STREAM.start_stream()
        # String of bytes
        data_stream = STREAM.read(CHUNK)
        # Array of float normalized 0 - 5V
        data_array = (numpy.fromstring(data_stream, dtype=numpy.int16) / 32768.0) * 5.0

    return data_stream, data_array


def end_audio():
    # You must call this after get_data_from_audio, just ONCE

    global STREAM, PORT
    # If there is a stream opened
    if STREAM:
        STREAM.stop_stream()
        STREAM.close()
    # Terminate the port connection - important!
    PORT.terminate()


def save_wave(frames, filename=WAVE_OUTPUT_FILENAME, ):

    global PORT, RATE, CHUNK, FORMAT, CHANNELS

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(PORT.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


# begin_audio()
# for i in range(0,10):
#     a,b = get_data_from_audio()
#     print b
# end_audio()
