#!/usr/bin/python
from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Replay
from datetime import datetime
from app.main import bp
from app.main.forms import ReplaySearchForm

import os, json, sys, subprocess, shlex, hashlib
from datetime import datetime

# Easy colors (print)
class col:
  BLN = '\033[0m'    # Blank
  UND = '\033[1;4m'  # Underlined
  INV = '\033[1;7m'  # Inverted
  CRT = '\033[1;41m' # Critical
  BLK = '\033[1;30m' # Black
  RED = '\033[1;31m' # Red
  GRN = '\033[1;32m' # Green
  YLW = '\033[1;33m' # Yellow
  BLU = '\033[1;34m' # Blue
  MGN = '\033[1;35m' # Magenta
  CYN = '\033[1;36m' # Cyan
  WHT = '\033[1;37m' # White

# Useful printing codes (long)
def inptp(s):
    return input(col.WHT+"["+col.BLU+"input"+col.WHT+"] "+str(s)+col.BLN)
def infop(s):
    print(col.WHT+"["+col.GRN+" info"+col.WHT+"] "+col.BLN+str(s),file=sys.stderr)
def logfp(s,logf=None):
    print(col.WHT+"["+col.MGN+"  log"+col.WHT+"] "+col.BLN+str(s),file=sys.stderr)
    if logf is not None: logf.write(str(s)+"\n")
def dbugp(s):
    print(col.WHT+"["+col.BLK+"debug"+cfol.WHT+"] "+col.BLN+str(s),file=sys.stderr)
def simup(s):
  if _simulate:
    print(col.WHT+"["+col.CYN+"simul"+col.WHT+"] "+col.BLN+str(s),file=sys.stderr)
def warnp(s):
    print(col.WHT+"["+col.YLW+" warn"+col.WHT+"] "+col.BLN+str(s),file=sys.stderr)
def erorp(s):
    print(col.WHT+"["+col.RED+"error"+col.WHT+"] "+col.BLN+str(s)+"\n",file=sys.stderr)
def sendp(s):
    print(col.WHT+"["+col.CYN+" send"+col.WHT+"] "+s+col.BLN,file=sys.stderr)
def recvp(s):
    print(col.WHT+"["+col.CYN+" recv"+col.WHT+"] "+s+col.BLN,file=sys.stderr)
def passp(s):
    return getpass(col.WHT+"["+col.BLU+"paswd"+col.WHT+"] "+str(s)+col.BLN,file=sys.stderr)

@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html.j2', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

# @bp.route('/user/<username>')
# @login_required
# def user(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     page = request.args.get('page', 1, type=int)
#     posts = user.posts.order_by(Post.timestamp.desc()).paginate(
#         page, current_app.config['POSTS_PER_PAGE'], False)
#     next_url = url_for('main.user', username=user.username, page=posts.next_num) \
#         if posts.has_next else None
#     prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
#         if posts.has_prev else None
#     return render_template('user.html.j2', user=user, posts=posts.items,
#                            next_url=next_url, prev_url=prev_url)

# @bp.route('/edit_profile', methods=['GET', 'POST'])
# @login_required
# def edit_profile():
#     form = EditProfileForm(current_user.username)
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         current_user.about_me = form.about_me.data
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('main.edit_profile'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html.j2', title='Edit Profile',
#                            form=form)

# @bp.route('/follow/<username>')
# @login_required
# def follow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('User {} not found.'.format(username))
#         return redirect(url_for('main.index'))
#     if user == current_user:
#         flash('You cannot follow yourself!')
#         return redirect(url_for('main.user', username=username))
#     current_user.follow(user)
#     db.session.commit()
#     flash('You are following {}!'.format(username))
#     return redirect(url_for('main.user', username=username))

# @bp.route('/unfollow/<username>')
# @login_required
# def unfollow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash('User {} not found.'.format(username))
#         return redirect(url_for('main.index'))
#     if user == current_user:
#         flash('You cannot unfollow yourself!')
#         return redirect(url_for('main.user', username=username))
#     current_user.unfollow(user)
#     db.session.commit()
#     flash('You are not following {}.'.format(username))
#     return redirect(url_for('main.user', username=username))

# @bp.route('/api/thing')
# def thing_api():
#     return jsonify({
#         "Time": str(datetime.now()),
#         })

@bp.route('/replays')
# @csrf.exempt
def replays():
    q        = request.args.get("query",None)
    rdir     = os.path.join(current_app.config['STATIC_FOLDER'], "data/replays")
    page     = request.args.get('page', 1, type=int)
    if q is None:
        rdata = current_user.all_replays().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    else:
        rdata = Replay.search(request.args).paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.replays', query=q, page=rdata.next_num) if rdata.has_next else None
    prev_url = url_for('main.replays', query=q, page=rdata.prev_num) if rdata.has_prev else None
    return render_template("replays.html.j2", title="Public Replays", form=ReplaySearchForm(), replays=rdata.items, next_url=next_url, prev_url=prev_url)

@bp.route('/replays/<r>')
def replay_viz(r):
    rdata  = Replay.query.filter_by(checksum=r).first()
    rpath  = os.path.join(current_app.config['STATIC_FOLDER'], "data/replays", r+".slp.json")
    replay = load_replay(rpath)
    replay["__original_filename"] = rdata.filename
    return render_template("replays-single.html.j2", rsummary=rdata, replay=replay)

def get_display_tag(p):
    if p["tag_player"] == "" or p["tag_player"] == "Player":
        if p["player_type"] == 1:
            return "[Lv. {} CPU]".format(p["cpu_level"])
        if p["tag_css"].strip() != "" :
            return "[{}]".format(p["tag_css"].strip().upper())
        return "[Port {}]".format(1+p["port"])
    return p["tag_player"]

def load_replay(rf):
    with open(rf,'r') as jin:
        r                  = json.loads(jin.read())
        r["__file"]        = rf.split("/")[-1].split(".")[0]
        r["__act_length"]  = r["game_length"]-84
        r["__game_length"] = get_game_length(r["game_length"]-123)
        r["p"]             = r["players"]
        for p in r["p"]:
            for k,v in p["interactions"].items():
                p["__int"+k] = v
            p["__l_cancels_hit_pct"] = 0
            if p["l_cancels_hit"] > 0:
                p["__l_cancels_hit_pct"] = 100 * p["l_cancels_hit"] / (p["l_cancels_hit"]+p["l_cancels_missed"])
            p["__tech_hit_pct"] = 100
            if p["missed_techs"] > 0:
                p["__tech_hit_pct"] = 100 * (p["techs"]+p["walltechs"]+p["walltechjumps"]) / (p["techs"]+p["walltechs"]+p["walltechjumps"]+p["missed_techs"])
            p["num_moves_landed"] = p["moves_landed"]["_total"]
            p["__display_tag"] = get_display_tag(p)
    return r

def get_game_length(frames):
    mins   = frames // 3600
    frames -= 3600*mins
    secs   = frames // 60
    frames -= 60*secs
    return f"{mins:02d}:{secs:02d}.{int((100*frames)/60):02d}"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ["slp"]

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

@bp.route('/upload', methods=['GET', 'POST'])
def upload_file():
    #Populate a return JSON
    jret = {
      "error"        : "good",
      "analysis-url" : "",
      "filename"     : "",
      }

    # Just return upload form if this is a get request
    if request.method == 'GET':
      return render_template("upload.html.j2")

    # Error if no file attribute
    if 'file' not in request.files:
        jret["error"] = 'No file part'
        return jsonify(jret)
        # flash('No file part')
        # return redirect(request.url)

    # Check if file is actually submitted
    file = request.files['file']
    if file.filename == '':
        jret["error"] = 'No selected file'
        return jsonify(jret)
        # flash('No selected file')
        # return redirect(request.url)

    jret["filename"] = file.filename
    # return jsonify(jret)
    # check if the post request has the file part
    if file:
        # if not allowed_file(file.filename):
        #     flash('Invalid replay file')
        #     return redirect(request.url)
        filename = secure_filename(file.filename)
        opath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        # dbugp(opath)
        file.save(opath)
        m     = md5file(opath)
        afile = os.path.join(current_app.config['REPLAY_FOLDER'], m+".slp.json")
        _,err = call([current_app.config['ANALYZER'],"-i",opath,"-a",afile],returnErrors=True)
        if not os.path.exists(afile):
          jret["error"] = 'Failed to parse replay; got the following error: <br/><code>'+err+'</code>'
          return jsonify(jret)
          # flash('Failed to parse replay; got the following error: <br/><code>'+err+'</code>')
          # return redirect(request.url)

        if len(Replay.query.filter_by(checksum=m).all()) > 0:
          jret["analysis-url"] = '/replays/'+m
          jret["error"]        = 'Replay already in database'
          return jsonify(jret)
          # flash('Replay already in database')
          # return redirect('replays/'+m)

        rdata = load_replay(afile)

        replay = Replay(
            checksum  = m,
            filename  = filename,
            user_id   = -1,
            is_public = True,
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
        # return redirect('replays/'+m)
