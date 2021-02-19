#!/usr/bin/python
from flask import jsonify, render_template, current_app as ca
from app import db
from app.helpers import htmlEscape, openJson
from app.errors import bp
import os, traceback

#Route for 404 (not found) page
@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html.j2'), 404

#Route for 418 (teapot) page (used for loading replay stats with missing analysis JSONS)
@bp.app_errorhandler(418)
def teapot_error(error):
    return render_template('418.html.j2'), 404

#Route for 500 (internal server error) page
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html.j2',
      error=error,trace=traceback.format_exc()), 500

#Route for opening in-app error logs
@bp.route('/errorlog', methods=['GET'])
def error_log():
  #Get log file dir name
  ldir = ca.config['LOG_FOLDER']
  #Get log file base name
  base = ca.config['LOG_FILE']
  #List all log files in directory
  logs = [os.path.join(ldir,f) for f in os.listdir(ldir) if base in f]
  #Sort logs by modification time
  logs = sorted(logs,key=lambda f: os.stat(f).st_mtime, reverse=True)
  #Get output of each log file
  errors  = []
  for f in logs:
    with open(f,'r') as fin:
      errors.append([os.path.basename(f),htmlEscape(fin.read())])
  #Render all logs
  return render_template('errorlog.html.j2',errors=errors)

#Route for opening error logs in a text editor
@bp.route('/errorlog/<e>', methods=['GET'])
def open_error_log(e):
  openJson(os.path.join(ca.config['LOG_FOLDER'],e))
  return jsonify({"status" : "ok"})
