#!/usr/bin/python
from flask import current_app
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
    return datetime.strptime(t, "%Y-%m-%dT%H:%M:%S")
  except:
    return datetime.strptime("2000-01-01T00:00:00", "%Y-%m-%dT%H:%M:%S")

#Recursively list slippi files in directory
def get_all_slippi_files(topdir,files):
  for f in os.listdir(topdir):
    path = os.path.join(topdir,f)
    if os.path.isfile(path) and path[-4:] == ".slp":
      files.append(path)
    elif os.path.isdir(path):
      get_all_slippi_files(path,files)
