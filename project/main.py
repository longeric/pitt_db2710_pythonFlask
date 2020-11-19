import datetime
import json

import peewee
from flask import (Blueprint, abort, current_app, flash, g, jsonify, redirect,
                   render_template, request, send_from_directory, url_for)
from flask_login import current_user, login_required
from playhouse import shortcuts

from . import models as db

main = Blueprint('main', __name__)


def modellist2dict(l):
    return [shortcuts.model_to_dict(i) for i in l]


@main.route('/', methods=['GET'])
def index():
    return redirect(url_for('main.game_list_page'))
    # return render_template('index.html')


@main.route('/images/<path:filename>')
def image_files(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main.route('/profile', methods=['GET'])
@login_required
def profile():
    return 'todo: profile or setting page'


@main.route('/game/list', methods=['GET'])
def game_list_page():
    sortby = request.args.get('sortby', '')
    search = request.args.get('search', '')
    print(search)
    games = db.Game.select(db.Game.id, db.Game.name, db.Game.type, db.Game.release_date, db.Game.platform,
                           db.Game.image, db.Game.price,
                           db.Game.hard_copy).order_by(db.Game.platform.desc())
    if search != '':
        games = games.where(db.Game.name.contains(search))
    if sortby == '':
        pass
    elif sortby == 'Price':
        games = games.order_by(db.Game.price.desc())
    elif sortby == 'Platform':
        games = games.order_by(db.Game.platform.desc())
    elif sortby == 'release_date':
        games = games.order_by(db.Game.release_date.desc())
    return render_template("gameList.html", gameList=list(games), games=modellist2dict(games))


@main.route('/game/show/<gameid>', methods=['GET'])
def game_page(gameid):
    try:
        game = db.Game.get_by_id(gameid)
        return "TODO: This is game detail page"
    except peewee.DoesNotExist as e:
        abort(404)
