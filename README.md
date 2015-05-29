# Wavy
Wavy acquire signals from mic and saves as data (.csv) or exports as image (.png). Wavy has two graphic areas, which represents the real time data from mic (started when the software runs), and the recording area that starts when clicked on Record button. All saved data is relative from recorded area.

![alt tag](https://cloud.githubusercontent.com/assets/5084939/7890891/5014ffee-061f-11e5-84c9-b3c77f91f123.png)

The recording area has three states: recording when the line is red, paused when the line is orange, and green when the recording was stopped.

Wavy automatically suggests the name for your data when is saved as the new_wavy_data_yymmddHHMMSS.ext.

## Problems and improvements

If you find any problems in this program, please let us know using the [Issues System] (https://github.com/dpizetta/wavy/issues) provided by GitHub. This is the correct way to keep us alert and how provide information about the development for you. Thanks in advance.

## About

Wavy was developed to be a simple software to acquire data from microphone channel, plot and save them. The main use is to provide an acquisition software for Ruchardt's method in Physics Laboratory at Sao Carlos Institute of Physics - University of Sao Paulo.

## Authors

* [Daniel Cosmo Pizetta] (https://github.com/dpizetta)
* [Wesley Daflita] (https://github.com/Wa59)

## Acknowledgment

Professors

* PhD Fernando Fernandes Paiva
* PhD Valmor Roberto Mastelaro

Technicians

* Antenor Fabbri Petrilli Filho
* Cláudio Boense Bretas
* Jae Antonio de Castro Filho


# Dependencies

* Python >= 2.7 < 3
* PyQt4
* pyqtgraph
* numpy
* PyAudio (also PortAudio)

Notes: The easiest way to install all those things is: 
* Install Python 2.7 (or Anaconda/Miniconda that comes with numpy and other better libraries)
* Use pip install pyqtgraph (installs PyQt4 automatically)
* Use pip install numpy
* Use pip install pyaudio

For Windows users, PyAudio requires more things, the better way is to download the .exe installer from PyAudio website (that includes PortAudio) and install it. If you are using Anaconda or Miniconda, replace the 'pip' command for 'conda'.

# Running the code

To run wavy without installing, use

`$ python run.py`

# Installing

To install it, do the following

`$ python setup.py install`

# Installing as developer

To install it as a developer, which means install it like a library but keeping it in the same place it is and providing the auto update if any changes are made.

`$ python setup.py install develop`
