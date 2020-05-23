#!/usr/bin/python
from flask import current_app
from datetime import datetime
import os, json, sys, subprocess, shlex, hashlib, stat, ntpath, gzip, ctypes

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
  p = subprocess.Popen(coms, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output, err = p.communicate(inp.encode("utf-8"))
  oc = output.decode('utf-8',errors='replace' if ignoreErrors else 'strict')
  return (oc,err.decode('utf-8')) if returnErrors else oc

#Call a process and return its output using shell syntax
def shcall(comstring,inp="",ignoreErrors=False,returnErrors=False):
  return call(shlex.split(comstring),inp,ignoreErrors,returnErrors)

def load_replay(rf):
    with open(rf,'r') as jin:
        r                  = json.loads(jin.read())
        r["__file"]        = rf.split("/")[-1].split(".")[0]
        r["__act_length"]  = r["game_length"]-84
        r["__game_length"] = get_game_length(r["game_length"]-123)
        r["p"]             = r["players"]
        for p in r["p"]:
            for k,v in p["interaction_frames"].items():
                p["__int"+k] = v
            for k,v in p["interaction_damage"].items():
                p["__dmg"+k] = v
            p["__l_cancels_hit_pct"] = 0
            if p["l_cancels_hit"] > 0:
                p["__l_cancels_hit_pct"] = 100 * p["l_cancels_hit"] / (p["l_cancels_hit"]+p["l_cancels_missed"])
            p["__tech_hit_pct"] = 100
            if p["missed_techs"] > 0:
                p["__tech_hit_pct"] = 100 * (p["techs"]+p["walltechs"]+p["walltechjumps"]) / (p["techs"]+p["walltechs"]+p["walltechjumps"]+p["missed_techs"])
            p["num_moves_landed"] = p["moves_landed"]["_total"]
            p["__display_tag"] = get_display_tag(p)
    return r

def get_display_tag(p):
    if p["tag_player"] == "" or p["tag_player"] == "Player":
        if p["player_type"] == 1:
            return "[Lv. {} CPU]".format(p["cpu_level"])
        if p["tag_css"].strip() != "" :
            return "[{}]".format(p["tag_css"].strip().upper())
        return "[Port {}]".format(1+p["port"])
    return p["tag_player"]

def get_game_length(frames):
    mins   = frames // 3600
    frames -= 3600*mins
    secs   = frames // 60
    frames -= 60*secs
    return f"{mins:02d}:{secs:02d}.{int((100*frames)/60):02d}"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ["slp"]

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
    if os.path.isfile(path) and path[-4:] == ".slp":
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
    return False
    return bool(os.stat(filepath).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)

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
      "class" : "updir",
      "click" : "travel",
      "sort"  : 1,
      })
    c = count_slippi_files(path)
    ddata.append({
      "name"  : "Add "+path,
      "path"  : path,
      "dirs"  : c["dirs"],
      "files" : c["files"],
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
  if not os.path.exists(p) and (indb or (not os.path.islink(p))):
    return {
      "name"  : base,
      "path"  : p,
      "dirs"  : 0,
      "files" : 0,
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
        "class" : classd,
        "click" : "travel" if click is None else click,
        "sort"  : 4,
      }
  return None

#Count slippi files / subdirectories at a path
def count_slippi_files(path):
  ndirs  = 0
  nfiles = 0
  try:
    if os.access(path, os.R_OK) and os.access(path, os.W_OK):
      for f in os.listdir(path):
        s = os.path.join(path,f)
        if os.path.isdir(s) and os.access(s, os.R_OK) and (not is_hidden(s)):
            ndirs += 1
        elif f[-4:] == ".slp":
            nfiles += 1
    return {"dirs" : ndirs, "files" : nfiles}
  except PermissionError:
    return {"dirs" : ndirs, "files" : nfiles}

#Compress writing example
def compressedJsonWrite(data,filename):
  with gzip.GzipFile(filename, 'w') as fout:
    fout.write(json.dumps(data).encode('utf-8'))

#Compress reading example
def compressedJsonRead(filename):
  with gzip.GzipFile(filename, 'r') as fin:
    return json.loads(fin.read().decode('utf-8'))
