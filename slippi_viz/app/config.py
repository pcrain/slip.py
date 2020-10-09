#!/usr/bin/python
import sys, os, multiprocessing

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #User config variables
    POSTS_PER_PAGE                 = 60
    SIMULTANEOUS_UPLOADS           = 100
    MAX_SCAN_THREADS               = multiprocessing.cpu_count()
    DEF_STATS                      = "?submit=&ndays=28" #Default stats page query
    ANALYZE_MISSING                = True #If True, recreate JSONs when entries aren't found in database

    #Global template variables
    SITE_VERSION                   = "0.4.4"
    SITE_NAME                      = "Slip.py Browser"
    SITE_PORT                      = 5050
    SITE_ICON                      = os.path.join(basedir,"static","icons","wolfhead.png")

    #Data location variables
    INSTALL_FOLDER                 = os.path.dirname(basedir)
    STATIC_FOLDER                  = os.path.join(basedir,"static")
    if os.name == 'nt':
      DEF_REPLAY_FOLDER            = os.path.join(os.path.expanduser("~"),"Documents","Slippi")
      DATA_FOLDER                  = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'),"slippi_viz")
      ANALYZER                     = "slippc.exe"
    else:
      DEF_REPLAY_FOLDER            = os.path.join(os.path.expanduser("~"),"Slippi")
      DATA_FOLDER                  = os.path.join(os.path.expanduser("~"),".local","share","slippi_viz")
      ANALYZER                     = "slippc"
    UPLOAD_FOLDER                  = os.path.join(DATA_FOLDER,"uploads")
    REPLAY_FOLDER                  = os.path.join(DATA_FOLDER,"replays")
    LOG_FOLDER                     = os.path.join(DATA_FOLDER,"logs")
    LOG_FILE                       = 'slippi_viz.log'
    TMP_FOLDER                     = os.path.join(DATA_FOLDER,"_tmp")
    SQLALCHEMY_DATABASE_URI        = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(DATA_FOLDER, 'app.db')

    #Other config variables
    SECRET_KEY                     = os.urandom(32)
    EXECUTOR_PROPAGATE_EXCEPTIONS  = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FORCE_COMPRESSION              = False
    JUST_LAUNCHED                  = True #Autoset to False after first page loads
