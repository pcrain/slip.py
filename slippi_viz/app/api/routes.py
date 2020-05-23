#!/usr/bin/python
from flask import request, jsonify, current_app, send_from_directory, render_template
from sqlalchemy  import or_, and_

from werkzeug.utils import secure_filename
from app import db, executor
# from app import db, limiter, executor
from app.models import User, Replay, ScanDir
from app.api import bp
from app.main.helpers import *

# from __main__ import app
from datetime import datetime
import json, glob, ntpath, time, os, subprocess

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
      "url"             : "",
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

@bp.route('/open', methods=['POST'])
def api_open_containing_dir():
  d    = request.get_json()["dir"]
  if d[0] == "/":
    d = d[1:]  #Eliminate leading slash from database
  elif d[0] == "\\":
    d = d[1:]  #Eliminate leading double backslash from database
  f    = request.get_json()["name"]
  full = os.path.join(current_app.config['DATA_FOLDER'],d,f)
  real = os.path.realpath(full)

  if os.name == 'nt':
    explorer = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    subprocess.run([explorer, '/select,', real])
  else:
    #Query default file explorer
    exp_query   = ["xdg-mime","query","default","inode/directory"]
    p           = subprocess.Popen(exp_query, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate("")
    explorer    = output.decode('utf-8').replace(".desktop\n","")

    #Can't highlight file in every Linux explorer, so settle for opening the directory
    subprocess.run([explorer, ntpath.dirname(real)])
  return jsonify({"status" : "ok"})

@bp.route('/scan', methods=['POST'])
def api_scan_dir():
  global _scan_jobs
  token             = md5(str(datetime.utcnow()))[:8]
  _scan_jobs[token] = {
    "posted"   : datetime.utcnow(),
    "progress" : -1,
    "total"    : 0,
    "adds"     : [],
    "details"  : [],
    }
  executor.submit(scan_job,token)
  return jsonify({"status" : "Scan Started", "token" : token})

@bp.route('/scan/add', methods=['POST'])
def api_scan_add():
  d = request.get_json()["dir"]

  scandir = ScanDir(
    fullpath = d,
    display  = ntpath.basename(d),
    path     = ntpath.dirname(d),
    lastscan = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S'),
    )

  db.session.add(scandir)
  db.session.commit()

  return jsonify({"status" : "ok"})

@bp.route('/scan/del', methods=['POST'])
def api_scan_del():
  d = request.get_json()["dir"]

  sd = ScanDir.query.filter(
    ScanDir.fullpath == d,
    ).first()
  db.session.delete(sd)
  db.session.commit()

  return jsonify({"status" : "ok"})

@bp.route('/scan/browse', methods=['POST'])
def api_scan_browse():
  curscans = set()
  # for f in os.listdir(current_app.config['SCAN_FOLDER']):
  #   curscans.add(os.readlink(os.path.join(current_app.config['SCAN_FOLDER'],f)))
  for item in ScanDir.query.all():
    curscans.add(os.path.realpath(item.fullpath))
  d       = request.get_json().get("dir",os.path.expanduser("~"))
  if d == "":
    d = os.path.expanduser("~")
  s       = request.get_json().get("subdir","")
  p       = d if s == "" else os.path.join(d,s)
  listing = check_for_slippi_files(p,nav=(p!="/"))
  listing = sorted(listing, key = lambda i: (i["sort"],i['name']))
  for item in listing:
    if item["class"] == "curdir":
      item["click"] = "addScanDir"
    else:
      item["click"] = "browseDir"
    if item["path"] in curscans:
      item["class"] += " scanned"
      item["click"] = "scanExists"
  j = {
    "status" : "ok",
    "back"   : os.path.dirname(p),
    "parent" : p,
    "subs"   : listing,
    "render" : render_template("_folder_list.html.j2",dirs=listing)
    }
  # print(j["render"])
  return jsonify(j)

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
  details = dict({"details" : _scan_jobs[token]["details"]})
  del _scan_jobs[token]
  logline(tmpfile,f"Scan job deleted")
  now = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
  scanfile = os.path.join(current_app.config['LOG_FOLDER'],f"scan-{now}.json.gz")
  compressedJsonWrite(details,scanfile)
  return jsonify({"status" : "Done!", "done" : True, "details": f"scan-{now}.json"})

@bp.route('/scanlog/<s>', methods=['GET'])
def api_get_scan_log(s):
  base = os.path.join(current_app.config['LOG_FOLDER'],s)
  with open(base,'w') as fout:
    json.dump(compressedJsonRead(base+".gz"), fout, indent=1, sort_keys=False)
  return send_from_directory(current_app.config['LOG_FOLDER'],s)

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
      jret["url"]          = '/replays/'+m
      jret["error"]        = 'Replay already in database'
      return jret

    #If an analysis of this file already exists, don't bother analyzing it and call it a day
    afile            = os.path.join(current_app.config['REPLAY_FOLDER'], m+".slp.json")
    if NODUPES and os.path.exists(afile):
      jret["status"]       = 'Duplicate'
      jret["url"]          = '/replays/'+m
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
        frames    = rdata["game_length"],
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
    jret["url"] = '/replays/'+m
    return jret

def scan_job(token):
  global _scan_jobs

  tmpdir  = current_app.config['TMP_FOLDER']
  tmpfile = os.path.join(tmpdir,token)
  lbase   = current_app.config['SCAN_FOLDER']
  replays = []
  rdata   = []
  checked = set()

  os.makedirs(tmpdir,exist_ok=True)
  logline(tmpfile,f"Starting scan",new=True)

  for item in ScanDir.query.all():
    get_all_slippi_files(item.fullpath,replays,checked)
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
      "time"            : datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S'),
      "filedir"         : ntpath.dirname(r),
      "filename"        : ntpath.basename(r),
      "filename_secure" : ntpath.basename(r),
      "url"             : "",
      "status"          : "Success",
      "error"           : "",
      }
    rstat = analyze_replay(r,jret,nokeep=False)
    rdata.append(rstat)
    del jret["time"]
    del jret["token"]
    del jret["filename_secure"]
    _scan_jobs[token]["details"].append(jret)
  logline(tmpfile,"Committing {} new entries".format(len(_scan_jobs[token]["adds"])))
  db.session.add_all(_scan_jobs[token]["adds"])
  db.session.commit()
  logline(tmpfile,f"Scan completed")
  return jsonify({"status" : "ok", "details" : rdata})
