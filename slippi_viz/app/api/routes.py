#!/usr/bin/python
from flask import request, jsonify, current_app, send_from_directory

from werkzeug.utils import secure_filename
from app import db, executor
# from app import db, limiter, executor
from app.models import User, Replay
from app.api import bp
from app.main.helpers import *

# from __main__ import app
from datetime import datetime
import json, glob, ntpath, time, os

REPLAY_UPLOAD_LIMIT = "600 per hour"
NODUPES             = True  #Set to True to not allow duplicate reuploads
NOKEEP              = False #Set to True to delete files after uploading

#Dictionary of job timers
_scan_jobs = {

}

@bp.route('/upload', methods=['POST'])
# @limiter.limit(REPLAY_UPLOAD_LIMIT)
def api_upload_replay():
    #Populate a return JSON
    jret = {
      "time"            : datetime.utcnow(),
      "status"          : "Success",
      "error"           : "",
      "analysis-url"    : "",
      "filename"        : "",
      "filename_secure" : "",
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
        jret["error"]  = 'No selected file'
        return jsonify(jret)

    jret["filename"]        = file.filename
    jret["filename_secure"] = secure_filename(file.filename)
    opath                   = os.path.join(current_app.config['UPLOAD_FOLDER'], jret["filename_secure"])
    file.save(opath)
    return analyze_replay(opath,jret,nokeep=NOKEEP)

@bp.route('/scan', methods=['POST'])
def api_scan_dir():
  global _scan_jobs
  token             = md5(str(datetime.utcnow()))[:8]
  _scan_jobs[token] = {
    "posted"   : datetime.utcnow(),
    "progress" : -1,
    "total"    : 0,
    "adds"     : [],
    }
  executor.submit(scan_job,token)
  return jsonify({"status" : "Scan Started", "token" : token})

@bp.route('/scan/progress', methods=['POST'])
def api_scan_progress():
  token                       = request.get_json()["token"]
  _scan_jobs[token]["posted"] = datetime.utcnow() #Update our posted time
  d                           = _scan_jobs[token]["progress"]+1
  t                           = _scan_jobs[token]["total"]
  tmpfile                     = os.path.join(current_app.config['TMP_FOLDER'],token)
  if d < t:
    return jsonify({"status" : f"{d}/{t}"})
  # db.session.flush()
  # db.session.commit()
  # db.session.close()
  del _scan_jobs[token]
  logline(tmpfile,f"Scan job deleted")
  return jsonify({"status" : "Done!", "done" : True})

@bp.route('/raw/<r>', methods=['GET'])
def api_get_raw_analysis(r):
    return send_from_directory(current_app.config['REPLAY_FOLDER'],r+".slp.json")
    # rpath  = os.path.join(current_app.config['REPLAY_FOLDER'], r+".slp.json")
    # replay = load_replay(rpath)
    # rdata  = Replay.query.filter_by(checksum=r).first()
    # replay["__original_filename"] = rdata.filename
    # return jsonify(replay)

def analyze_replay(local_file,jret,nokeep=False):
    global _scan_jobs

    #If we've already analyzed a replay with the same md5, update its info and call it a day
    m       = md5file(local_file)
    samemd5 = Replay.query.filter_by(checksum=m).all()
    if NODUPES and len(samemd5) > 0:

      for r in samemd5:
        r.filedir  = jret.get("filedir","").replace(current_app.config['DATA_FOLDER'],"")
        r.filename = jret["filename_secure"]
        # db.session.flush()
        db.session.commit()

      jret["status"]       = 'Duplicate'
      jret["analysis-url"] = '/replays/'+m
      jret["error"]        = 'Replay already in database'
      return jret

    #If an analysis of this file already exists, don't bother analyzing it and call it a day
    afile            = os.path.join(current_app.config['REPLAY_FOLDER'], m+".slp.json")
    if NODUPES and os.path.exists(afile):
      jret["status"]       = 'Duplicate'
      jret["analysis-url"] = '/replays/'+m
      jret["error"]        = 'Replay already in database'
      if nokeep:
        os.remove(local_file)
      return jret

    #Try to actually analyze the replay; if we can't, call it a day
    _,err            = call([current_app.config['ANALYZER'],"-i",local_file,"-a",afile],returnErrors=True)
    if nokeep:
      os.remove(local_file)
    if not os.path.exists(afile):
      jret["status"] = 'Failure'
      jret["error"]  = 'Failed to parse replay; got the following error: <br/><code>'+err+'</code>'
      return jret


    #Add the replay to the database
    rdata  = load_replay(afile)
    replay = Replay(
        checksum  = m,
        filename  = jret["filename_secure"],
        filedir   = jret.get("filedir","").replace(current_app.config['DATA_FOLDER'],""),
        user_id   = -1,
        is_public = True,
        uploaded  = jret["time"],
        played    = try_parse_time(rdata["game_time"][:19]),
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
    _scan_jobs[jret["token"]]["adds"].append(replay)
    jret["analysis-url"] = '/replays/'+m
    return jret

def scan_job(token):
  global _scan_jobs

  tmpdir  = current_app.config['TMP_FOLDER']
  tmpfile = os.path.join(tmpdir,token)
  os.makedirs(tmpdir,exist_ok=True)
  logline(tmpfile,f"Starting scan",new=True)

  lbase   = current_app.config['SCAN_FOLDER']
  replays = []
  get_all_slippi_files(lbase,replays)
  rdata   = []
  _scan_jobs[token]["total"] = len(replays)
  logline(tmpfile,f"Found {len(replays)} total files")
  for i,r in enumerate(replays):
    #If we haven't received a progress update request in the last 2 seconds, cancel the job
    if (datetime.utcnow() - _scan_jobs[token]["posted"]).seconds >= 2:
      logline(tmpfile,f"Browser closed by user after {i}/{len(replays)} files")
      break
    _scan_jobs[token]["progress"] = i
    jret = {
      "token"           : token,
      "time"            : datetime.utcnow(),
      "status"          : "Success",
      "error"           : "",
      "analysis-url"    : "",
      "filedir"         : ntpath.dirname(r),
      "filename"        : ntpath.basename(r),
      "filename_secure" : ntpath.basename(r),
      }
    rstat = analyze_replay(r,jret,nokeep=False)
    rdata.append(rstat)
  logline(tmpfile,"Committing {} new entries".format(len(_scan_jobs[token]["adds"])))
  db.session.add_all(_scan_jobs[token]["adds"])
  db.session.commit()
  logline(tmpfile,f"Scan completed")
  return jsonify({"status" : "ok", "details" : rdata})