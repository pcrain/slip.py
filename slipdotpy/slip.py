#!/usr/bin/python
#Run slip.py in Desktop mode

#Import standard modules
import os, sys, socket, time, sqlite3

PY_VER = sys.version[:3].replace(".","")
if int(PY_VER) < 36:
  print("You must use at least Python 3.6.x to run this App")
  print(f"Your version: {sys.version.split()[0]}")
  input("Press any key to exit")
  sys.exit(1)

#On Windows, make sure necessary Python paths are in PATH
if os.name == 'nt':
  sys.path.append(os.path.expanduser(os.path.join(
    "~","AppData","Roaming","Python",f"Python{PY_VER}","site-packages")))
  flaskpath = os.path.expanduser(os.path.join(
    "~","AppData","Roaming","Python",f"Python{PY_VER}","Scripts"))
  sys.path.append(os.path.expanduser(flaskpath))

#Import app config
from app.config import Config
from app.migrator import Migrator

#Migrate databases as necessary
print("TODO: finish migrations")
# Migrator(Config).run()
# sys.exit(1)

#If we're running thie directly, verify our requested port is open
if __name__ == "__main__":
  try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('localhost',Config.SITE_PORT))
    sock.close()
  except OSError:
    print(f"Slip.py port {Config.SITE_PORT} already in use!")
    print(f"Close all instances of the Slip.py Browser and try again")
    print(f"If this error persists, you may need to reboot your computer")
    print("Exiting in 5 seconds")
    time.sleep(5)
    sys.exit(1)

#Import remaining app modules
from app import create_app, db, generators #, cli
from app.models import User, Replay

#Create app factory
app = create_app()
generators.config_generators(app)

#Create context processors for app
@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User, 'Replay': Replay}

@app.context_processor
def config_var():
    return app.config

#If we're running this script directly, launch the web GUI
def launch_web_gui():
  from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets
  #Next three classes / functions are inlined code (modified) from pyfladesk
  class ApplicationThread(QtCore.QThread):
    def __init__(self, application, port):
      super(ApplicationThread, self).__init__()
      self.application = application
      self.port        = port

    def __del__(self):
      self.wait()

    def run(self):
      self.application.run(port=self.port, threaded=True)

  class WebPage(QtWebEngineWidgets.QWebEnginePage):
    def __init__(self, root_url):
      super(WebPage, self).__init__()
      self.root_url = root_url

    def home(self):
      self.load(QtCore.QUrl(self.root_url))

    def acceptNavigationRequest(self, url, kind, is_main_frame):
      """Open external links in browser and internal links in the webview"""
      ready_url = url.toEncoded().data().decode()
      is_clicked = kind == self.NavigationTypeLinkClicked
      if is_clicked and self.root_url not in ready_url:
        QtGui.QDesktopServices.openUrl(url)
        return False
      return super(WebPage, self).acceptNavigationRequest(url, kind, is_main_frame)

  class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None,window=None):
      self.window = window
      QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
      menu          = QtWidgets.QMenu(parent)
      restoreAction = menu.addAction("Show / Hide Window")
      exitAction    = menu.addAction("Exit Slip.py Browser")
      restoreAction.triggered.connect(self.restore)
      exitAction.triggered.connect(self.exit)
      self.setContextMenu(menu)

    def restore(self):
      if self.window.windowState() == QtCore.Qt.WindowMinimized:
        # Window is minimised. Restore it.
        self.window.setWindowState(QtCore.Qt.WindowNoState)
        self.window.raise_()
        self.window.activateWindow()
        self.window.setFocus(True)
        self.window.showMaximized()
        self.window.showNormal()
      else:
        self.window.setWindowState(QtCore.Qt.WindowMinimized)

    def exit(self):
      QtCore.QCoreApplication.exit()

  def init_gui(application, port=0, width=-1, height=-1,
    window_title="PyFladesk", icon="appicon.png", argv=None):
      if argv is None:
          argv = sys.argv

      if port == 0:
          sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          sock.bind(('localhost', 0))
          port = sock.getsockname()[1]
          sock.close()

      # Application Level
      qtapp  = QtWidgets.QApplication(argv)
      webapp = ApplicationThread(application, port)
      webapp.start()
      qtapp.aboutToQuit.connect(webapp.terminate)

      # Main Window Level
      window = QtWidgets.QMainWindow()
      if width >= 1 and height >= 1:
        window.resize(width, height)
      else:
        screen = qtapp.primaryScreen()
        size   = screen.size()
        rect   = screen.availableGeometry()
        window.resize(rect.width(), rect.height())
      window.setWindowTitle(window_title)
      window.setWindowIcon(QtGui.QIcon(icon))

      # Tray Icon
      w        = QtWidgets.QWidget()
      trayIcon = SystemTrayIcon(QtGui.QIcon(icon), w, window)
      trayIcon.show()

      # WebView Level
      webView = QtWebEngineWidgets.QWebEngineView(window)
      webView.page().profile().clearHttpCache() #Clear CSS / JS / image cache
      window.setCentralWidget(webView)

      # WebPage Level
      homepage = WebPage('http://localhost:{}'.format(port))
      homepage.home()
      webView.setPage(homepage)

      # Keyboard shortcuts
      back     = QtWidgets.QShortcut(QtGui.QKeySequence("Backspace"), window);
      back.activated.connect(lambda : webView.back()) #back a page
      back2    = QtWidgets.QShortcut(QtGui.QKeySequence("Alt+Left"), window);
      back2.activated.connect(lambda : webView.back()) #back a page
      forward  = QtWidgets.QShortcut(QtGui.QKeySequence("Alt+Right"), window);
      forward.activated.connect(lambda : webView.forward()); #forward a page
      reset    = QtWidgets.QShortcut(QtGui.QKeySequence("F12"), window);
      reset.activated.connect(lambda : homepage.home()); #hard app reset

      window.showMaximized()
      return qtapp.exec_()

  #Get the real location of this script and change working directory appropriately
  location = (os.path.dirname(os.path.realpath(os.path.abspath(__file__))))
  os.chdir(location)
  init_gui(app,
    port         = app.config["SITE_PORT"],
    window_title = app.config["SITE_NAME"],
    icon         = app.config["SITE_ICON"]
    )

if __name__ == "__main__":
  launch_web_gui()
