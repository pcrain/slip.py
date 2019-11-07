#!/usr/bin/python

import os
basedir = os.path.abspath(os.path.dirname(__file__))
# basedir = app.root_path

class Config(object):
    #Global template variables
    SITE_NAME                      = "Slippi Replay Analysis"

    #Other config options
    SQLALCHEMY_DATABASE_URI        = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SECRET_KEY                     = os.environ.get('SECRET_KEY') or 'i-like-pretzels'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER                    = os.environ.get('MAIL_SERVER')
    MAIL_PORT                      = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS                   = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME                  = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD                  = os.environ.get('MAIL_PASSWORD')
    ADMINS                         = ['patrickacrain@gmail.com']
    POSTS_PER_PAGE                 = 10
    STATIC_FOLDER                  = "{}/app/static/".format(basedir)

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

    # print(basedir)
