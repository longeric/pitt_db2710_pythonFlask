import datetime
import json
import peewee
from flask_login import login_required, current_user
from playhouse import shortcuts
from . import models as db

from flask import Blueprint, request, g, render_template, redirect, url_for, flash, abort, jsonify

main = Blueprint('main', __name__)


@main.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@main.route('/profile', methods=['GET'])
@login_required
def profile():
    return 'todo: profile or setting page'


@main.route('/game/list', methods=['GET'])
def game_list_page():
    user = {}
    if current_user and not current_user.is_anonymous and current_user.is_authenticated:
        user['name'] = current_user.name
        user['email'] = current_user.email
        user['role'] = current_user.role
    games = db.Game.select(db.Game.id, db.Game.name, db.Game.type, db.Game.release_date, db.Game.platform,
                           db.Game.image, db.Game.price,
                           db.Game.hard_copy)
    print(user)
    return render_template("gameList.html", gameList=list(games), user=user)


@main.route('/game/show/<gameid>', methods=['GET'])
def game_page(gameid):
    try:
        game = db.Game.get_by_id(gameid)
        return "TODO: This is game detail page"
    except peewee.DoesNotExist as e:
        abort(404)

