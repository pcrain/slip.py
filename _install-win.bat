SET PATH="%PATH%%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python38\Scripts;"
%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python38\Scripts\pip.exe install --user .
mklink "%HOMEDRIVE%%HOMEPATH%\Desktop\slippi_viz.bat" "%HOMEDRIVE%%HOMEPATH%\AppData\Roaming\Python\Python38\site-packages\slippi_viz\_run-win.bat"
PAUSE
