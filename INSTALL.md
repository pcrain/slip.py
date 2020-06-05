### Windows Install Instructions
  - Install Python 3.8:
    - Download and install "Windows x86-64 executable installer" at the bottom of [this page](https://www.python.org/downloads/release/python-380/)
  - Install Pip:
    - Download "get-pip.py" from [this page](https://www.liquidweb.com/kb/install-pip-windows/)
    - Double click the file to install it
  - Install slip.py by double-clicking "\_install-win.bat"
  - If the installation is successful, a "slip.py" shortcut will be created on your Desktop
  - Double-click slip.py to launch the Flask application. Note that the command prompt must remain open when using slip.py

### Linux / OSX Install Instructions
  - Install Python 3.8 and pip using your package manager
  - Make and install [slippc](https://github.com/pcrain/slippc)
  - Create a symlink to the slippc binary in your home bin directory using:

    `ln -s /path/to/slippc ~/bin/slippc`

  - Navigate to the directory of this install file in a terminal and run the command:

    `pip install --user .`

  - If the installation is successful, slip.py will be installed to ~/.local/lib/python3.8/site-packages/slippi_viz/slip.py
  - [Optional] You may want to create a Desktop to slip.py for easier access.
  - Run slip.py in a terminal to launch the Flask application.
