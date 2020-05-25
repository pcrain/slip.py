#!/usr/bin/python
from flask import render_template, flash, redirect, url_for, request, current_app, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.main import bp
from app.main.forms import ReplaySearchForm
from app.main.helpers import *
from app.models import User, Replay, ScanDir

from datetime import datetime
import os

@bp.before_request
def before_request():
    if not os.path.exists(current_app.config["DATA_FOLDER"]):
      return render_template("nodata.html.j2", title="No Data")
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(
      current_app.config["STATIC_FOLDER"],"icons"
      ), 'pretzel.png', mimetype='image/vnd.microsoft.icon')

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

    ddata = []
    if ddir == "":
        for item in ScanDir.query.all():
            ddata.append(check_single_folder_for_slippi_files(item.path,item.display,indb=True))
    else:
        ddata = check_for_slippi_files(ddir)

    #Copy GET args and set next / previous page
    qdict             = dict(request.args)
    qdict["nextpage"] = rdata.next_num
    qdict["prevpage"] = rdata.prev_num
    if "page" in qdict:
      del qdict["page"]
    next_url = url_for('main.replays', page=qdict["nextpage"], **qdict) if rdata.has_next else None
    prev_url = url_for('main.replays', page=qdict["prevpage"], **qdict) if rdata.has_prev else None
    return render_template("index.html.j2", title="Public Replays", form=ReplaySearchForm(), replays=rdata.items, dirs=ddata, next_url=next_url, prev_url=prev_url)

@bp.route('/replays/<r>')
def replay_viz(r):
    rdata  = Replay.query.filter_by(checksum=r).first()
    rpath  = os.path.join(current_app.config['REPLAY_FOLDER'], r+".slp.json")
    replay = load_replay(rpath)
    replay["__original_filename"] = rdata.filename
    replay["__filedir"]           = rdata.filedir
    replay["__checksum"]          = r
    return render_template("replay.html.j2", title=rdata.filename, rsummary=rdata, replay=replay)

@bp.route('/upload', methods=['GET'])
def upload_page():
  return render_template("upload.html.j2", title="Upload Replays")

@bp.route('/settings', methods=['GET'])
def settings_page():
  return render_template("settings.html.j2", title="Settings")

@bp.route('/scan', methods=['GET'])
def scan_page():
  ldirs = []

  for item in ScanDir.query.all():
    lbase = item.path
    f     = item.display
    full  = item.fullpath
    if not os.path.exists(full): #Broken symlink
      ldirs.append({
        "name"  : f,
        "stats" : {
            "name"  : f,
            "path"  : os.path.join(lbase,f),
            "dirs"  : 0,
            "files" : 0,
            "class" : "broken",
            "click" : "delScanDir",
            "sort"  : 4,
          },
        })
    elif os.path.isdir(full):
        ldirs.append({
            "name"  : f,
            "stats" : check_single_folder_for_slippi_files(lbase,f,click="delScanDir",classd="scanned")
            })
  return render_template("scan.html.j2", title="Scan Replays", scandirs=ldirs)
