#!/usr/bin/python
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.main import bp
from app.main.forms import ReplaySearchForm
from app.main.helpers import *
from app.models import User, Replay

from datetime import datetime
import os

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/')
@bp.route('/replays')
def replays():
    q        = request.args.get("query",None)
    ddir     = request.args.get("path","")
    rdir     = current_app.config['REPLAY_FOLDER']
    page     = request.args.get('page', 1, type=int)
    if (q is None) and (ddir == ""):
        rdata = current_user.all_replays().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    else:
        rdata = Replay.search(request.args).paginate(page, current_app.config['POSTS_PER_PAGE'], False)

    dfull = os.path.join(current_app.config['SCAN_FOLDER'],ddir)
    ddata = []
    for d in os.listdir(dfull):
        p = os.path.join(dfull,d)
        if os.path.isdir(p):
            ndirs  = 0
            nfiles = 0
            for s in os.listdir(p):
                f = os.path.join(p,s)
                if os.path.isdir(f):
                    ndirs += 1
                elif f[-4:] == ".slp":
                    nfiles += 1
            ddata.append({
                "name"  : d,
                "path"  : os.path.join(ddir,d),
                "dirs"  : ndirs,
                "files" : nfiles,
                })

    # ddata = [{"name" : "dir1"},{"name" : "dir2"},{"name" : "dir3"},{"name" : "dir4"},{"name" : "dir5"},{"name" : "dir6"},{"name" : "dir7"}]

    #Copy GET args and set next / previous page
    qdict             = dict(request.args)
    qdict["nextpage"] = rdata.next_num
    qdict["prevpage"] = rdata.prev_num
    if "page" in qdict:
      del qdict["page"]
    next_url = url_for('main.replays', page=qdict["nextpage"], **qdict) if rdata.has_next else None
    prev_url = url_for('main.replays', page=qdict["prevpage"], **qdict) if rdata.has_prev else None
    return render_template("index.html.j2", title="Public Replays", form=ReplaySearchForm(), replays=rdata.items, dirs=ddata, next_url=next_url, prev_url=prev_url)

# @bp.route('/', defaults={'path': ''})
# @bp.route('/<path:path>')
# def get_dir(path):
#     return path

@bp.route('/replays/<r>')
def replay_viz(r):
    rdata  = Replay.query.filter_by(checksum=r).first()
    rpath  = os.path.join(current_app.config['REPLAY_FOLDER'], r+".slp.json")
    replay = load_replay(rpath)
    replay["__original_filename"] = rdata.filename
    return render_template("replay.html.j2", rsummary=rdata, replay=replay)

@bp.route('/upload', methods=['GET'])
def upload_page():
  return render_template("upload.html.j2")

@bp.route('/scan', methods=['GET'])
def scan_page():
  lbase = current_app.config['SCAN_FOLDER']
  ldirs = [f for f in os.listdir(lbase) if os.path.isdir(os.path.join(lbase, f))]
  return render_template("scan.html.j2", scandirs=ldirs)
