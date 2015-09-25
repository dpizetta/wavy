echo "Initiating installer, downloading files"
mkdir C:\Wavy
echo "Downloading Miniconda ..."
cscript.exe downloadfiles.vbs "https://repo.continuum.io/miniconda/Miniconda-latest-Windows-x86.exe" "C:\Wavy\Miniconda-latest-Windows-x86.exe" 
echo "Downloading PyAudio ..."
cscript.exe downloadfiles.vbs "https://people.csail.mit.edu/hubert/pyaudio/packages/pyaudio-current.py27.exe" "C:\Wavy\pyaudio-current.py27.exe" 
echo "Installing Miniconda ..."
C:\Wavy\Miniconda-latest-Windows-x86.exe
echo "Updating Miniconda ..."
conda update conda
echo "Instaling dependencies: Numpy ..."
conda install numpy
echo "Instaling dependencies: PyQtGraph ..."
conda install pyqtgraph
echo "Installing PyAudio ..."
C:\Wavy\pyaudio-current.py27.exe
echo "Installing Wavy ..."
C:\Miniconda32\python.exe setup.py install
