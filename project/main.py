import datetime
import json

import peewee
from flask import (Blueprint, abort, current_app, flash, g, jsonify, redirect,
                   render_template, request, send_from_directory, url_for)
from flask_login import current_user, login_required
from playhouse import shortcuts

from . import models as db, role_required

main = Blueprint('main', __name__)


def modellist2dict(l):
    return [shortcuts.model_to_dict(i) for i in l]


@main.route('/', methods=['GET'])
def index():
    # return render_template('index.html')
    return redirect(url_for('main.game_list_page'))


@main.route('/images/<path:filename>')
def image_files(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main.route('/profile', methods=['GET'])
@role_required(['customer'])
def profile():
    page = request.args.get('page')
    if page == 'orderList':
        customer_orders = db.Order.select().where(db.Order.customer == current_user.customer[0])
        return render_template("order.html", orderList=customer_orders, info='Order')
    elif page == 'orderDetail':
            order = db.Order.get_by_id(request.args.get('id'))
            total = sum((contain.number*contain.per_price) for contain in order.order_contains)
            return render_template("order.html", order=order, info='Order Detail', total=total)
    else:
        return render_template("profile.html", c=db.Order.customer)


@main.route('/profile', methods=['POST'])
@role_required(['customer'])
def profile_post():
    account = db.Account.get(db.Account.email == current_user)
    account.name = request.form.get('name')
    account.save()

    customer = db.Customer.get(db.Customer.account == current_user)
    customer.phone = request.form.get('phone')
    customer.first_name = request.form.get('first_name')
    customer.last_name = request.form.get('last_name')
    customer.card_number = request.form.get('card_number')
    customer.card_expire_at = request.form.get('card_expire_at')
    customer.card_holder_name = request.form.get('card_holder_name')
    customer.addr_country = request.form.get('addr_country')
    customer.addr_state = request.form.get('addr_state')
    customer.addr_city = request.form.get('addr_city')
    customer.addr_zipcode = request.form.get('addr_zipcode')
    customer.addr_street = request.form.get('addr_street')
    customer.save()

    return redirect(url_for('main.profile'))


@main.route('/game/list', methods=['GET'])
def game_list_page():
    sortby = request.args.get('sortby', '')
    search = request.args.get('search', '')
    print(search)
    games = db.Game.select(db.Game.id, db.Game.name, db.Game.type, db.Game.release_date, db.Game.platform,
                           db.Game.image, db.Game.price,
                           db.Game.hard_copy).where(db.Game.hard_copy > 0).order_by(db.Game.platform.desc())
    if search:
        games = games.where(db.Game.name.contains(search))
    if sortby == 'Price':
        games = games.order_by(db.Game.price.desc())
    elif sortby == 'Platform':
        games = games.order_by(db.Game.platform.desc())
    elif sortby == 'release_date':
        games = games.order_by(db.Game.release_date.desc())
    return render_template("gameList.html", gameList=list(games), games=modellist2dict(games))


@main.route('/game/show', methods=['GET'])
def game_page():
    try:
        print(request.args)
        game_id = request.args.get('gameid')
        game = db.Game.get_by_id(game_id)	
        return render_template("gameDetail.html", game=game)
    except peewee.DoesNotExist as e:
        return abort(404)
