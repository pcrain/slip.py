#!/usr/bin/python
from flask import request, jsonify, current_app, send_from_directory, render_template
from sqlalchemy  import or_, and_

from werkzeug.utils import secure_filename
from app import db, executor
from app.models import User, Replay, ScanDir, Settings
from app.api import bp
from app.main.helpers import *

from PyQt5 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets


# from __main__ import app
from datetime import datetime
from pathlib import Path
import json, glob, ntpath, time, os, subprocess, copy, shutil, shlex
import concurrent.futures

NODUPES             = True  #Set to True to not allow duplicate reuploads
NOKEEP              = False #Set to True to delete files after uploading

#Dictionary of job timers
_scan_jobs = {

}

@bp.route('/upload', methods=['POST'])
def api_upload_replay():
    #Populate a return JSON
    jret = {
      "time"            : datetime.utcnow(),
      "status"          : "Success",
      "error"           : "",
      "url"             : "",
      "filename"        : "",
      "filename_secure" : "",
      "replay"          : None,
      "update"          : None,
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
    conf      = dict(current_app.config)
    checksums = set(i.checksum for i in Replay.query.all())
    return analyze_replay(opath,jret,nokeep=NOKEEP,conf=conf,checksums=checksums)

@bp.route('/open', methods=['POST'])
def api_open_containing_dir():
  d    = request.get_json()["dir"]
  f    = request.get_json()["name"]
  full = os.path.join(current_app.config['DATA_FOLDER'],d,f)
  real = os.path.realpath(full)
  openDir(real,isfile=True)
  return jsonify({"status" : "ok"})

@bp.route('/opendata', methods=['GET'])
def api_open_data_dir():
  openDir(current_app.config['DATA_FOLDER'])
  return jsonify({"status" : "ok"})

@bp.route('/openinstall', methods=['GET'])
def api_open_install_dir():
  openDir(current_app.config['INSTALL_FOLDER'])
  return jsonify({"status" : "ok"})

@bp.route('/setemupath', methods=['GET'])
def api_set_emu_path():
  Settings.load()
  fp = os.path.join(current_app.config["INSTALL_FOLDER"],"app","filepicker.py")
  print(fp)
  fn = shcall(f"""python {fp} "Select Slippi Dolphin Executable" """)
  if fn:
    Settings.query.filter_by(name="emupath").update({"value" : fn})
    db.session.commit()
  return jsonify({"status" : "ok"})

@bp.route('/setisopath', methods=['GET'])
def api_set_iso_path():
  Settings.load()
  fp = os.path.join(current_app.config["INSTALL_FOLDER"],"app","filepicker.py")
  fn = shcall(f"""python {fp} "Select Melee 1.02 ISO Path" """)
  if fn:
    Settings.query.filter_by(name="isopath").update({"value" : fn})
    db.session.commit()
  return jsonify({"status" : "ok"})

@bp.route('/purge', methods=['POST'])
def api_purge():
  # Replay.query.delete()
  if os.path.exists(current_app.config["DATA_FOLDER"]):
    shutil.rmtree(current_app.config["DATA_FOLDER"])
  return jsonify({"status" : "ok"})

@bp.route('/scan', methods=['POST'])
def api_scan_dir():
  global _scan_jobs
  token             = md5(str(datetime.utcnow()))[:8]
  _scan_jobs[token] = {
    "posted"   : datetime.utcnow(),
    "progress" : 0,
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
  d                           = _scan_jobs[token]["progress"]
  t                           = _scan_jobs[token]["total"]
  tmpfile                     = os.path.join(current_app.config['TMP_FOLDER'],token)
  if d is not None:
    return jsonify({"status" : f"{d}/{t}"})

  with open(os.path.join(current_app.config['TMP_FOLDER'],token),'r') as fin:
    logoutput = fin.read()

  details = dict({
    "details" : _scan_jobs[token]["details"],
    "log"     : logoutput,
    })
  del _scan_jobs[token]
  logline(tmpfile,f"Scan job deleted")
  now      = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
  scanfile = os.path.join(current_app.config['LOG_FOLDER'],f"scan-{now}.json.gz")
  compressedJsonWrite(details,scanfile)
  return jsonify({"status" : "Done!", "done" : True, "details": f"scan-{now}.json"})

@bp.route('/scanlog/<s>', methods=['GET'])
def api_get_scan_log(s):
  base = os.path.join(current_app.config['LOG_FOLDER'],s)
  with open(base,'w') as fout:
    json.dump(compressedJsonRead(base+".gz"), fout, indent=1, sort_keys=False)
  openJson(base)
  return jsonify({"status" : "ok"})

@bp.route('/raw/<r>', methods=['GET'])
def api_get_raw_analysis(r):
  openJson(
    os.path.join(
      current_app.config['REPLAY_FOLDER'],r+".slp.json"))
  return jsonify({"status" : "ok"})

@bp.route('/play/<c>',           methods=['GET']) #File
@bp.route('/play/<c>/<sf>',      methods=['GET']) #File, Start
@bp.route('/play/<c>/<sf>/<ef>', methods=['GET']) #File, Start, End
def api_play_replay(c,sf=-123,ef=999999):
  settings = Settings.load()
  isopath  = settings["isopath"]
  emupath  = settings["emupath"]
  r        = Replay.query.filter_by(checksum=c).first()
  p        = os.path.join(r.filedir,r.filename)
  jdata    = f"""{{"mode":"queue","queue":[{{"path":"{p}","startFrame":{sf},"endFrame":{ef}}}]}}"""
  tname    = "/tmp/slipjson.json"
  with open(tname,'w') as fout:
    fout.write(jdata)
  comm     = f"{emupath} -b -e {isopath} -i {tname}"
  subprocess.Popen(shlex.split(comm))
  return jsonify({"status" : "ok"})

def analyze_replay(local_file,jret,*,nokeep=False,conf={},checksums=set()):
    global _scan_jobs

    #If we've already analyzed a replay with the same md5, update its info and call it a day
    m       = md5file(local_file)
    # samemd5 = Replay.query.filter_by(checksum=m).all()
    # samemd5 = []
    if NODUPES and m in checksums:
      jret["update"] = {
        "filedir"  : jret.get("filedir","").replace(conf['DATA_FOLDER'],""),
        "filename" : jret["filename_secure"],
        "checksum" : m,
      }
      jret["status"] = 'Duplicate'
      jret["url"]    = '/replays/'+m
      jret["error"]  = 'Replay already in database'
      return jret

    #If an analysis of this file already exists, don't bother analyzing it
    afile = os.path.join(conf['REPLAY_FOLDER'], m+".slp.json")
    if not os.path.exists(afile):
      #Try to actually analyze the replay; if we can't, call it a day
      _,err = call([conf['ANALYZER'],"-i",local_file,"-a",afile],returnErrors=True)

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
        filedir   = jret.get("filedir","").replace(conf['DATA_FOLDER'],""),
        filesize  = os.stat(local_file).st_size,
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
        p1codetag = rdata["players"][0]["tag_code"],
        p1display = get_display_tag(rdata["players"][0]),
        p2char    = rdata["players"][1]["char_id"],
        p2color   = rdata["players"][1]["color"],
        p2stocks  = rdata["players"][1]["end_stocks"],
        p2metatag = rdata["players"][1]["tag_player"],
        p2csstag  = rdata["players"][1]["tag_css"],
        p2codetag = rdata["players"][1]["tag_code"],
        p2display = get_display_tag(rdata["players"][1]),
        stage     = rdata["stage_id"],
        )
    # _scan_jobs[jret["token"]]["adds"].append(replay)
    jret["url"] = '/replays/'+m
    jret["replay"] = replay
    return jret

def scan_single(i,r,token,conf,checksums):
  global _scan_jobs
  # progfile = os.path.join(current_app.config['TMP_FOLDER'],token+"-progress")
  # Path(progfile).touch()

  jret = {
    "token"           : token,
    "time"            : datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S'),
    "filedir"         : ntpath.dirname(r),
    "filename"        : ntpath.basename(r),
    "filename_secure" : ntpath.basename(r),
    "url"             : "",
    "status"          : "Success",
    "error"           : "",
    "replay"          : None,
    "update"          : None,
    }
  jret = analyze_replay(r,jret,nokeep=False,conf=conf,checksums=checksums)
  # rdata.append(rstat)
  del jret["time"]
  del jret["token"]
  del jret["filename_secure"]
  # _scan_jobs[token]["details"].append(jret)
  # print(f"Returning {i}")
  # print(f"Finishing {i}")
  return jret

def scan_job(token):
  global _scan_jobs

  tmpfile     = os.path.join(current_app.config['TMP_FOLDER'],token)
  allreplays  = []
  rdata       = []
  checked     = set()
  checksums   = set()
  namesizes   = set()

  logline(tmpfile,f"Fetching cached replay metadata",new=True)
  for i in Replay.query.all():
    checksums.add(i.checksum)
    namesizes.add((os.path.join(i.filedir,i.filename),i.filesize))

  logline(tmpfile,f"Locating .slp Replay files")
  for item in ScanDir.query.all():
    get_all_slippi_files(item.fullpath,allreplays,checked)
  _scan_jobs[token]["total"] = len(allreplays)
  logline(tmpfile,f"Found {len(allreplays)} total files")

  logline(tmpfile,f"Filtering unchanged .slp Replay files")
  replays = [r for r in allreplays if (r,os.stat(r).st_size) not in namesizes]
  logline(tmpfile,f"Found {len(replays)} changed files ({len(allreplays)-len(replays)} unchanged)")

  logline(tmpfile,f"Starting scan")
  conf      = dict(current_app.config)
  adds      = []
  updates   = []
  #TODO: might spawn multiple GUIs on Windows now that we're using init_gui
  with concurrent.futures.ProcessPoolExecutor(max_workers=current_app.config["MAX_SCAN_THREADS"]) as ex:
    tasks = {ex.submit(scan_single,i,r,token,conf,checksums) for i,r in enumerate(replays)}
    for i,t in enumerate(concurrent.futures.as_completed(tasks)):
      # if (datetime.utcnow() - _scan_jobs[token]["posted"]).seconds >= 2:
      #   pass
      res = t.result()
      if res is None:
        logline(tmpfile,f"Browser closed by user after {i}/{len(replays)} files")
        break
      if res["replay"] is not None:
        adds.append(res["replay"])
      if res["update"] is not None:
        updates.append(res["update"])
      del res["replay"]
      rdata.append(res)
      _scan_jobs[token]["progress"] += 1

  logline(tmpfile,f"Committing {len(adds)} new entries")
  db.session.add_all(adds)

  logline(tmpfile,f"Updating {len(updates)} entries: ")
  for u in updates:
    Replay.query.filter_by(checksum=u["checksum"]).update(u)

  db.session.commit()
  logline(tmpfile,f"Scan completed")

  _scan_jobs[token]["details"]  = rdata
  _scan_jobs[token]["progress"] = None
  return jsonify({"status" : "ok", "details" : rdata})
