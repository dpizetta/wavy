cd ../wavy
#pyside-uic -o mw_wavy.py mw_wavy.ui 
pyuic4 mw_wavy.ui -o mw_wavy.py
#pyside-uic -o dlg_wav2dat.py dlg_wav2dat.ui 
pyuic4 dlg_wav2dat.ui -o dlg_wav2dat.py
#pyside-rcc -o images/rc_wavy_rc.py images/rc_wavy.qrc 
pyrcc4 images/rc_wavy.qrc -o images/rc_wavy_rc.py
cd ../..

