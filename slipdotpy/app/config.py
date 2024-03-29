#!/usr/bin/python
import sys, os, multiprocessing

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    #User config variables
    POSTS_PER_PAGE                 = 60
    SIMULTANEOUS_UPLOADS           = 100
    MAX_SCAN_THREADS               = multiprocessing.cpu_count()
    DEF_STATS                      = "?submit=&ndays=28" #Default stats page query
    UNIVERSAL_TOOLTIPS             = True #Whether we use fancy tooltips on all pages (slows things down too much on replay index)

    #Global template variables
    SITE_VERSION                   = "0.7.0"
    SITE_INTNAME                   = "slipdotpy"
    SITE_NAME                      = "Slip.py Browser"
    SITE_PORT                      = 5050
    SITE_ICON                      = os.path.join(basedir,"static","icons","wolfhead.png")

    #Data location variables
    INSTALL_FOLDER                 = os.path.dirname(basedir)
    STATIC_FOLDER                  = os.path.join(basedir,"static")
    if os.name == 'nt':
      DEF_REPLAY_FOLDER            = os.path.join(os.path.expanduser("~"),"Documents","Slippi")
      DATA_FOLDER                  = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'),SITE_INTNAME)
      ANALYZER                     = os.path.join("slippc","slippc.exe")
    else:
      DEF_REPLAY_FOLDER            = os.path.join(os.path.expanduser("~"),"Slippi")
      DATA_FOLDER                  = os.path.join(os.path.expanduser("~"),".local","share",SITE_INTNAME)
      ANALYZER                     = "slippc"
    UPLOAD_FOLDER                  = os.path.join(DATA_FOLDER,"uploads")
    ANALYSIS_FOLDER                = os.path.join(DATA_FOLDER,"replays")
    QUAR_FOLDER                    = os.path.join(DATA_FOLDER,"quarantine")
    LOG_FOLDER                     = os.path.join(DATA_FOLDER,"logs")
    LOG_FILE                       = SITE_INTNAME+'.log'
    TMP_FOLDER                     = os.path.join(DATA_FOLDER,"_tmp")
    SQLALCHEMY_DATABASE_URI        = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(DATA_FOLDER, 'app.db')

    #Other config variables
    SECRET_KEY                     = os.urandom(32)
    EXECUTOR_PROPAGATE_EXCEPTIONS  = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FORCE_COMPRESSION              = False

    #Modified during run time
    JUST_LAUNCHED                  = True  #Autoset to False after first page loads
    SCAN_IN_PROGRESS               = False #Autoset as needed when scans are initiated
    SCAN_REQUEST_STOPPED           = False #Whether we've requested to stop an in progress scan
    SEARCH_CACHE_VALID             = True  #Whether our current search cache is valid
    BG_MESSAGES                    = []    #List of messages regarding background tasks
    REPLAY_NAV                     = {}    #Dictionary for tracking previous / next replay based on last search
    REPLAY_NAV_QUERY               = None  #Query that we're tracking for the REPLAY_NAV above
    LAST_SEARCH                    = ""    #GET parameters for the last search we ran
