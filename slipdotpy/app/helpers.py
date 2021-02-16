#!/usr/bin/python
from flask import current_app
from datetime import datetime, timedelta
import os, json, sys, subprocess, shlex, hashlib, stat, ntpath, gzip, time
import tkinter as tk
from tkinter import filedialog
from multiprocessing import Process, Queue

from PyQt5 import QtCore, QtWidgets

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

#Compute md5sum for string
def md5(string):
  return hashlib.md5(string.encode('utf-8')).hexdigest()

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
  if os.name == 'nt': #Suppres spawning of consoles
    s = subprocess.STARTUPINFO()
    s.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    p = subprocess.Popen(coms, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=s)
  else:
    p = subprocess.Popen(coms, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output, err = p.communicate(inp.encode("utf-8"))
  oc = output.decode('utf-8',errors='replace' if ignoreErrors else 'strict')
  return (oc,err.decode('utf-8')) if returnErrors else oc

#Call a process and return its output using shell syntax
def shcall(comstring,inp="",ignoreErrors=False,returnErrors=False):
  return call(shlex.split(comstring),inp,ignoreErrors,returnErrors)

#Load replay data from an analysis JSON
def load_replay(rf):
    with open(rf,'r') as jin:
        r                  = json.loads(jin.read())
        r["__file"]        = rf.split("/")[-1].split(".")[0]
        r["__act_length"]  = r["game_length"]-84
        r["__game_length"] = get_game_length(r["game_length"]-123)
        r["__game_secs"]   = frame_to_timestamp(r["game_length"])
        r["p"]             = r["players"]
        for p in r["p"]:
            for k,v in p["interaction_frames"].items():
                p["__int"+k] = v
            for k,v in p["interaction_damage"].items():
                p["__dmg"+k] = v
            p["__air_pct"] = 100 * p["air_frames"] / (r["game_length"])
            p["__l_cancels_hit_pct"] = 0
            if p["l_cancels_hit"] > 0:
                p["__l_cancels_hit_pct"] = 100 * p["l_cancels_hit"] / (p["l_cancels_hit"]+p["l_cancels_missed"])
            p["__tech_hit_pct"] = 100
            p["__techs_hit"] = p["techs"]+p["walltechs"]+p["walltechjumps"]
            if p["missed_techs"] > 0:
                p["__tech_hit_pct"] = 100 * (p["__techs_hit"]) / (p["__techs_hit"]+p["missed_techs"])
            p["num_moves_landed"] = p["moves_landed"]["_total"]
            p["__display_tag"] = get_display_tag(p)
    return r

#Determine a nice dispaly tag based on Display Name, Slippi Code, CSS Code, or Port
def get_display_tag(p):
    if p["tag_player"] == "" or p["tag_player"] == "Player":
        if p["player_type"] == 1:
            return "[Lv. {} CPU]".format(p["cpu_level"])
        if p["tag_css"].strip() != "" :
            return "[{}]".format(p["tag_css"].strip().upper())
        if p["tag_code"].strip() != "" :
            return "[{}]".format(p["tag_code"].strip().upper())
        return "[Port {}]".format(1+p["port"])
    return p["tag_player"]

#Get a nicely formatted string representing time elapsed based on frame count
def get_game_length(frames):
    mins   = frames // 3600
    frames -= 3600*mins
    secs   = frames // 60
    frames -= 60*secs
    return f"{mins:02d}:{secs:02d}.{int((100*frames)/60):02d}"

#Fallback in case we can't parse time from a .slp file
def try_parse_time(t):
  try:
    t = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S")
  except:
    t = datetime.strptime("2000-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")
  return t.strftime('%Y-%m-%d_%H-%M-%S')

#Recursively list slippi files in directory
def get_all_slippi_files(topdir,files,checked):
  rpath=os.path.realpath(topdir)
  if rpath in checked:
    return
  checked.add(rpath)
  for f in os.listdir(topdir):
    path = os.path.join(topdir,f)
    if os.path.isfile(path) and path[-4:] in [".slp",".zlp"]:
      files.append(path)
    elif os.path.isdir(path):
      get_all_slippi_files(path,files,checked)

#Write a line to a log file
def logline(l,text,new=False):
  with open(l,"w" if new else "a") as log:
    log.write(f"[{datetime.utcnow()}] {text}\n")

#Check if a file is hidden (X-platform)
def is_hidden(filepath):
    name = os.path.basename(os.path.abspath(filepath))
    return name.startswith('.') or has_hidden_attribute(filepath)

#Check if a file is hidden (X-platform)
def has_hidden_attribute(filepath):
    return False #TODO: can't check for hidden files on Windows right now
    return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

#Count all files / subdirectories at a path
def count_files(path,fiterfunc=None):
  ndirs  = 0
  nfiles = 0
  try:
    if os.access(path, os.R_OK) and os.access(path, os.W_OK):
      for f in os.listdir(path):
        s = os.path.join(path,f)
        if os.path.isdir(s) and os.access(s, os.R_OK) and (not is_hidden(s)):
            ndirs += 1
        elif (fiterfunc is None) or fiterfunc(f):
            nfiles += 1
    return {"dirs" : ndirs, "files" : nfiles}
  except PermissionError:
    return {"dirs" : ndirs, "files" : nfiles}

#Count slippi files / subdirectories at a path
def count_slippi_files(path):
  return count_files(path,lambda x: x[-4:] in [".slp",".zlp"])

#Get info about all files in a directory (no recursion)
def check_for_files(path,nav=False):
  ddata = []
  if nav: #Add navigations to current / previous folder
    b = os.path.dirname(path)
    c = count_files(b)
    ddata.append({
      "name"  : "[Up]",
      "path"  : b,
      "dirs"  : c["dirs"],
      "files" : c["files"],
      "ftype" : "files",
      "class" : "updir",
      "click" : "travel",
      "sort"  : 1,
      })
  for f in os.listdir(path):
      data = check_single_folder_for_any_files(path,f)
      if data is not None:
        ddata.append(data)
  return ddata

#Scan one folder for any files
def check_single_folder_for_any_files(parent,base,*,click=None,classd="",indb=False):
  p = os.path.join(parent,base)
  if os.access(p, os.R_OK) and (not is_hidden(p)):
    if os.path.isdir(p):
      c = count_files(p)
      return {
          "name"  : base,
          "path"  : p,
          "dirs"  : c["dirs"],
          "files" : c["files"],
          "ftype" : "files",
          "class" : classd,
          "click" : "travel" if click is None else click,
          "sort"  : 4,
        }
    else:
      return {
        "name"  : base,
        "path"  : p,
        "dirs"  : 0,
        "files" : 0,
        "ftype" : None,
        "class" : "file",
        "click" : "pickFile" if click is None else click,
        "sort"  : 5,
      }
  return None

#Get info about slippi files in a directory (no recursion)
def check_for_slippi_files(path,nav=False):
  ddata = []
  if nav: #Add navigations to current / previous folder
    b = os.path.dirname(path)
    c = count_slippi_files(b)
    ddata.append({
      "name"  : "[Up]",
      "path"  : b,
      "dirs"  : c["dirs"],
      "files" : c["files"],
      "ftype" : "replays",
      "class" : "updir",
      "click" : "travel",
      "sort"  : 1,
      })
    if nav < 2:
      c = count_slippi_files(path)
      ddata.append({
        "name"  : "Add "+path,
        "path"  : path,
        "dirs"  : c["dirs"],
        "files" : c["files"],
        "ftype" : "replays",
        "class" : "curdir",
        "click" : "travel",
        "sort"  : 2,
        })
  for f in os.listdir(path):
      data = check_single_folder_for_slippi_files(path,f)
      if data is not None:
        ddata.append(data)
  return ddata

#Scan one folder for Slippi files
def check_single_folder_for_slippi_files(parent,base,*,click=None,classd="",indb=False):
  p = os.path.join(parent,base)
  #Show deleted folders if they are in the database
  if not os.path.exists(p) and indb:
    return {
      "name"  : base,
      "path"  : p,
      "dirs"  : 0,
      "files" : 0,
      "ftype" : "replays",
      "class" : "broken",
      "click" : "delScanDir",
      "sort"  : 4,
      }
  if os.path.isdir(p) and os.access(p, os.R_OK) and (not is_hidden(p)):
    c = count_slippi_files(p)
    return {
        "name"  : base,
        "path"  : p,
        "dirs"  : c["dirs"],
        "files" : c["files"],
        "ftype" : "replays",
        "class" : classd,
        "click" : "travel" if click is None else click,
        "sort"  : 4,
      }
  return None

#Compress writing example
def compressedJsonWrite(data,filename):
  with gzip.GzipFile(filename, 'w') as fout:
    fout.write(json.dumps(data).encode('utf-8'))

#Compress reading example
def compressedJsonRead(filename):
  with gzip.GzipFile(filename, 'r') as fin:
    return json.loads(fin.read().decode('utf-8'))

#Open JSON in OS's default JSON viewer
def openJson(path,mimetype="application/json"):
  if os.name == 'nt':
    notepad = os.path.join(os.getenv('WINDIR'), 'notepad.exe')
    subprocess.run([notepad, path])
  else:
    #Query default file viewer
    exp_query   = ["xdg-mime","query","default",mimetype]
    p           = subprocess.Popen(exp_query, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate("")
    notepad     = output.decode('utf-8').replace(".desktop\n","")
    subprocess.run([notepad, path])

#Thunar-specific file highlighting
def openFileThunar(path):
  return [
    "dbus-send",
    "--type=method_call",
    "--dest=org.xfce.Thunar",
    "/org/xfce/FileManager",
    "org.xfce.FileManager.DisplayFolderAndSelect",
    f"string:{ntpath.dirname(path)}",
    f"string:{ntpath.basename(path)}",
    "string:",
    "string:",
    ]

#Open folder (and optionally highlight a file in supported explorers)
def openDir(path,isfile=False):
  if os.name == 'nt':
    explorer = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
    if isfile and os.path.exists(path):
      subprocess.Popen([explorer, '/select,', path])
    else:
      subprocess.Popen([explorer, path])
  else:
    #Query default file explorer
    exp_query   = ["xdg-mime","query","default","inode/directory"]
    p           = subprocess.Popen(exp_query, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate("")
    explorer    = output.decode('utf-8').replace(".desktop\n","")
    if isfile and os.path.exists(path):
      if explorer in ["thunar"]:
        subprocess.Popen(openFileThunar(path))
      elif explorer in ["nautilus","nemo"]:
        subprocess.Popen([explorer, "no-desktop", path])
      else: #Explorer not supported; settle for opening directory
        subprocess.Popen([explorer, ntpath.dirname(path)])
    else:
      subprocess.Popen([explorer, path])

#Open a file selection dialog and return the path of the selected file
#DEPRECATED: use built-in file selection mechanisms now
def pickFile(prompt="Select a File",startDir=""):
  root = tk.Tk()
  root.withdraw()
  fname = tk.filedialog.askopenfilename(title=prompt,initialdir=ntpath.dirname(startDir))
  root.destroy()
  return fname
  # QtWidgets.QFileDialog.getOpenFileName()
  # return None
  # fp = os.path.join(current_app.config["INSTALL_FOLDER"],"app","filepicker.py")
  # print(fp)
  # return call(["python",fp,prompt,startDir])
  # return exec(open(fp).read())

#HTML escape a string
def htmlEscape(s):
  return (s
    .replace('&','&amp;' )
    .replace('"','&quot;')
    .replace("'",'&#39;' )
    .replace('<','&lt;'  )
    .replace('>','&gt;'  )
    )

#Convert Slippi UTC dates to local date
def localDate(d):
  is_dst     = time.daylight and time.localtime().tm_isdst > 0
  utc_offset = -(time.altzone if is_dst else time.timezone)
  return d+timedelta(seconds=utc_offset)

#Convert Slippi UTC timestamps to local timestamps
def localStamp(s,f="%Y-%m-%d_%H-%M-%S"):
  d        = datetime.strptime(s,f)
  newlocal = localDate(d)
  newstamp = newlocal.strftime(f)
  return newstamp

#Convert a frame number to a timestamp
def frame_to_timestamp(f):
  f -= 123
  m  = f//3600
  f -= m*3600
  s  = f//60
  f -= s*60
  c  = int(100*f/60.0)
  return f"{m}:{s:02d}.{c:02d}"
