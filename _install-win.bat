SET PATH="%PATH%;%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python38\Scripts;"
%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python38\Scripts\pip.exe install --user .

rem Create a Shortcut https://superuser.com/questions/392061/how-to-make-a-shortcut-from-cmd
@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
SET LinkName=slip.py
SET Esc_LinkDest=%%HOMEDRIVE%%%%HOMEPATH%%\Desktop\!LinkName!.lnk
SET Esc_LinkTarget=%%HOMEDRIVE%%%%HOMEPATH%%\AppData\Roaming\Python\Python38\site-packages\slippi_viz\slippi_viz.py
SET cSctVBS=CreateShortcut.vbs
SET LOG=".\%~N0_runtime.log"
((
  echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
  echo sLinkFile = oWS.ExpandEnvironmentStrings^("!Esc_LinkDest!"^)
  echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
  echo oLink.TargetPath = oWS.ExpandEnvironmentStrings^("!Esc_LinkTarget!"^)
  echo oLink.Save
)1>!cSctVBS!
%SystemRoot%\System32\cscript.exe //nologo .\!cSctVBS!
DEL !cSctVBS! /f /q
)1>>!LOG! 2>>&1
PAUSE
