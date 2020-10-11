@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

ECHO Leave this window open until installation is complete

ECHO Identifying path to Python / Pip
SET found=0
FOR /L %%G IN (6,1,9) DO (
  SET pyver=3%%G

  rem Python / Pip installed for all users
  SET abase=%HOMEDRIVE%\Python3%%G
  SET apip=!abase!\Scripts

  IF EXIST !apip!\pip.exe (
    SET base=!abase!
    SET pip=!apip!
    SET found=1
    )
  if !found!==1 GOTO :found

  rem Python / Pip installed for current user
  SET ubase=%HOMEDRIVE%%HOMEPATH%\AppData\Local\Programs\Python\Python3%%G
  SET upip=!ubase!\Scripts
  IF EXIST !upip!\pip.exe (
    SET base=!ubase!
    SET pip=!upip!
    SET found=1
    )
  if !found!==1 GOTO :found
  )
ECHO Could not find pip; cannot proceed with installation
ECHO You may close this window
PAUSE
GOTO :eof



:found
ECHO Python version is %pyver%
ECHO Python path is %base%
ECHO Pip path is %pip%
SET Esc_LinkTarget=%%HOMEDRIVE%%%%HOMEPATH%%\AppData\Roaming\Python\Python%pyver%\site-packages\slipdotpy\slip.py
ECHO Link Target is %Esc_LinkTarget%
GOTO :continue

:continue
ECHO Checking for Python / Pip
WHERE pip
IF %ERRORLEVEL% NEQ 0 (
  ECHO pip wasn't found in PATH
  IF EXIST %pip%\pip.exe (
    ECHO pip for Python %pyver% found at %pip%
    SET PATH="%PATH%;%pip%;"
    @echo on
    %pip%\pip.exe install --user .
  ) ELSE (
    ECHO pip was not found; please install python 3.8 and pip to proceed
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
SET Esc_LinkTarget=%%HOMEDRIVE%%%%HOMEPATH%%\AppData\Roaming\Python\Python%pyver%\site-packages\slipdotpy\slip.py
SET Esc_LinkIcon=%%HOMEDRIVE%%%%HOMEPATH%%\AppData\Roaming\Python\Python%pyver%\site-packages\slipdotpy\app\static\icons\wolfhead.ico
SET cSctVBS=CreateShortcut.vbs
SET LOG=".\%~N0_runtime.log"
((
  echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
  echo sLinkFile = oWS.ExpandEnvironmentStrings^("!Esc_LinkDest!"^)
  echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
  echo oLink.TargetPath = oWS.ExpandEnvironmentStrings^("!Esc_LinkTarget!"^)
  echo oLink.IconLocation = oWS.ExpandEnvironmentStrings^("!Esc_LinkIcon!"^)
  echo oLink.Save
)1>!cSctVBS!
%SystemRoot%\System32\cscript.exe //nologo .\!cSctVBS!
DEL !cSctVBS! /f /q
)1>>!LOG! 2>>&1

ECHO Installation of slip.py successful! You may close this window
PAUSE
