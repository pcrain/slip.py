#!/usr/bin/python
#Run Slippi Viz in the default web browser

import sys

PY_VER = sys.version[:3].replace(".","")
if int(PY_VER) < 36:
  print("You must use at least Python 3.6.x to run this App")
  print(f"Your version: {sys.version.split()[0]}")
  input("Press any key to exit")
  sys.exit(1)

from app.config import Config
import os, sys, subprocess

#Set appropriate environment variables
os.environ["FLASK_APP"]      = "slip.py"
os.environ["FLASK_DEBUG"]    = "1"
os.environ["FLASK_RUN_PORT"] = str(Config.SITE_PORT)

APP_URL= "http://127.0.0.1:"+str(Config.SITE_PORT)

#On Windows, make sure necessary Python paths are in PATH
if os.name == 'nt':
  sys.path.append(os.path.expanduser(os.path.join(
    "~","AppData","Roaming","Python",f"Python{PY_VER}","site-packages")))
  flaskpath = os.path.expanduser(os.path.join(
    "~","AppData","Roaming","Python",f"Python{PY_VER}","Scripts"))
  sys.path.append(os.path.expanduser(flaskpath))
  flaskexec = os.path.join(flaskpath,"flask.exe")
else:
  flaskexec = "flask"

#Get the real location of this script and change working directory appropriately
location = (os.path.dirname(os.path.realpath(os.path.abspath(__file__))))
os.chdir(location)

#Open the app's main page in the default web browser
if sys.platform=='win32':
    os.startfile(APP_URL)
elif sys.platform=='darwin':
    subprocess.Popen(['open', APP_URL])
else:
    try:
        subprocess.Popen(['xdg-open', APP_URL], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    except OSError:
        print('Please open a browser on: '+APP_URL)

#Launch the flask app
os.execlp(flaskexec,flaskexec,"run")
