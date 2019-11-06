#!/usr/bin/python
from flask import render_template, flash, redirect, url_for, request, current_app, jsonify
from werkzeug.urls import url_parse
from app import db
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from datetime import datetime
from app.main import bp
from app.main.forms import EditProfileForm, PostForm

import os, json

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

# @bp.route('/explore')
# @login_required
# def explore():
#     page = request.args.get('page', 1, type=int)
#     posts = Post.query.order_by(Post.timestamp.desc()).paginate(
#         page, current_app.config['POSTS_PER_PAGE'], False)
#     next_url = url_for('main.explore', page=posts.next_num) \
#         if posts.has_next else None
#     prev_url = url_for('main.explore', page=posts.prev_num) \
#         if posts.has_prev else None
#     return render_template("index.html.j2", title='Explore', posts=posts.items,
#                           next_url=next_url, prev_url=prev_url)

@bp.route('/research')
def research():
    # with open("/home/pretzel/downloads/console-input.js",'r') as fin:
    with open("/home/pretzel/workspace/slippc-viz/app/static/data/replays/Game_20191001T103257.slp.json",'r') as fin:
        lines = [fin.read()]#.split("\n")
    # lines = [""]
    return render_template("research.html.j2", entries=lines)

@bp.route('/cv')
def cv():
    return render_template("cv.html.j2")

@bp.route('/thing')
def thing():
    return render_template("json-test.html.j2")

@bp.route('/api/thing')
def thing_api():
    return jsonify({
        "Time": str(datetime.now()),
        })

@bp.route('/replays')
def replays():
    rdir      = os.path.join(current_app.config['STATIC_FOLDER'], "data/replays")
    rfiles    = os.listdir(rdir)
    replays   = []
    for r in sorted(rfiles,reverse=True)[:50]:
        rf = os.path.join(rdir,r)
        replays.append(load_replay(rf))
    return render_template("replays.html.j2", replays=replays)

@bp.route('/replays/<r>')
def replay_viz(r):
    rpath = os.path.join(current_app.config['STATIC_FOLDER'], "data/replays", r+".slp.json")
    replay = load_replay(rpath)
    return render_template("replays-single.html.j2", replays=[replay])

def load_replay(rf):
    with open(rf,'r') as jin:
        r                  = json.loads(jin.read())
        r["__file"]        = rf.split("/")[-1].split(".")[0]
        r["__act_length"]  = r["game_length"]-84
        r["__game_length"] = get_game_length(r["game_length"]-123)
        r["p"]             = r["players"]
        for p in r["p"]:
            for k,v in p["interactions"].items():
                p["int"+k] = v
            p["l_cancels_hit_pct"] = 0
            if p["l_cancels_hit"] > 0:
                p["l_cancels_hit_pct"] = 100 * p["l_cancels_hit"] / (p["l_cancels_hit"]+p["l_cancels_missed"])
            p["tech_hit_pct"] = 100
            if p["missed_techs"] > 0:
                p["tech_hit_pct"] = 100 * (p["techs"]+p["walltechs"]+p["walltechjumps"]) / (p["techs"]+p["walltechs"]+p["walltechjumps"]+p["missed_techs"])
            p["num_moves_landed"] = p["moves_landed"]["_total"]
            if p["tag_player"] == "":
                p["tag_player"] = "[CPU]" if p["player_type"] == 1 else "[Human]"
    return r

def get_game_length(frames):
    mins   = frames // 3600
    frames -= 3600*mins
    secs   = frames // 60
    frames -= 60*secs
    return f"{mins:02d}:{secs:02d}.{int((100*frames)/60):02d}"
