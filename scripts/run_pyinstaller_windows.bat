python get_version.py
set /p texte=< got_version.temp  

set DATESTAMP=%DATE:~6,4%%DATE:~3,2%%DATE:~0,2%
set TIMESTAMP=%TIME:~0,2%%TIME:~3,2%
set NAME=Wavy
set SYSTEM=windows
set /p VERSION=< got_version.temp
set DATETIMES=%DATESTAMP%%TIMESTAMP%
set EXECUTABLE=%NAME%-%SYSTEM%-portable-v.%VERSION%-build.%DATETIMES%

del got_version.temp

cd  ..

del "out.log*"
del "*.pyc"
del "*.pyw"
del ".\build" /Q 
del "*pycache*"
del ".\dist" /Q

pyinstaller run.py ^
	--noconfirm ^
	--clean ^
	--log-level=INFO ^
    --specpath=dist ^
	--name=%EXECUTABLE% -F  ^
	--icon=.\wavy\images\symbol.ico 


echo "Creating list of imported library versions ..."
pip freeze > .\dist\lib_versions.info

echo "Compressing files ..."
cd .\dist
"C:\Program Files\7-Zip\7z.exe" a -tzip "%EXECUTABLE%.zip"  "%EXECUTABLE%.exe" "checksum.md5" "lib_versions.info"
cd ..
cd scripts

echo "Process finished ..."






