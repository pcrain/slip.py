#!/usr/bin/python
from werkzeug.security        import generate_password_hash, check_password_hash
from datetime                 import datetime
from app                      import db, login, cache
from app.config               import Config
from flask_login              import UserMixin, AnonymousUserMixin
from sqlalchemy               import or_, and_, event
# from flask_sqlalchemy_caching import FromCache
import sys, os

class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.username = 'Guest'
    self.id       = -1

  def all_replays(self):
    pubs = Replay.query.filter_by(is_public=1)
    pubs = pubs.order_by(Replay.played.desc())
    pubs = pubs.group_by(Replay.checksum)
    # pubs = pubs.options(FromCache(cache))
    return pubs
    # return pubs.order_by(Replay.uploaded.desc())

login.anonymous_user = Anonymous

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), index=True, unique=True)
    email         = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    replays       = db.relationship('Replay', backref='uploader', lazy='dynamic')
    last_seen     = db.Column(db.DateTime, default=datetime.utcnow)
    # followed      = db.relationship(
    #     'User', secondary=followers,
    #     primaryjoin=(followers.c.follower_id == id),
    #     secondaryjoin=(followers.c.followed_id == id),
    #     backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def all_replays(self):
        reps = Replay.query.filter_by(user_id=self.id)
        pubs = Replay.query.filter_by(is_public=1)
        return reps.union(pubs).order_by(Replay.uploaded.desc())

class Settings(db.Model):
    name  = db.Column(db.String(128), primary_key=True)
    type_ = db.Column(db.String(16))
    value = db.Column(db.String(128))

    def asDict():
        casts = {
          "str"  : lambda x: str(x),
          "int"  : lambda x: int(x),
          "num"  : lambda x: float(x),
          "bool" : lambda x: True if "True" in x else False,
          }
        return { d.name : casts[d.type_](d.value) for d in Settings.query.all() }

    def load():
      d = Settings.asDict()
      if not "appversion" in d:
        if not "autoscan" in d: #Hack to check if we are on a version of the app before version numbers exist
          db.session.add(Settings(name="appversion", type_="str",value=Config.SITE_VERSION))
          db.session.commit()
        else:
          print("OLD VERSION")
      if not "isopath" in d:
          db.session.add(Settings(name="isopath",    type_="str" ,value=""))
      if not "emupath" in d:
        if os.name == "nt": #Set default Playback dolphin path to bundled Dolphin
          db.session.add(Settings(name="emupath",    type_="str" ,value=os.path.join(Config.INSTALL_FOLDER,"playback-dolphin","Dolphin.exe")))
        else:
          db.session.add(Settings(name="emupath",    type_="str" ,value=""))
      if not "scanthreads" in d:
          db.session.add(Settings(name="scanthreads",type_="int" ,value=str(max(1,Config.MAX_SCAN_THREADS//2))))
      if not "autoscan" in d:
          db.session.add(Settings(name="autoscan",   type_="bool",value="False"))
          db.session.commit()
      d = Settings.asDict()
      return d

class ScanDir(db.Model):
    fullpath  = db.Column(db.String(), primary_key=True)
    display   = db.Column(db.String(), index=True)
    path      = db.Column(db.String(), index=True)
    lastscan  = db.Column(db.String(19))

@event.listens_for(ScanDir.__table__, 'after_create')
def insert_initial_values(*args, **kwargs):
    #Add default replay folder on startup
    if os.path.exists(Config.DEF_REPLAY_FOLDER):
        db.session.add(ScanDir(
          fullpath = Config.DEF_REPLAY_FOLDER,
          display  = os.path.basename(Config.DEF_REPLAY_FOLDER),
          path     = os.path.dirname(Config.DEF_REPLAY_FOLDER),
          lastscan = "2000-01-01_00-00-00",
          ))
        db.session.commit()


class Replay(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    checksum   = db.Column(db.String(32))
    filename   = db.Column(db.String())
    filedir    = db.Column(db.String())
    filesize   = db.Column(db.Integer)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), default=-1)
    played     = db.Column(db.String(19), index=True)
    uploaded   = db.Column(db.String(19), index=True)
    is_public  = db.Column(db.Boolean, default=True)

    frames     = db.Column(db.Integer)
    p1char     = db.Column(db.Integer)
    p1color    = db.Column(db.Integer)
    p1stocks   = db.Column(db.Integer)
    p1metatag  = db.Column(db.String(128))
    p1csstag   = db.Column(db.String(8))
    p1codetag  = db.Column(db.String(8))
    p1display  = db.Column(db.String(128))
    p2char     = db.Column(db.Integer)
    p2color    = db.Column(db.Integer)
    p2stocks   = db.Column(db.Integer)
    p2metatag  = db.Column(db.String(128))
    p2csstag   = db.Column(db.String(8))
    p2codetag  = db.Column(db.String(8))
    p2display  = db.Column(db.String(128))
    stage      = db.Column(db.Integer)

    #0.7.0 additions
    winner     = db.Column(db.Integer,  default=-1)
    timer      = db.Column(db.Integer,  default=480)
    p1bstocks  = db.Column(db.Integer,  default=4)
    p2bstocks  = db.Column(db.Integer,  default=4)
    p1_stats   = db.Column(db.Boolean,  default=False) #Future tracking for if stats are cached
    p2_stats   = db.Column(db.Boolean,  default=False) #Future tracking for if stats are cached
    game_flags = db.Column(db.Integer,  default=0) #Future tourney legal / item flags
    p1punish   = db.Column(db.Float,    default=-1)
    p1defense  = db.Column(db.Float,    default=-1)
    p1neutral  = db.Column(db.Float,    default=-1)
    p1speed    = db.Column(db.Float,    default=-1)
    p1control  = db.Column(db.Float,    default=-1)
    p1accuracy = db.Column(db.Float,    default=-1)
    p2punish   = db.Column(db.Float,    default=-1)
    p2defense  = db.Column(db.Float,    default=-1)
    p2neutral  = db.Column(db.Float,    default=-1)
    p2speed    = db.Column(db.Float,    default=-1)
    p2control  = db.Column(db.Float,    default=-1)
    p2accuracy = db.Column(db.Float,    default=-1)
    ver_slippi = db.Column(db.String(8),default="") #slippi version
    ver_stats  = db.Column(db.String(8),default="") #slippc analyzer version
    ver_viz    = db.Column(db.String(8),default=Config.SITE_VERSION) #slip.py browser version

    def search(args):
        query     = args.get("query","")
        p1char    = int(args.get("p1char",  -1))
        p2char    = int(args.get("p2char",  -1))
        p1cost    = int(args.get("p1cost",  -1))
        p2cost    = int(args.get("p2cost",  -1))
        stage     = int(args.get("stage",   -1))
        path      = str(args.get("path",    ""))

        p1stock   = str(args.get("p1stock",   ""))
        p2stock   = str(args.get("p2stock",   ""))
        minframes = int(args.get("lengthmin", -1))
        maxframes = int(args.get("lengthmax", -1))

        q         = Replay.query

        p1clauses = []
        p2clauses = []
        p1alts    = []
        p2alts    = []

        #TODO: canonicalize database entries so we don't have to check both ways for p1 / p2 searches
        if p1char >= 0:
            p1clauses.append((Replay.p1char == p1char))
            p2clauses.append((Replay.p2char == p1char))
            if p1cost >= 0:
                p1clauses.append((Replay.p1color == p1cost))
                p2clauses.append((Replay.p2color == p1cost))
        if p1stock != "":
            if "lt" in p1stock:
                p1clauses.append((Replay.p1stocks < int(p1stock[2:])))
                p2clauses.append((Replay.p2stocks < int(p1stock[2:])))
            elif "gt" in p1stock:
                p1clauses.append((Replay.p1stocks > int(p1stock[2:])))
                p2clauses.append((Replay.p2stocks > int(p1stock[2:])))
            elif p1stock != "-1":
                p1clauses.append((Replay.p1stocks == int(p1stock)))
                p2clauses.append((Replay.p2stocks == int(p1stock)))
        if p2char >= 0:
            p1alts.append((Replay.p1char == p2char))
            p2alts.append((Replay.p2char == p2char))
            if p2cost >= 0:
                p1alts.append((Replay.p1color == p2cost))
                p2alts.append((Replay.p2color == p2cost))
        if p2stock != "":
            if "lt" in p2stock:
                p1alts.append((Replay.p1stocks < int(p2stock[2:])))
                p2alts.append((Replay.p2stocks < int(p2stock[2:])))
            elif "gt" in p2stock:
                p1alts.append((Replay.p1stocks > int(p2stock[2:])))
                p2alts.append((Replay.p2stocks > int(p2stock[2:])))
            elif p2stock != "-1":
                p1alts.append((Replay.p1stocks == int(p2stock)))
                p2alts.append((Replay.p2stocks == int(p2stock)))
        if minframes >= 0:
            q = q.filter(Replay.frames >= minframes)
        if maxframes >= 0:
            q = q.filter(Replay.frames <= maxframes)

        if len(p1clauses) > 0 or len(p1alts) > 0:
            q = q.filter(or_(and_(*p1clauses,*p2alts),and_(*p2clauses,*p1alts)))

        if stage >= 0:
            q = q.filter(Replay.stage == stage)

        for term in query.split(" "):
            t = "%{}%".format(term)
            q = q.filter(or_(
                Replay.filename.like(t),
                Replay.p1metatag.like(t),
                Replay.p2metatag.like(t),
                Replay.p1csstag.like(t),
                Replay.p2csstag.like(t),
                Replay.p1codetag.like(t),
                Replay.p2codetag.like(t),
                ))

        if path != "":
            q = q.filter(Replay.filedir.like(path))

        if args.get("sort","play") == "upload":
            q = q.order_by(Replay.uploaded.desc())
        else:
            q = q.order_by(Replay.played.desc())

        q = q.group_by(Replay.checksum)

        # q = q.options(FromCache(cache))

        return q

    def __repr__(self):
        return '<Replay {} [{}]>'.format(self.filename, self.checksum)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

