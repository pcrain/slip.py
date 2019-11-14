#!/usr/bin/python
from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app import db, limiter
from app.models import User, Replay
from werkzeug.utils import secure_filename
from app.api import bp

import os, json, sys, subprocess, shlex, hashlib
from datetime import datetime

#Compute md5sum for file
def md5file(fname):
  #http://stackoverflow.com/questions/3431825/generating-a-md5-checksum-of-a-file
  hash_md5 = hashlib.md5()
  with open(fname, "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
      hash_md5.update(chunk)
  return hash_md5.hexdigest()

#Call a process and return its output
def call(coms,inp="",ignoreErrors=False,returnErrors=False):
  # p = subprocess.Popen(coms.split(" "), stdin=PIPE, stdout=PIPE, stderr=PIPE)
  p = subprocess.Popen(coms,
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output, err = p.communicate(inp.encode("utf-8"))
  if ignoreErrors:
    oc = output.decode('utf-8',errors='replace')
  else:
    oc = output.decode('utf-8')
  # print(oc)
  if returnErrors:
    return (oc,err.decode('utf-8'))
  return oc

#Call a process and return its output using shell syntax
def shcall(comstring,inp="",ignoreErrors=False):
  return call(shlex.split(comstring),inp,ignoreErrors)

@bp.route('/upload', methods=['POST'])
@limiter.limit("1000 per hour")
def api_upload_replay():
    requestdate = datetime.utcnow();
    #Populate a return JSON
    jret = {
      "time"         : requestdate,
      "error"        : "good",
      "analysis-url" : "",
      "filename"     : "",
      }

    # Error if no file attribute
    if 'file' not in request.files:
        jret["error"] = 'No file part'
        return jsonify(jret)

    # Check if file is actually submitted
    file = request.files['file']
    if file.filename == '':
        jret["error"] = 'No selected file'
        return jsonify(jret)

    jret["filename"] = file.filename
    # return jsonify(jret)
    # check if the post request has the file part
    if file:
        filename = secure_filename(file.filename)
        opath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(opath)
        m     = md5file(opath)
        afile = os.path.join(current_app.config['REPLAY_FOLDER'], m+".slp.json")
        _,err = call([current_app.config['ANALYZER'],"-i",opath,"-a",afile],returnErrors=True)
        if not os.path.exists(afile):
          jret["error"] = 'Failed to parse replay; got the following error: <br/><code>'+err+'</code>'
          return jsonify(jret)

        if len(Replay.query.filter_by(checksum=m).all()) > 0:
          jret["analysis-url"] = '/replays/'+m
          jret["error"]        = 'Replay already in database'
          return jsonify(jret)

        rdata = load_replay(afile)

        replay = Replay(
            checksum  = m,
            filename  = filename,
            user_id   = -1,
            is_public = True,
            uploaded  = requestdate,
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
