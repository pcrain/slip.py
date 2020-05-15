#!/usr/bin/python
from flask import request, jsonify, current_app, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from app import db, limiter
from app.models import User, Replay
from app.api import bp
from app.main.helpers import *

from datetime import datetime
import json

REPLAY_UPLOAD_LIMIT = "600 per hour"
NODUPES = True  #Set to True to not allow duplicate reuploads
NOKEEP  = False #Set to True to delete files after uploading

def analyze_replay(local_file,jret):
    m                = md5file(local_file)
    afile            = os.path.join(current_app.config['REPLAY_FOLDER'], m+".slp.json")
    if NODUPES and os.path.exists(afile):
      jret["status"]       = 'Duplicate'
      jret["analysis-url"] = '/replays/'+m
      jret["error"]        = 'Replay already in database'
      if NOKEEP:
        os.remove(local_file)
      return jsonify(jret)

    _,err            = call([current_app.config['ANALYZER'],"-i",local_file,"-a",afile],returnErrors=True)
    if NOKEEP:
      os.remove(local_file)
    if not os.path.exists(afile):
      jret["status"] = 'Failure'
      jret["error"] = 'Failed to parse replay; got the following error: <br/><code>'+err+'</code>'
      return jsonify(jret)

    #Should never get here theoretically, should fail at the afile check above
    if NODUPES and len(Replay.query.filter_by(checksum=m).all()) > 0:
      jret["status"]       = 'Duplicate'
      jret["analysis-url"] = '/replays/'+m
      jret["error"]        = 'Replay already in database'
      return jsonify(jret)

    rdata  = load_replay(afile)
    replay = Replay(
        checksum  = m,
        filename  = jret["filename_secure"],
        user_id   = -1,
        is_public = True,
        uploaded  = jret["time"],
        played    = datetime.strptime(rdata["game_time"][:19], "%Y-%m-%dT%H:%M:%S"),
        p1char    = rdata["players"][0]["char_id"],
        p1color   = rdata["players"][0]["color"],
        p1stocks  = rdata["players"][0]["end_stocks"],
        p1metatag = rdata["players"][0]["tag_player"],
        p1csstag  = rdata["players"][0]["tag_css"],
        p1display = get_display_tag(rdata["players"][0]),
        p2char    = rdata["players"][1]["char_id"],
        p2color   = rdata["players"][1]["color"],
        p2stocks  = rdata["players"][1]["end_stocks"],
        p2metatag = rdata["players"][1]["tag_player"],
        p2csstag  = rdata["players"][1]["tag_css"],
        p2display = get_display_tag(rdata["players"][1]),
        stage     = rdata["stage_id"],
        )
    db.session.add(replay)
    db.session.commit()
    jret["analysis-url"] = '/replays/'+m
    return jsonify(jret)

@bp.route('/upload', methods=['POST'])
@limiter.limit(REPLAY_UPLOAD_LIMIT)
def api_upload_replay():
    requestdate = datetime.utcnow();
    #Populate a return JSON
    jret = {
      "time"         : requestdate,
      "status"       : "Success",
      "error"        : "",
      "analysis-url" : "",
      "filename"     : "",
      }

    # Error if no file attribute
    if 'file' not in request.files:
        jret["status"] = 'Failure'
        jret["error"]  = 'No file part'
        return jsonify(jret)

    # Check if file is actually submitted
    file = request.files['file']
    if file.filename == '' or not file:
        jret["status"] = 'Failure'
        jret["error"] = 'No selected file'
        return jsonify(jret)

    jret["filename"]        = file.filename
    jret["filename_secure"] = secure_filename(file.filename)
    opath                   = os.path.join(current_app.config['UPLOAD_FOLDER'], jret["filename_secure"])
    file.save(opath)
    return analyze_replay(opath,jret)
    # m                = md5file(opath)
    # afile            = os.path.join(current_app.config['REPLAY_FOLDER'], m+".slp.json")
    # if NODUPES and os.path.exists(afile):
    #   jret["status"]       = 'Duplicate'
    #   jret["analysis-url"] = '/replays/'+m
    #   jret["error"]        = 'Replay already in database'
    #   if NOKEEP:
    #     os.remove(opath)
    #   return jsonify(jret)

    # _,err            = call([current_app.config['ANALYZER'],"-i",opath,"-a",afile],returnErrors=True)
    # if NOKEEP:
    #   os.remove(opath)
    # if not os.path.exists(afile):
    #   jret["status"] = 'Failure'
    #   jret["error"] = 'Failed to parse replay; got the following error: <br/><code>'+err+'</code>'
    #   return jsonify(jret)

    # #Should never get here theoretically, should fail at the afile check above
    # if NODUPES and len(Replay.query.filter_by(checksum=m).all()) > 0:
    #   jret["status"]       = 'Duplicate'
    #   jret["analysis-url"] = '/replays/'+m
    #   jret["error"]        = 'Replay already in database'
    #   return jsonify(jret)

    # rdata  = load_replay(afile)
    # replay = Replay(
    #     checksum  = m,
    #     filename  = filename,
    #     user_id   = -1,
    #     is_public = True,
    #     uploaded  = requestdate,
    #     played    = datetime.strptime(rdata["game_time"][:19], "%Y-%m-%dT%H:%M:%S"),
    #     p1char    = rdata["players"][0]["char_id"],
    #     p1color   = rdata["players"][0]["color"],
    #     p1stocks  = rdata["players"][0]["end_stocks"],
    #     p1metatag = rdata["players"][0]["tag_player"],
    #     p1csstag  = rdata["players"][0]["tag_css"],
    #     p1display = get_display_tag(rdata["players"][0]),
    #     p2char    = rdata["players"][1]["char_id"],
    #     p2color   = rdata["players"][1]["color"],
    #     p2stocks  = rdata["players"][1]["end_stocks"],
    #     p2metatag = rdata["players"][1]["tag_player"],
    #     p2csstag  = rdata["players"][1]["tag_css"],
    #     p2display = get_display_tag(rdata["players"][1]),
    #     stage     = rdata["stage_id"],
    #     )
    # db.session.add(replay)
    # db.session.commit()
    # jret["analysis-url"] = '/replays/'+m
    # return jsonify(jret)

@bp.route('/raw/<r>', methods=['GET'])
def api_get_raw_analysis(r):
    rpath  = os.path.join(current_app.config['STATIC_FOLDER'], "data/replays", r+".slp.json")
    return send_from_directory(os.path.join(current_app.config['STATIC_FOLDER'], "data/replays"),r+".slp.json")
    # replay = load_replay(rpath)
    # rdata  = Replay.query.filter_by(checksum=r).first()
    # replay["__original_filename"] = rdata.filename
    # return jsonify(replay)
