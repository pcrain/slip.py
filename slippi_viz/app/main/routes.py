#!/usr/bin/python
from flask import render_template, jsonify, flash, redirect, url_for, request, current_app, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy        import or_, and_

from app import db
from app.main import bp
from app.main.forms import ReplaySearchForm
from app.main.helpers import *
from app.models import User, Replay, ScanDir, Settings

from datetime import datetime, timedelta
from collections import defaultdict
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

@bp.route('/help')
def help():
  return render_template("help.html.j2", title="Help")

@bp.route('/')
@bp.route('/replays')
def replays():
    rdir     = current_app.config['REPLAY_FOLDER']
    q        = request.args.get("query",None)
    ddir     = request.args.get("path","")
    page     = request.args.get('page', 1, type=int)
    scandirs = ScanDir.query.all()

    #If we're at a top-level scanned directory, back out to index
    for item in scandirs:
      if item.path == ddir:
        ddir = ""
        break

    if (q is None) and (ddir == ""):
        rdata = current_user.all_replays().paginate(page, current_app.config['POSTS_PER_PAGE'], False)
    else:
        rdata = Replay.search(request.args).paginate(page, current_app.config['POSTS_PER_PAGE'], False)

    ddata = []
    if ddir == "":
        for item in scandirs:
            ddata.append(check_single_folder_for_slippi_files(item.path,item.display,indb=True))
    else:
        ddata = check_for_slippi_files(ddir,nav=2)

    #Copy GET args and set next / previous page
    qdict             = dict(request.args)
    qdict["nextpage"] = rdata.next_num
    qdict["prevpage"] = rdata.prev_num
    if "page" in qdict:
      del qdict["page"]
    next_url = url_for('main.replays', page=qdict["nextpage"], **qdict) if rdata.has_next else None
    prev_url = url_for('main.replays', page=qdict["prevpage"], **qdict) if rdata.has_prev else None

    #Check if we just launched the app (for autoscan purposes)
    first                               = current_app.config['JUST_LAUNCHED']
    current_app.config['JUST_LAUNCHED'] = False
    s                                   = Settings.load()
    return render_template("index.html.j2",
      autoscan = first and s["autoscan"],
      title    = "Public Replays",
      form     = ReplaySearchForm(),
      replays  = rdata.items,
      dirs     = ddata,
      next_url = next_url,
      prev_url = prev_url)

@bp.route('/replays/<r>')
def replay_viz(r):
    rdata  = Replay.query.filter_by(checksum=r).first()
    rpath  = os.path.join(current_app.config['REPLAY_FOLDER'], r+".slp.json")
    exists = os.path.exists(os.path.join(rdata.filedir,rdata.filename))
    replay = load_replay(rpath)
    replay["__original_filename"] = rdata.filename
    replay["__filedir"]           = rdata.filedir
    replay["__checksum"]          = r
    replay["__exists"]            = exists
    return render_template("replay.html.j2", title=rdata.filename, rsummary=rdata, replay=replay)

@bp.route('/upload', methods=['GET'])
def upload_page():
  return render_template("upload.html.j2", title="Upload Replays")

@bp.route('/settings', methods=['GET'])
def settings_page():
  s = Settings.load()
  return render_template("settings.html.j2", title="Settings", settings=s)

@bp.route('/stats', methods=['GET'])
def stats_index_page():
  codes = defaultdict(int)
  for row in Replay.query.all():
    if row.p1codetag != "": codes[row.p1codetag] += 1
    # else:                   codes[row.p1metatag] += 1
    if row.p2codetag != "": codes[row.p2codetag] += 1
    # else:                   codes[row.p2metatag] += 1
  players = sorted([(k,codes[k]) for k in codes],key=lambda x: x[1], reverse=True)
  return render_template("stats-index.html.j2", title="Stats Index", players=players)

def get_stats(tag,args):
  ndays = 29         #Number of days to backlog
  mlen  = 26         #Length of recent / most player opponent lists
  count = 10000      #Number of games to fetch

  #Start with a basic search for tag in either player slot
  p1and=[Replay.p1codetag==tag]
  p2and=[Replay.p2codetag==tag]

  if "char" in args:
    p1and.append(Replay.p1char==args["char"])
    p2and.append(Replay.p2char==args["char"])

  #Get all relevant rows from the database
  rows = (Replay.query
    .filter(
      or_(
        and_(*p1and),
        and_(*p2and)
      )
    ).order_by(Replay.played.desc())
    .limit(count)
    .all()
    )

  #Set up dict for stats
  stats = {
    "tag"    : tag,                                    #Tag of player we're showing stats for
    "name"   : None,                                   #Display name for player we're showing stats for
    "count"  : len(rows),                              #Total number of matches returned from query
    "char"   : [[i]+[0,0,0,0,0,0] for i in range(26)], #Own character / colors selection choices
    "opp"    : [[i]+[0,0,0] for i in range(26)],       #Char,Win,Lose,Draw against each character
    "recent" : [],                                     #Win,Lose,Draw against most recent opponents
    "top"    : [],                                     #Win,lose,Draw against most played opponents
    }

  #Set up miscellaneous variables
  olast  = None #last opponent
  latest = None #date of last match played
  top    = {}   #most played opponents
  tagmap = {}   #map of codes to display tags
  dmap   = {}   #map of dates to winrates

  #Compute stats for each returned result
  for rnum,r in enumerate(rows):
    #Determine player's and opponent's stats for the game
    gdate   = r.played[:10]                          #date the game was played
    p       = 1 if r.p1codetag == tag else 2         #player's port number
    pname   = r.p1metatag if p == 1 else r.p2metatag #player's display name
    oname   = r.p2metatag if p == 1 else r.p1metatag #opponent's display tag
    o       = 3-p                                    #opponent's port number
    otag    = r.p2codetag if p == 1 else r.p1codetag #opponent's code tag
    pstocks = r.p1stocks  if p == 1 else r.p2stocks  #player stock count
    ostocks = r.p2stocks  if p == 1 else r.p1stocks  #opponent stock count
    pcolor  = r.p1color   if p == 1 else r.p2color   #player costume choice
    pchar   = r.p1char    if p == 1 else r.p2char    #player character choice
    ochar   = r.p2char    if p == 1 else r.p1char    #opponent character choice

    #Get latest dates, display names and tags
    if not stats["name"]:
      stats["name"] = pname
    if not tagmap.get(otag,None):
      tagmap[otag] = oname
    if not latest:
      latest    = gdate
      asdate    = datetime.strptime(latest, '%Y-%m-%d')
      #Get data from last ndays days
      for i in range(ndays-1,-1,-1):
        timestamp = (asdate-timedelta(days=i)).strftime('%Y-%m-%d')
        dmap[timestamp] = [0,0,0]

    #Determine the game results
    if pstocks > ostocks:   res = 0 #win
    elif ostocks > pstocks: res = 1 #lose
    else:                   res = 2 #draw

    #Increment appropriate character, costume, opponent, and result choices, creating new ones as needed
    stats["char"][pchar][pcolor+1] += 1
    stats["opp"][ochar][res+1]     += 1
    if otag != olast:
      stats["recent"].append([0,0,0,otag])
    stats["recent"][-1][res]  += 1
    if not otag in top:
      top[otag] = [0,0,0,otag]
    top[otag][res] += 1

    #Only track matches that fall within the requested date range
    if gdate in dmap:
      dmap[gdate][res] += 1

    olast = otag #Set last-played opponent

  #Reconcile Slippi codes with display tags
  for o in top.values():    o.append(tagmap[o[-1]])
  for o in stats["recent"]: o.append(tagmap[o[-1]])

  # print(dmap)

  #Sort own characters by number of times pickes
  stats["char"] = sorted(stats["char"],key=lambda x: sum(x[1:]), reverse=True)
  #Get preferred costumes for each character
  for char in stats["char"]:
    char.append(max(0,char[1:].index(max(char[1:])))) #7th item in the array is the preferred costume
  #Sort opponent characters by wins / (wins+losses)
  stats["opp"] = sorted(stats["opp"],key=lambda x: x[1]/(max(1,x[1]+x[2])), reverse=True)
  #Sort top opponents by most-played
  stats["top"]  = sorted([top[k] for k in top],key=lambda x: x[0]+x[1]+x[2], reverse=True)[:mlen]
  #Recent opponent characters are already sorted
  stats["recent"] = stats["recent"][:mlen]

  #Game dates are already sorted, so convert it to proper bar chart format
  stats["bydate"] = { "data" : [{
      "Date"  : k,          #dates
      "Wins"  : dmap[k][0], #wins
      "Losses": dmap[k][1], #losses
    } for k in dmap],
    "meta" : {
      "labels"   : "Date",
      "pos"      : "Wins",
      "neg"      : "Losses",
      "ttkeys"   : ["Date","Wins","Losses"], #keys to show in tooltip
      "rot"      : 0,
    }
  }
  #Compile barchart data for most played opponents
  stats["bytop"] = { "data" : [{
      "Code"  : item[3], #code
      "Wins"  : item[0], #wins
      "Losses": item[1], #losses
    } for item in stats["top"]],
    "meta" : {
      "labels"   : "Code",
      "pos"      : "Wins",
      "neg"      : "Losses",
      "ttkeys"   : ["Code","Wins","Losses"], #Jinja does not preserve dict key order
      "rot"      : 90,
    }
  }
  stats["bytop"]["data"] = sorted(stats["bytop"]["data"],key=lambda x: x["Code"])[:10]
  return stats

@bp.route('/stats/<tag>', methods=['GET'])
def stats_page(tag):
  tag   = tag.replace("_","#") #Replace underscore with pound sign
  stats = get_stats(tag,request.args)
  return render_template("stats.html.j2", title=tag, stats=stats)

@bp.route('/stats2/<tag>', methods=['GET'])
def stats2_page(tag):
  tag     = tag.replace("_","#") #Replace underscore with pound sign
  stats   = get_stats(tag,request.args)
  # return render_template("stats2.html.j2", title=tag, stats=stats, bardata=stats["bytop"])
  return render_template("stats2.html.j2", title=tag, stats=stats, bardata=stats["bydate"])

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
