SET PATH="%PATH%;%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python38\Scripts;"
%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python38\Scripts\pip.exe install --user .
mklink "%HOMEDRIVE%%HOMEPATH%\Desktop\slip.py" "%HOMEDRIVE%%HOMEPATH%\AppData\Roaming\Python\Python38\site-packages\slippi_viz\slip.py"
PAUSE
