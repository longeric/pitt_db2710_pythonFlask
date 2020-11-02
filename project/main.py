import datetime
import json
import peewee
from flask_login import login_required, current_user
from playhouse import shortcuts
from . import models as db

from flask import Blueprint, request, g, render_template, redirect, url_for, flash, abort

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@main.route('/profile', methods=['GET'])
@login_required
def profile():
    return current_user.email


@main.route('/api/game/list', methods=['GET'])
def api_game_list():
    games = db.Game.select(db.Game.id, db.Game.name, db.Game.type, db.Game.release_date, db.Game.platform, db.Game.image, db.Game.hard_copy)
    return json.dumps(list(games.dicts()), default=str)


@main.route('/api/game/show/<gameid>', methods=['GET'])
def api_game_show(gameid):
    try:
        game = db.Game.get_by_id(gameid)
        return json.dumps(shortcuts.model_to_dict(game), default=str)
    except peewee.DoesNotExist as e:
        abort(404)



