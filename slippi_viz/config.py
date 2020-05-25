#!/usr/bin/python
import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #Global template variables
    SITE_NAME                      = "Slip.py Browser"
    SITE_VERSION                   = "0.1.0"

    #Data location variables
    STATIC_FOLDER                  = os.path.join(basedir,"app","static")
    if os.name == 'nt':
      DATA_FOLDER                  = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'),"slippi_viz")
      ANALYZER                     = "slippc.exe"
    else:
      DATA_FOLDER                  = os.path.join(os.path.expanduser("~"),".local","share","slippi_viz")
      ANALYZER                     = os.path.join(os.path.expanduser("~"),"bin","slippc")
    UPLOAD_FOLDER                  = os.path.join(DATA_FOLDER,"uploads")
    REPLAY_FOLDER                  = os.path.join(DATA_FOLDER,"replays")
    LOG_FOLDER                     = os.path.join(DATA_FOLDER,"logs")
    TMP_FOLDER                     = os.path.join(DATA_FOLDER,"_tmp")
    SQLALCHEMY_DATABASE_URI        = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(DATA_FOLDER, 'app.db')

    #Other config variables
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    POSTS_PER_PAGE                 = 60
    SIMULTANEOUS_UPLOADS           = 100
    FORCE_COMPRESSION              = False
    SECRET_KEY                     = os.urandom(32)
