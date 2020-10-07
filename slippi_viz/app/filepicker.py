#!/usr/bin/python
#Small script for picking files / folders

from PyQt5 import QtCore, QtWidgets
import sys, os

class ApplicationThread(QtCore.QThread):
  def __init__(self):
    super(ApplicationThread, self).__init__()

  def run(self):
    title = "Select a File"
    try: #Keep iterating through argv until we hit the end of the list
      title = sys.argv[1]
    except:
      pass
    options     = QtWidgets.QFileDialog.Options()
    # options    |= QtWidgets.QFileDialog.DontUseNativeDialog
    fileName, _ = QtWidgets.QFileDialog.getOpenFileName(
      None,
      title,
      "",
      "All Files (*)",
      options=options)
    if fileName:
      print(os.path.normpath(fileName),end="")

def main():
  webapp = ApplicationThread()
  qtapp  = QtWidgets.QApplication(sys.argv)
  qtapp.aboutToQuit.connect(webapp.terminate)
  webapp.run()

if __name__ == "__main__":
  main()
