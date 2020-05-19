#!/usr/bin/python
from werkzeug.security import generate_password_hash, check_password_hash
from datetime          import datetime
from app               import db, login
from flask_login       import UserMixin, AnonymousUserMixin
from hashlib           import md5
from sqlalchemy        import or_, and_
import sys

class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.username = 'Guest'
    self.id       = -1

  def all_replays(self):
    pubs = Replay.query.filter_by(is_public=1)
    return pubs.order_by(Replay.played.desc())
    # return pubs.order_by(Replay.uploaded.desc())

login.anonymous_user = Anonymous

class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), index=True, unique=True)
    email         = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    replays       = db.relationship('Replay', backref='uploader', lazy='dynamic')
    # about_me      = db.Column(db.String(2000))
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

    # def avatar(self, size):
    #     digest = md5(self.email.lower().encode('utf-8')).hexdigest()
    #     return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
    #         digest, size)

    # def follow(self, user):
    #     if not self.is_following(user):
    #         self.followed.append(user)

    # def unfollow(self, user):
    #     if self.is_following(user):
    #         self.followed.remove(user)

    # def is_following(self, user):
    #     return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(followers, (followers.c.followed_id == Post.user_id)
            ).filter(followers.c.follower_id == self.id)
        own      = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def all_replays(self):
        reps = Replay.query.filter_by(user_id=self.id)
        pubs = Replay.query.filter_by(is_public=1)
        return reps.union(pubs).order_by(Replay.uploaded.desc())

class Replay(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    checksum  = db.Column(db.String(32))
    filename  = db.Column(db.String(128))
    filedir   = db.Column(db.String(128))
    user_id   = db.Column(db.Integer, db.ForeignKey('user.id'), default=-1)
    played    = db.Column(db.DateTime, index=True)
    uploaded  = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)

    p1char    = db.Column(db.Integer)
    p1color   = db.Column(db.Integer)
    p1stocks  = db.Column(db.Integer)
    p1metatag = db.Column(db.String(128))
    p1csstag  = db.Column(db.String(8))
    p1display = db.Column(db.String(128))
    p2char    = db.Column(db.Integer)
    p2color   = db.Column(db.Integer)
    p2stocks  = db.Column(db.Integer)
    p2metatag = db.Column(db.String(128))
    p2csstag  = db.Column(db.String(8))
    p2display = db.Column(db.String(128))
    stage     = db.Column(db.Integer)

    def search(args):
        query     = args.get("query","")
        p1char    = int(args.get("p1char",  -1))
        p2char    = int(args.get("p2char",  -1))
        p1cost    = int(args.get("p1cost",  -1))
        p2cost    = int(args.get("p2cost",  -1))
        p1stock   = int(args.get("p1stock", -1))
        p2stock   = int(args.get("p2stock", -1))
        stage     = int(args.get("stage",   -1))
        path      = str(args.get("path",    ""))

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
        if p1stock >= 0:
            p1clauses.append((Replay.p1stocks == p1stock))
            p2clauses.append((Replay.p2stocks == p1stock))
        if p2char >= 0:
            p1alts.append((Replay.p1char == p2char))
            p2alts.append((Replay.p2char == p2char))
            if p2cost >= 0:
                p1alts.append((Replay.p1color == p2cost))
                p2alts.append((Replay.p2color == p2cost))
        if p2stock >= 0:
            p1alts.append((Replay.p1stocks == p2stock))
            p2alts.append((Replay.p2stocks == p2stock))

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
                ))

        if path != "":
            q = q.filter(Replay.filedir.like("/local/"+path))

        if args.get("sort","play") == "upload":
            q = q.order_by(Replay.uploaded.desc())
        else:
            q = q.order_by(Replay.played.desc())

        # sys.stderr.write(str(q))
        return q

    def __repr__(self):
        return '<Replay {} [{}]>'.format(self.filename, self.checksum)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))