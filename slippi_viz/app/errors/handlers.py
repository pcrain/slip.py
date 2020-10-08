#!/usr/bin/python
from flask import render_template
from app import db
from app.errors import bp
import traceback

@bp.app_errorhandler(404)
def not_found_error(error):
    return render_template('404.html.j2'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html.j2',
      error=error,trace=traceback.format_exc()), 500
