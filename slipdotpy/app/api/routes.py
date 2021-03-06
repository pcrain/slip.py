#!/usr/bin/python

#Flask imports
from flask import request, jsonify, current_app, send_from_directory, render_template
from sqlalchemy import or_, and_
from werkzeug.utils import secure_filename

#App imports
from app import db, executor
from app.helpers import *
from app.models import User, Replay, ScanDir, Settings
from app.api import bp

#Standard imports
from datetime import datetime
import json, glob, ntpath, time, os, subprocess, copy, shutil, shlex, traceback
import concurrent.futures

NODUPES             = True  #Set to True to not allow duplicate reuploads
NOKEEP              = False #Set to True to delete files after uploading
_scan_jobs          = {}    #Dictionary of job timers

#API call for getting messages about ongoing / completed background tasks
@bp.route('/getmessages', methods=['POST'])
def api_get_messages():
  messages = jsonify({"messages":current_app.config["BG_MESSAGES"]})
  current_app.config["BG_MESSAGES"] = []
  return messages

#[Deprecated] API call for uploading a replay to the server
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

#API call for opening the containing directory for a replay file
@bp.route('/open', methods=['POST'])
def api_open_replay_dir():
  d    = request.get_json()["dir"]
  f    = request.get_json()["name"]
  full = os.path.join(current_app.config['DATA_FOLDER'],d,f)
  real = os.path.realpath(full)
  openDir(real,isfile=True)
  return jsonify({"status" : "ok"})

#API call for opening the user data directory for slip.py
@bp.route('/opendata', methods=['GET'])
def api_open_data_dir():
  openDir(current_app.config['DATA_FOLDER'])
  return jsonify({"status" : "ok"})

#API call for opening the install directory for slip.py
@bp.route('/openinstall', methods=['GET'])
def api_open_install_dir():
  openDir(current_app.config['INSTALL_FOLDER'])
  return jsonify({"status" : "ok"})

#API call for setting the Slippi Playback Dolphin build path
@bp.route('/setemupath', methods=['GET'])
def api_set_emu_path():
  fn = pickFile("Select Slippi Dolphin Executable",Settings.load()["emupath"])
  if fn:
    Settings.query.filter_by(name="emupath").update({"value" : fn})
    db.session.commit()
  return jsonify({"status" : "ok"})

#API call for setting the Melee 1.02 ISO path
@bp.route('/setisopath', methods=['GET'])
def api_set_iso_path():
  fn = pickFile("Select Melee 1.02 ISO Path",Settings.load()["isopath"])
  if fn:
    Settings.query.filter_by(name="isopath").update({"value" : fn})
    db.session.commit()
  return jsonify({"status" : "ok"})

#API call for toggling auto scan of replays on startup
@bp.route('/toggleautoscan', methods=['GET'])
def api_toggle_auto_scan():
  s = "False" if Settings.load()["autoscan"] else "True"
  Settings.query.filter_by(name="autoscan").update({"value" : s})
  db.session.commit()
  return jsonify({"status" : "ok"})

#API call for adjusting the maximum number of threads used for scanning
@bp.route('/togglescanthreads', methods=['GET'])
def api_toggle_scan_threads():
  m = current_app.config["MAX_SCAN_THREADS"]
  s = str((Settings.load()["scanthreads"]%m)+1)
  Settings.query.filter_by(name="scanthreads").update({"value" : s})
  db.session.commit()
  return jsonify({"status" : "ok"})

#API call for removing all scanned replays from database (JSONs left intact)
@bp.route('/deletereplays', methods=['POST'])
def api_delete_all_replays():
  Replay.query.delete()
  db.session.commit()
  return jsonify({"status" : "ok"})

#[Deprecated] API call for deleting all slip.py user data
@bp.route('/purge', methods=['POST'])
def api_purge_all_data():
  # Replay.query.delete()
  if os.path.exists(current_app.config["DATA_FOLDER"]):
    shutil.rmtree(current_app.config["DATA_FOLDER"])
  return jsonify({"status" : "ok"})

#API call for adding a folder to scan list
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

#API call for removing a folder from scan list
@bp.route('/scan/del', methods=['POST'])
def api_scan_del():
  d  = request.get_json()["dir"]
  sd = ScanDir.query.filter(ScanDir.fullpath == d).first()
  db.session.delete(sd)
  db.session.commit()
  return jsonify({"status" : "ok"})

#API call for returning pretty list of scanned folders
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
  return jsonify(j)

#API call for checking scan progress
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
    logoutput = [line[:-1] for line in fin.readlines()]

  details = dict({
    "log"     : logoutput,
    "details" : _scan_jobs[token]["details"],
    })
  del _scan_jobs[token]
  logline(tmpfile,f"Scan job deleted")
  now      = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
  scanfile = os.path.join(current_app.config['LOG_FOLDER'],f"scan-{now}.json.gz")
  compressedJsonWrite(details,scanfile)
  return jsonify({"status" : "Done!", "done" : True, "details": f"scan-{now}.json"})

#API call for opening a scan log JSON
@bp.route('/scanlog/<s>', methods=['GET'])
def api_get_scan_log(s):
  base = os.path.join(current_app.config['LOG_FOLDER'],s)
  with open(base,'w') as fout:
    json.dump(compressedJsonRead(base+".gz"), fout, indent=1, sort_keys=False)
  openJson(base)
  return jsonify({"status" : "ok"})

#API call for opening a raw analysis JSON
@bp.route('/raw/<r>', methods=['GET'])
def api_get_raw_analysis(r):
  openJson(
    os.path.join(
      current_app.config['REPLAY_FOLDER'],r+".slp.json"))
  return jsonify({"status" : "ok"})

#API calls for playing replays
@bp.route('/play/<c>',           methods=['GET']) #File
@bp.route('/play/<c>/<sf>',      methods=['GET']) #File, Start
@bp.route('/play/<c>/<sf>/<ef>', methods=['GET']) #File, Start, End
def api_play_replay(c,sf=-123,ef=999999):
  settings = Settings.load()
  isopath  = settings["isopath"]
  emupath  = settings["emupath"]
  r        = Replay.query.filter_by(checksum=c).first()
  p        = json.dumps(os.path.join(r.filedir,r.filename))
  jdata    = f"""{{"mode":"queue","queue":[{{"path":{p},"startFrame":{sf},"endFrame":{ef}}}]}}\r\n"""
  tname    = os.path.join(current_app.config['DATA_FOLDER'],"__replay__.json")
  with open(tname,'w') as fout:
    fout.write(jdata)
  subprocess.Popen([emupath,"-b","-e",isopath,"-i",tname])
  return jsonify({"status" : "ok"})

#API call for initiating a scan over all replays in list of scanned folders
@bp.route('/scan', methods=['POST'])
def api_begin_scan():
  if current_app.config['SCAN_IN_PROGRESS']:
    return jsonify({"status" : "Scan Already In Progress"})

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

#Function called by api_begin_scan() to delegate individual replay scans
def scan_job(token):
  global _scan_jobs

  #Load settings from the database
  settings    = Settings.load()

  #Create a temporary file for logging progress
  tmpfile     = os.path.join(current_app.config['TMP_FOLDER'],token)

  #Set up some other variables
  allreplays  = []
  rdata       = []
  checked     = set()
  checksums   = set()
  namesizes   = set()

  #Load checksums, filenames, and filesizes for all replays currently in DB
  logline(tmpfile,f"Fetching cached replay metadata",new=True)
  for i in Replay.query.all():
    checksums.add(i.checksum)
    namesizes.add((os.path.join(i.filedir,i.filename),i.filesize))

  #Recursively list replys in all scanned directories
  logline(tmpfile,f"Locating .slp Replay files")
  for item in ScanDir.query.all():
    get_all_slippi_files(item.fullpath,allreplays,checked)
  _scan_jobs[token]["total"] = len(allreplays)
  logline(tmpfile,f"Found {len(allreplays)} total files")

  #Filter out replays whose names and file sizes have not changed
  logline(tmpfile,f"Filtering unchanged .slp Replay files")
  replays = [r for r in allreplays if (r,os.stat(r).st_size) not in namesizes]
  logline(tmpfile,f"Found {len(replays)} changed files ({len(allreplays)-len(replays)} unchanged)")

  #Begin the actual scanning process using a threadpool
  logline(tmpfile,f"Starting scan")
  conf      = dict(current_app.config)
  adds      = []
  updates   = []

  #TODO: might spawn multiple GUIs on Windows now that we're using init_gui
  current_app.config['SCAN_IN_PROGRESS'] = True
  with concurrent.futures.ProcessPoolExecutor(max_workers=settings["scanthreads"]) as ex:
    #Submit all scan jobs to the ProcessPoolExecutor to complete as possible
    tasks = {ex.submit(scan_single,i,r,token,conf,checksums) for i,r in enumerate(replays)}
    #As each replay scan finishes...
    for i,t in enumerate(concurrent.futures.as_completed(tasks)):
      print(f"Background scan: {i+1}/{len(replays)} replays scanned",end="\r")
      #Get the result
      res = t.result()
      #If there is no result, the browser was closed as the scan was in progress
      if res is None:
        logline(tmpfile,f"Browser closed by user after {i}/{len(replays)} files")
        break

      #If we have a new replay, add it to our list of replays to add
      if res["replay"] is not None:
        adds.append(res["replay"])

      #If we have an updated replay, add it to our list of replays to update
      if res["update"] is not None:
        updates.append(res["update"])

      #Delete the replay metadata from our result and append it to rdata
      del res["replay"]
      rdata.append(res)

      #Update the number of scans completed
      _scan_jobs[token]["progress"] += 1

  #Add each new replay to the database
  logline(tmpfile,f"Committing {len(adds)} new entries")
  db.session.add_all(adds)

  #Update each existing replay as necessary in the database
  logline(tmpfile,f"Updating {len(updates)} entries: ")
  for u in updates:
    Replay.query.filter_by(checksum=u["checksum"]).update(u)

  #Commit all database transactions
  db.session.commit()
  current_app.config['SCAN_IN_PROGRESS'] = False
  current_app.config["BG_MESSAGES"].append(
    "Background Scan Completed! Reload page to see changes."
    )

  #Clean up
  logline(tmpfile,f"Scan completed")
  _scan_jobs[token]["details"]  = rdata
  _scan_jobs[token]["progress"] = None
  return jsonify({"status" : "ok", "details" : rdata})

#Function called by individual worker threads from scan_job()
def scan_single(i,r,token,conf,checksums):
  #Put together a basic metadata JSON for the replay to be scanned
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

  #Actually scan the replay and update the metadata JSON
  jret = analyze_replay(r,jret,nokeep=False,conf=conf,checksums=checksums)

  #Delete all of the keys we don't need
  del jret["time"]
  del jret["token"]
  del jret["filename_secure"]

  #Return the metadata
  return jret

#Function called by scan_single() for actually analyzing a replay
def analyze_replay(local_file,jret,*,nokeep=False,conf={},checksums=set()):
    #If database already has a replay with the same md5, update its info and call it a day
    m       = md5file(local_file)
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

    #Determine the file name for the analysis JSON
    afile = os.path.join(conf['REPLAY_FOLDER'], m+".slp.json")

    #If an analysis of this replay already exists, don't bother analyzing it
    if conf["ANALYZE_MISSING"] or (not os.path.exists(afile)):
      #Try to actually analyze the replay; if we can't, call it a day
      try:
        _,err = call([conf['ANALYZER'],"-i",local_file,"-a",afile],returnErrors=True)
      except:
        err               = traceback.format_exc()
        jret["status"]    = 'Failure'
        jret["error"]     = f"Failed to run {conf['ANALYZER']} on {local_file}; got the following error:"
        jret["traceback"] = err.split("\n")
        return jret

    if not os.path.exists(afile):
      jret["status"]    = 'Failure'
      jret["error"]     = 'Failed to parse replay; got the following error: <br/><code>'+err+'</code>'
      return jret

    #Load replay data from the analysis JSON
    try:
      rdata             = load_replay(afile)
    except:
      err               = traceback.format_exc()
      jret["status"]    = 'Failure'
      jret["error"]     = f"Failed to load replay JSON from {afile}; got the following error:"
      jret["traceback"] = err.split("\n")
      return jret

    #Add the replay to the database
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

    #Return metadata JSON to caller
    jret["url"]    = '/replays/'+m
    jret["replay"] = replay
    return jret
