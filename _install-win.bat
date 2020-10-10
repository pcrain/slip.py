@echo off
ECHO Leave this window open until installation is complete
ECHO Checking for Python / Pip
WHERE pip
IF %ERRORLEVEL% NEQ 0 (
  ECHO pip wasn't found in PATH
  IF EXIST %HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python38\Scripts\pip.exe (
    ECHO pip found in default location
    SET PATH="%PATH%;%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python38\Scripts;"
    @echo on
    %HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python38\Scripts\pip.exe install --user .
  ) ELSE (
    ECHO pip wasn't found in default location; please install pip to proceed
    ECHO You may close this window
    PAUSE
    EXIT /B
  )
) ELSE (
  ECHO pip found
  @echo on
  pip install --user .
)

rem Creating shortcut to slip.py
@echo off
rem https://superuser.com/questions/392061/how-to-make-a-shortcut-from-cmd
SETLOCAL ENABLEDELAYEDEXPANSION
SET LinkName=slip.py
SET Esc_LinkDest=%%HOMEDRIVE%%%%HOMEPATH%%\Desktop\!LinkName!.lnk
SET Esc_LinkTarget=%%HOMEDRIVE%%%%HOMEPATH%%\AppData\Roaming\Python\Python38\site-packages\slipdotpy\slip.py
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

ECHO Installation of slip.py successful! You may close this window
PAUSE
