#!/bin/bash

# export WINEPATH="Z:\\home\\pretzel\\downloads\\winpy\\python\\Lib\\site-packages\\"

# wine cmd
# wine /home/pretzel/downloads/winpy/python/python.exe /home/pretzel/downloads/winpy/python/Scripts/pip.exe

WINEPATH="C:\\users\\pretzel\\Application Data\\Python\\Python38\\Scripts" wine pyinstaller \
  -d all --noupx --noconfirm \
  --add-data "slippi_viz\\app;app" \
  --add-binary "slippi_viz\\slippc.exe;slippc.exe" \
  slippi_viz\\slippi_viz.py
