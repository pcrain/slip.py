#!/usr/bin/python
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from flask_limiter import Limiter
# from flask_limiter.util import get_remote_address
from flask_executor import Executor
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os

db               = SQLAlchemy()
login            = LoginManager()
# limiter          = Limiter(key_func=get_remote_address)
executor         = Executor()
login.login_view = 'auth.login'

def init_environment(app):
  os.makedirs(app.config["DATA_FOLDER"],exist_ok=True)
  os.makedirs(app.config["UPLOAD_FOLDER"],exist_ok=True)
  os.makedirs(app.config["REPLAY_FOLDER"],exist_ok=True)
  os.makedirs(app.config["LOG_FOLDER"],exist_ok=True)
  os.makedirs(app.config["TMP_FOLDER"],exist_ok=True)

def create_app(config_class=Config):
    print("Creating Flask App")
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    # limiter.init_app(app)
    executor.init_app(app)

    init_environment(app)

    from app.errors import bp as errors_bp
    from app.auth   import bp as auth_bp
    from app.api    import bp as api_bp
    from app.main   import bp as main_bp

    with app.app_context():
        db.create_all()

    # limiter.exempt(errors_bp)
    # limiter.exempt(auth_bp)
    # limiter.exempt(main_bp)

    app.register_blueprint(errors_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(main_bp)

    if not os.path.exists(app.config['LOG_FOLDER']):
        os.mkdir(app.config['LOG_FOLDER'])
    file_handler = RotatingFileHandler(
        os.path.join(app.config['LOG_FOLDER'],'slippi_viz.log'),
        maxBytes=10240, backupCount=10
        )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s '
        '[in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Slippi Viz startup')

    print("Flask App Created")
    return app

from app import models
