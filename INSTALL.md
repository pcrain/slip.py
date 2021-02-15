
### Windows Easy Install Instructions
  - Head to the [release page](https://github.com/pcrain/slip.py/releases/latest) and download the latest official release executable

### Windows Standard Install Instructions
  - [Download and extract the ZIP file containing the latest version of slip.py](https://github.com/pcrain/slip.py/archive/master.zip).
  - Install Python 3.8 from [the official website](https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe):
    - Make sure you install pip when prompted under "Optional Features"
    - You may skip this step if Python is already installed
  - Double-click "\_install-win.bat"
  - If the installation is successful, a "slip.py" Desktop shortcut will be created
  - Double-click "slip.py" to launch the Slip.py Browser

### Linux / OSX Standard Install Instructions
  - [Download and extract the ZIP file containing the latest version of slip.py](https://github.com/pcrain/slip.py/archive/master.zip).
  - Install Python 3.8 using your package manager (Pip should be included)
    - While Python 3.8 is recommended, Python 3.6 and up should work fine
  - Make and install [slippc](https://github.com/pcrain/slippc)
  - Create a symlink to the slippc binary in your /home/$USER/bin directory (or anywhere else in your `PATH`) using:

    `ln -s </path/to/slippc> ~/bin/slippc`

  - Navigate to the directory of this install file in a terminal and run the command:

    `pip install --user .`

  - If the installation is successful, slip.py will be installed to ~/.local/lib/python3.8/site-packages/slipdotpy/slip.py
  - Run slip.py to launch the Flask desktop application
  - Alternately, run slip-server.py in a terminal to launch the Flask web application
  - [Optional] You may wish to create a symlink to slip.py and/or slip-server.py for easier access
