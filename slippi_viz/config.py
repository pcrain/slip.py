#!/usr/bin/python
import os
basedir = os.path.abspath(os.path.dirname(__file__))
# basedir = app.root_path

class Config(object):
    #Global template variables
    SITE_NAME                      = "Slippi Replay Analysis"

    #Other config options
    SECRET_KEY                     = os.environ.get('SECRET_KEY') or 'i-like-pretzels'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER                    = os.environ.get('MAIL_SERVER')
    MAIL_PORT                      = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS                   = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME                  = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD                  = os.environ.get('MAIL_PASSWORD')
    ADMINS                         = ['patrickacrain@gmail.com']
    POSTS_PER_PAGE                 = 60
    SIMULTANEOUS_UPLOADS           = 100
    FORCE_COMPRESSION              = False
    STATIC_FOLDER                  = os.path.join(basedir,"app","static")
    DATA_FOLDER                    = os.path.join(os.path.expanduser("~"),".local","share","slippi_viz")
    UPLOAD_FOLDER                  = os.path.join(DATA_FOLDER,"uploads")
    REPLAY_FOLDER                  = os.path.join(DATA_FOLDER,"replays")
    SCAN_FOLDER                    = os.path.join(DATA_FOLDER,"local")
    TMP_FOLDER                     = os.path.join(DATA_FOLDER,"_tmp")
    SQLALCHEMY_DATABASE_URI        = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(DATA_FOLDER, 'app.db')
    ANALYZER                       = "/home/pretzel/workspace/slippc/slippc"

    INTERACTIONS = [
      "EDGEGUARDING",
      "TECHCHASING",
      "PUNISHING",
      "SHARKING",
      "PRESSURING",
      # "OFFENSIVE",
      "FOOTSIES",
      "POSITIONING",
      # "NEUTRAL",
      "POKING",
      # "TRADING",
      # "DEFENSIVE",
      "PRESSURED",
      "GROUNDING",
      "PUNISHED",
      "ESCAPING",
      "RECOVERING",
      ]

    CHARS = {
      "_NONE"   : -1,
      "BOWSER"  :  5,
      "CLIMBER" :  14,
      "DOCTOR"  :  22,
      "FALCO"   :  20,
      "FALCON"  :  0,
      "FOX"     :  2,
      "GANON"   :  25,
      "JIGGLY"  :  15,
      "KIRBY"   :  4,
      "KONG"    :  1,
      "LINK"    :  6,
      "LUIGI"   :  7,
      "MARIO"   :  8,
      "MARTH"   :  9,
      "MEWTWO"  :  10,
      "NESS"    :  11,
      "PEACH"   :  12,
      "PICHU"   :  24,
      "PIKACHU" :  13,
      "ROY"     :  23,
      "SAMUS"   :  16,
      "SHEIK"   :  19,
      "WATCH"   :  3,
      "YOSHI"   :  17,
      "YOUNG"   :  21,
      "ZELDA"   :  18,
      }

    # print(basedir)
