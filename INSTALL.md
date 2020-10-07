### Windows Install Instructions
  - Install Python 3.8.6 from [the official website](https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe):
    - You may skip this step if Python is already installed
  - Double-click "\_install-win.bat"
  - If the installation is successful, a "slip.py" Desktop shortcut will be created
  - Double-click "slip.py" to launch the Slip.py Browser

### Linux / OSX Install Instructions
  - Install Python 3.8 and pip using your package manager
  - Make and install [slippc](https://github.com/pcrain/slippc)
  - Create a symlink to the slippc binary in your /home/$USER/bin directory (or anywhere else in your `PATH`) using:

    `ln -s </path/to/slippc> ~/bin/slippc`

  - Navigate to the directory of this install file in a terminal and run the command:

    `pip install --user .`

  - If the installation is successful, slip.py will be installed to ~/.local/lib/python3.8/site-packages/slippi_viz/slip.py
  - Run slippi_viz.py to launch the Flask desktop application
  - Alternately, run slip.py in a terminal to launch the Flask web application
  - [Optional] You may wish to create a symlink to slippi_viz.py and/or slip.py for easier access
