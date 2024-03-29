#!/usr/bin/python

#Flask imports
from flask import render_template, jsonify, flash, redirect, url_for, request, current_app, send_from_directory, abort
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import or_, and_

#App imports
from app import db
from app.helpers import *
from app.main import bp
from app.main.forms import ReplaySearchForm
from app.models import User, Replay, ScanDir, Settings
from app.generators import * #TODO: should do this more cleanly

#Standard imports
from datetime import datetime, timedelta
from collections import defaultdict
import os, math, shutil, ntpath, time, json

#Function to call before any requests
@bp.before_request
def before_request():
    if not os.path.exists(current_app.config["DATA_FOLDER"]):
      return render_template("nodata.html.j2", title="No Data")
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

#Route for rendering default stock images
@bp.route('/static/icons/stock/<path:filename>')
def get_stock_icon(filename):
    basepath = os.path.join(current_app.config["STATIC_FOLDER"],"icons","stock")
    if not os.path.exists(os.path.join(basepath,filename)):
      #Check if the default costume is available
      filename = filename[:-5]+"0.png"
      if not os.path.exists(os.path.join(basepath,filename)):
        return send_from_directory(basepath, '_NONE0.png')
    return send_from_directory(basepath,filename)

#Route for rendering default CSS images
@bp.route('/static/icons/css/<path:filename>')
def get_css_icon(filename):
    basepath = os.path.join(current_app.config["STATIC_FOLDER"],"icons","css")
    if not os.path.exists(os.path.join(basepath,filename)):
      #Check if the default costume is available
      filename = filename[:-5]+"0.png"
      if not os.path.exists(os.path.join(basepath,filename)):
        return send_from_directory(basepath, '_NONE0.png')
    return send_from_directory(basepath,filename)

#Route for favicon for browser
@bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(
      current_app.config["STATIC_FOLDER"],"icons"
      ), 'wolfhead.png', mimetype='image/vnd.microsoft.icon')

#Route for help page
@bp.route('/help')
def help():
  return render_template("help.html.j2", title="Help")

#Route for replay index (home page)
@bp.route('/')
@bp.route('/replays')
def replays():
    rdir     = current_app.config['ANALYSIS_FOLDER']
    q        = request.args.get("query",None)
    ddir     = request.args.get("path","")
    page     = request.args.get('page', 1, type=int)
    scandirs = ScanDir.query.all()

    #Stash our last search for use with backspace button later
    current_app.config["LAST_SEARCH"] = request.args

    #If we're at a top-level scanned directory, back out to index
    for item in scandirs:
      if item.path == ddir:
        ddir = ""
        break

    #Get IDs for all replays corresponding to the current filter
    if (q is None) and (ddir == ""):
        replay_res = current_user.all_replays()
    else:
        replay_res = Replay.search(request.args)

    #Determine whether we need to update our page-navigation nav-dict
    baserequest = '&'.join([f"{k}={v}" for k,v in request.args.items() if k not in ["page","nextpage","prevpage"]])
    if baserequest == current_app.config["REPLAY_NAV_QUERY"]:
      pass; # print("USING CACHED NAV")
    else: #New search query, so navigation nav needs to be repopulated
      current_app.config["REPLAY_NAV_QUERY"] = baserequest
      checksum_list = replay_res.with_entities(Replay.checksum).all()
      current_app.config['REPLAY_NAV'] = {}
      for i,c in enumerate(checksum_list):
        current_app.config['REPLAY_NAV'][c[0]] = {}
        if i > 0:
          current_app.config['REPLAY_NAV'][c[0]]["prev"] = checksum_list[i-1][0]
        if i < (len(checksum_list) - 1):
          current_app.config['REPLAY_NAV'][c[0]]["next"] = checksum_list[i+1][0]

    rdata = replay_res.paginate(page, current_app.config['POSTS_PER_PAGE'], False)

    #Get directory data
    ddata = []
    if ddir == "":
      for item in scandirs:
        subdir = check_single_folder_for_slippi_files(item.path,item.display,indb=True)
        if subdir is not None:
          ddata.append(subdir)
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
    render                              = render_template("index.html.j2",
      autoscan = first and s["autoscan"],
      title    = "Public Replays",
      form     = ReplaySearchForm(),
      replays  = rdata.items,
      dirs     = ddata,
      next_url = next_url,
      prev_url = prev_url)
    return render

#Route for re-executing the last search
@bp.route('/last_search', methods=['GET'])
def last_search():
  query = ""
  for i,(k,v) in enumerate(current_app.config["LAST_SEARCH"].items()):
    query += f"""{"?" if i==0 else "&"}{k}={v}"""
  return redirect(url_for('main.replays')+query)

#Route for an individual replay's analysis page
@bp.route('/replays/<r>')
def replay_analysis_page(r):
    rdata      = Replay.query.filter_by(checksum=r).first()
    replay_loc = os.path.join(rdata.filedir,rdata.filename)

    #(COMPATIBILITY) Move replay from old to new location
    compat_path  = get_analysis_compat_path(r,current_app.config)
    raw_path     = get_analysis_path(r,current_app.config)
    #Move from compatibility folder to new folder as needed
    if os.path.exists(compat_path):
      os.makedirs(ntpath.dirname(raw_path),exist_ok=True)
      shutil.move(compat_path,raw_path)

    #(COMPATIBILITY) Compress output as needed
    zip_path = raw_path+".gz"
    if not os.path.exists(zip_path):
      try:
        if not os.path.exists(raw_path):
          #Try to generate a new analysis on the fly
          slippc_analysis(replay_loc,raw_path,current_app.config)
        compressedJsonWrite(jsonRead(raw_path),zip_path)
      except:
        return abort(418) #File doesn't exist and we've waited long enough
    if os.path.exists(raw_path):
      os.remove(raw_path)

    exists = os.path.exists(replay_loc)
    try:
      replay = load_analysis(zip_path)
    except:
      return abort(418) #File doesn't exist and we've waited long enough
    replay["__original_filename"] = rdata.filename
    replay["__filedir"]           = rdata.filedir
    replay["__checksum"]          = r
    replay["__exists"]            = exists

    s      = Settings.load()
    if s["emupath"] == "" or (not os.path.exists(s["emupath"])):
      replay["__canplay"] = False
      replay["__play"]    = "Dolphin Path Not Set"
    elif s["isopath"] == "" or (not os.path.exists(s["isopath"])):
      replay["__canplay"] = False
      replay["__play"]    = "Melee 1.02 ISO Path Not Set"
    else:
      replay["__canplay"] = True
      replay["__play"]    = "Watch Replay"

    return render_template("replay.html.j2", title=rdata.filename, rsummary=rdata, replay=replay)

#[Deprecated] Route for replay upload page
@bp.route('/upload', methods=['GET'])
def upload_page():
  return render_template("upload.html.j2", title="Upload Replays")

#Route for organize page
@bp.route('/organize', methods=['GET'])
def organize_page():
  s = Settings.load()
  return render_template("organize.html.j2", title="Organize")

#Route for settings page
@bp.route('/settings', methods=['GET'])
def settings_page():
  s = Settings.load()
  return render_template("settings.html.j2", title="Settings", settings=s)

#Route for page showing index of players for whom we can display stats
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

#Route for finder page
@bp.route('/filepicker', methods=['GET'])
def filepicker_page():
  api_call  = request.args.get("api_call",None)
  if api_call == "setemupath":
    start_dir = ntpath.dirname(Settings.load()["emupath"])
  elif api_call == "setisopath":
    start_dir = ntpath.dirname(Settings.load()["isopath"])
  else:
    start_dir = ""
  return render_template("filepicker.html.j2", title="Find a File", api_call=api_call, start_dir=json.dumps(start_dir))

#Route for scan page
@bp.route('/scan', methods=['GET'])
def scan_page():
  ldirs = []

  for item in ScanDir.query.all():
    lbase = item.path
    f     = item.display
    full  = item.fullpath
    broke = False
    if not os.path.exists(full): #Broken symlink
      broke = True
    else:
      try:
        os.listdir(os.path.join(lbase,f))
      except PermissionError: #Access is forbidden
        broke = True
    if broke:
      ldirs.append({
        "name"  : f,
        "stats" : {
            "name"  : f,
            "path"  : os.path.join(lbase,f),
            "dirs"  : 0,
            "files" : 0,
            "ftype" : "files",
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

#Route for individual player's stats page
@bp.route('/stats/<tag>', methods=['GET'])
def stats_page(tag):
  tag           = tag.replace("_","#") #Replace underscore with pound sign
  stats         = get_stats(tag,request.args)
  return render_template("stats.html.j2", title=tag, stats=stats)

#Function for getting stats on player with a given tag
def get_stats(tag,args):
  ndays  = int(args.get("ndays", 10000))   #Max number of days to backlog
  ngames = int(args.get("ngames",1000000)) #Max number of games to backlog
  mlen   = 10                              #Length of recent / most player opponent lists

  #Get data from last ndays days
  dmap     = {}   #map of dates to winrates
  earliest = (datetime.now()-timedelta(days=ndays)).strftime('%Y-%m-%d')

  #Start with a basic search for tag in either player slot
  p1and=[Replay.p1codetag==tag]
  p2and=[Replay.p2codetag==tag]

  #Check if we're filtering by character
  if "char" in args:
    p1and.append(Replay.p1char==args["char"])
    p2and.append(Replay.p2char==args["char"])

  #Check if we're filtering by opponent character
  if "vs" in args:
    p1and.append(Replay.p2char==args["vs"])
    p2and.append(Replay.p1char==args["vs"])

  #Check if we're filtering by opponent code
  if "against" in args:
    p1and.append(Replay.p2codetag==args["against"].replace("_","#"))
    p2and.append(Replay.p1codetag==args["against"].replace("_","#"))

  #Set up a giant and statement for p1 and p2 args
  bigand = [or_(and_(*p1and),and_(*p2and))]
  #Check if we're filtering by date
  if ndays >= 0:
    bigand.append(Replay.played > earliest)
  #Check if we're filtering by stage
  if "stage" in args:
    bigand.append(Replay.stage == args["stage"])

  #Get all relevant rows from the database
  rows = (Replay.query
    .filter(
      and_(*bigand)
    ).order_by(Replay.played.desc())
    .limit(ngames)
    .all()
    )

  #Reset number of games based on the number of rows we actually got
  actualgames = len(rows)

  #Compile list of legal stages
  legal    = [8,31,28,32,2,3,-1]
  stagemap = {v:i for i,v in enumerate(legal)}

  #Set up dict for stats
  stats = {
    "tag"    : tag,                                    #Tag of player we're showing stats for
    "name"   : tag,                                    #Display name for player we're showing stats for
    "count"  : len(rows),                              #Total number of matches returned from query
    "char"   : [[i]+[0,0,0,0,0,0] for i in range(26)], #Own character / colors selection choices
    "opp"    : [
      [i]          + #Char id
      [0,0,0]      + #Win,Lose,Draw against that char
      [0]          + #Average end Stocks against that char
      [0,0,0,0,0,0]+ #Punish,Defense,Neutral,Accuracy,Control,APM against that char
      [0,0,0,0,0,0]  #Punish,Defense,Neutral,Accuracy,Control,APM for that char against you
      for i in range(26)],
    "stg"    : [[legal[i]]+[0,0,0] for i in range(7)], #Stage,Win,Lose,Draw against each legal stage + others
    "recent" : [],                                     #Win,Lose,Draw against most recent opponents
    "top"    : [],                                     #Win,lose,Draw against most played opponents
    }
  fourstocks  = [0 for i in range(26)]                  #Our fur-stock counter for use with stats
  fourstocked = [0 for i in range(26)]                  #Foe four-stock counter for use with stats

  #Set up header banner
  if args.get("ndays",False):
    stats["subtitle"] = f"Showing stats for {actualgames} games in the last {ndays} days"
  elif args.get("ngames",False):
    stats["subtitle"] = f"Showing stats for last {actualgames} games"
  else:
    stats["subtitle"] = f"Showing lifetime stats for {actualgames} games"
  if "char" in args:
    stats["subtitle"] += f" as <span title='Click to remove player character filter' onclick='changeChar(undefined)' class='filter filterChar'>{intchardata[int(args['char'])]['name']}</span>"
  if "vs" in args:
    stats["subtitle"] += f" vs. <span title='Click to remove opponent character filter' onclick='changeOpponent(undefined)' class='filter filterVs'>{intchardata[int(args['vs'])]['name']}</span>"
  if "stage" in args:
    stats["subtitle"] += f" on <span title='Click to remove stage filter' onclick='changeStage(undefined)' class='filter filterStage'>{intstagedata[int(args['stage'])]['name']}</span>"
  if "against" in args:
    stats["subtitle"] += f" against <span title='Click to remove opponent connect code filter' onclick='changeAgainst(undefined)' class='filter filterAgainst'>{args['against'].replace('_','#')}</span>"

  #Populate bar chart up to today, but only down to the earliest match played in a timeframe
  #  e.g., we are searching 28 days back, but our earliest game is 25 days ago, just show 25 days
  if len(rows) > 0:
    minstamp = localStamp(rows[-1].played)
    mindate  = datetime.strptime(minstamp[:10], '%Y-%m-%d')
  else:
    mindate  = datetime.now()
  smindate = mindate.strftime('%Y-%m-%d')
  smaxdate = datetime.now().strftime('%Y-%m-%d')
  newdays  = 0
  while smindate <= smaxdate:
    # dmap[smindate] = [0,0,0]
    dmap[smindate] = [0,0,0,0,0,0,0,0] #1, 2, 3, 4, -4, -3, -2, -1 stocks
    mindate        = mindate+timedelta(days=1)
    smindate       = mindate.strftime('%Y-%m-%d')
    newdays       += 1
  ndays = newdays

  #Set up miscellaneous variables
  olast  = None #last opponent
  top    = {}   #most played opponents
  tagmap = {}   #map of codes to display tags

  #Compute stats for each returned result
  for rnum,r in enumerate(rows):
    #Determine player's and opponent's stats for the game
    gdate     = localStamp(r.played)[:10]                #date the game was played
    p         = 1 if r.p1codetag == tag else 2           #player's port number
    pname     = r.p1metatag  if p == 1 else r.p2metatag  #player's display name
    oname     = r.p2metatag  if p == 1 else r.p1metatag  #opponent's display tag
    o         = 3-p                                      #opponent's port number
    otag      = r.p2codetag  if p == 1 else r.p1codetag  #opponent's code tag
    pstocks   = r.p1stocks   if p == 1 else r.p2stocks   #player stock count
    ostocks   = r.p2stocks   if p == 1 else r.p1stocks   #opponent stock count
    pcolor    = r.p1color    if p == 1 else r.p2color    #player costume choice
    pchar     = r.p1char     if p == 1 else r.p2char     #player character choice
    ochar     = r.p2char     if p == 1 else r.p1char     #opponent character choice
    stage     = r.stage
    stockdiff = (r.p1stocks-r.p2stocks)*(1 if p == 1 else -1) #stock difference between players
    ppunish   = r.p1punish   if p == 1 else r.p2punish   #player character punish
    opunish   = r.p2punish   if p == 1 else r.p1punish   #opponent character punish
    pdefense  = r.p1defense  if p == 1 else r.p2defense  #player character defense
    odefense  = r.p2defense  if p == 1 else r.p1defense  #opponent character defense
    pneutral  = r.p1neutral  if p == 1 else r.p2neutral  #player character neutral
    oneutral  = r.p2neutral  if p == 1 else r.p1neutral  #opponent character neutral
    paccuracy = r.p1accuracy if p == 1 else r.p2accuracy #player character accuracy
    oaccuracy = r.p2accuracy if p == 1 else r.p1accuracy #opponent character accuracy
    pcontrol  = r.p1control  if p == 1 else r.p2control  #player character control
    ocontrol  = r.p2control  if p == 1 else r.p1control  #opponent character control
    pspeed    = r.p1speed    if p == 1 else r.p2speed    #player character speed
    ospeed    = r.p2speed    if p == 1 else r.p1speed    #opponent character speed

    #Get latest dates, display names and tags
    if stats["name"] == tag:
      stats["name"] = pname
    if not tagmap.get(otag,None):
      tagmap[otag] = oname

    #Determine the game results
    if pstocks > ostocks:   res = 0 #win
    elif ostocks > pstocks: res = 1 #lose
    else:                   res = 2 #draw

    #Increment appropriate character, costume, opponent, stage, and result choices, creating new ones as needed
    #  TODO: ignores extended characters and costumes, fix later???
    if pchar < 26 and pcolor < 6:
      stats["char"][pchar][pcolor+1] += 1
    if ochar < 26:
      stats["opp"][ochar][res+1]     += 1
    if otag != olast:
      stats["recent"].append([0,0,0,otag])
    stats["recent"][-1][res]  += 1
    if not otag in top:
      top[otag] = [0,0,0,otag]
    stats["stg"][stagemap.get(stage,-1)][res+1]  += 1
    top[otag][res] += 1

    #Increment appropriate stats
    if ochar < 26:
      stats["opp"][ochar][4]  += stockdiff

      #Our stats vs. this character
      stats["opp"][ochar][5]  += ppunish
      if pdefense > 0:
        stats["opp"][ochar][6]  += pdefense
      else:
        fourstocks[ochar] += 1
      stats["opp"][ochar][7]  += pneutral
      stats["opp"][ochar][8]  += paccuracy
      stats["opp"][ochar][9]  += pcontrol
      stats["opp"][ochar][10] += pspeed

      #This character's stats vs. us
      stats["opp"][ochar][11]  += opunish
      if odefense > 0:
        stats["opp"][ochar][12]  += odefense
      else:
        fourstocked[ochar] += 1
      stats["opp"][ochar][13]  += oneutral
      stats["opp"][ochar][14]  += oaccuracy
      stats["opp"][ochar][15]  += ocontrol
      stats["opp"][ochar][16]  += ospeed

    #Track dates of matches that fall within the requested date range
    if pstocks > ostocks:
      dmap[gdate][pstocks-1] += 1
    elif pstocks < ostocks:
      dmap[gdate][-ostocks] += 1

    olast = otag #Set last-played opponent

  #Take the mean of all of our stats in each matchup
  for ochar in range(26):
    ogames = sum(stats["opp"][ochar][1:4])
    for stat in range(4,17):
      if ogames > 0:
        if stat == 6: #For survivabilty stat, we ignore 4-stock games
          games_that_count = (ogames-fourstocks[ochar])
        elif stat == 12: #For survivabilty stat, we ignore 4-stock games
          games_that_count = (ogames-fourstocked[ochar])
        else:
          games_that_count = (ogames)
        if games_that_count > 0:
          stats["opp"][ochar][stat] /= games_that_count

  #Reconcile Slippi codes with display tags
  for o in top.values():    o.append(tagmap[o[-1]])
  for o in stats["recent"]: o.append(tagmap[o[-1]])

  #Sort own characters by number of times picked
  stats["char"] = sorted(stats["char"],key=lambda x: sum(x[1:]), reverse=True)
  #Get preferred costumes for each character
  for char in stats["char"]:
    char.append(max(0,char[1:].index(max(char[1:])))) #7th item in the array is the preferred costume
  #Sort opponent characters by wins / (wins+losses) (2nd element of tuple sorts non-zero losses properly)
  stats["opp"] = sorted(stats["opp"],key=lambda x: (x[1]/(max(1,x[1]+x[2])),x[2]), reverse=True)
  #Sort stages characters by wins / (wins+losses)
  stats["stg"] = sorted(stats["stg"],key=lambda x: x[1]/(max(1,x[1]+x[2])), reverse=True)
  #Sort top opponents by most-played
  stats["top"]  = sorted([top[k] for k in top],key=lambda x: x[0]+x[1]+x[2], reverse=True)[:mlen]
  #Recent opponent characters are already sorted
  stats["recent"] = stats["recent"][:mlen]

  #Determine where to split columns for character MUs
  stats["splitpoint"]  = 9
  stats["splitpoint2"] = 18
  for i,c in enumerate(stats["opp"]):
    if (c[1] + c[2]) == 0:
      if i > 18:
        stats["splitpoint"] = math.ceil(i/3)  #Determine the halfway point for the characters we've played
        stats["splitpoint2"] = math.ceil(2*i/3)  #Determine the halfway point for the characters we've played
      elif i > 9:
        stats["splitpoint"] = math.ceil(i/2)  #Determine the halfway point for the characters we've played
      break

  #Game dates are already sorted, so convert it to proper bar chart format
  gdata = [{
      "Date"  : k,          #dates
      "Wins"  : sum(dmap[k][:4]), #wins
      "Losses": sum(dmap[k][-4:]), #losses
      "Stocks": dmap[k],
      "4-Stock Wins": dmap[k][3],
      "3-Stock Wins": dmap[k][2],
      "2-Stock Wins": dmap[k][1],
      "1-Stock Wins": dmap[k][0],
      "1-Stock Losses": dmap[k][-1],
      "2-Stock Losses": dmap[k][-2],
      "3-Stock Losses": dmap[k][-3],
      "4-Stock Losses": dmap[k][-4],
      # "Stocks": {i : dmap[k][i] for i in range(-4,5)}, #stock count distribution
    } for k in dmap]
  stats["bydate"] = {
    "data" : gdata,
    "meta" : {
      "labels"   : "Date",
      "lshow"    : [0,ndays-1],
      "pos"      : "Wins",
      "neg"      : "Losses",
      "stack"    : "Stocks", #Uncomment for graadient version
      # "stack"    : None,     #Uncomment for non-gradient version
      "ttkeys"   : [] if len(gdata) == 0 else list([k for k in gdata[0].keys() if k not in ["Stocks"]]), #keys to show in tooltip
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
      "lshow"    : list(range(len(stats["top"]))),
      "pos"      : "Wins",
      "neg"      : "Losses",
      "stack"    : None,
      "ttkeys"   : ["Code","Wins","Losses"], #Jinja does not preserve dict key order
      "rot"      : 90,
    }
  }
  stats["bytop"]["data"] = sorted(stats["bytop"]["data"],key=lambda x: x["Code"])[:10]
  return stats
