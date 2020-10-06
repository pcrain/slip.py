#!/bin/bash
#Generate single-file bundle for slippi_viz.py

pyinstaller -F \
  --add-data "slippi_viz/app:app" \
  --add-binary "slippi_viz/slippc.exe:slippc.exe" \
  ./slippi_viz/slippi_viz.py
