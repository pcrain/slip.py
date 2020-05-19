#!/usr/bin/python
from app import create_app, db, generators #, cli
from app.models import User, Replay

import os

app = create_app()
generators.config_generators(app)

def init_slippi_viz():
  # print(app.config)
  os.makedirs(app.config["DATA_FOLDER"],exist_ok=True)
  os.makedirs(app.config["UPLOAD_FOLDER"],exist_ok=True)
  os.makedirs(app.config["REPLAY_FOLDER"],exist_ok=True)
  os.makedirs(app.config["SCAN_FOLDER"],exist_ok=True)
  os.makedirs(app.config["TMP_FOLDER"],exist_ok=True)

  if os.name == 'nt':
    default_slippi_path = os.path.join(os.path.expanduser("~"),"Desktop","FM-v5.9-Slippi-r18-Win","Slippi")
  else:
    default_slippi_path = os.path.join(os.path.expanduser("~"),"Slippi")

  if os.path.exists(default_slippi_path):
    default_slippi_link = os.path.join(app.config["SCAN_FOLDER"],"Slippi")
    if not os.path.exists(default_slippi_link):
      os.symlink(default_slippi_path,default_slippi_link)
      pass

@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User, 'Replay': Replay}

@app.context_processor
def config_var():
    return app.config

init_slippi_viz()
