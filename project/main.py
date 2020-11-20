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
    # return render_template('index.html')
    return redirect(url_for('main.game_list_page'))


@main.route('/images/<path:filename>')
def image_files(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)


@main.route('/profile', methods=['GET'])
@login_required
def profile():
    customer = db.Customer.select().where(db.Customer.account == current_user.email)
    customer_id = list(customer.dicts())[0].get('id')
    page = request.args.get('page')
    detail = request.args.get('detail', '')
    if page == 'order':
        order_status = db.OrderStatus.select(db.Order.datetime, db.Order.game.alias('game'),
                                             db.OrderStatus.status, db.Order.id, db.OrderStatus.note,
                                             db.Order.addr_name, db.Order.addr_country, db.Order.addr_state,
                                             db.Order.addr_city, db.Order.addr_street, db.Order.addr_zipcode) \
            .join(db.Order, on=(db.Order.datetime == db.OrderStatus.datetime)) \
            .where(db.Order.customer == customer_id).alias('order_status')

        if detail == '':
            customer_order = db.Game.select(order_status.c.datetime,
                                            peewee.fn.Count(order_status.c.id).alias('quantity'),
                                            peewee.fn.Sum(db.Game.price).alias("amount"), order_status.c.status) \
                .join(order_status, on=(order_status.c.game == db.Game.id)) \
                .group_by(order_status.c.datetime).order_by(order_status.c.datetime.desc())

            return render_template("order.html", orderList=list(customer_order.dicts()), info='Order')
        else:
            customer_order_detail = db.Game.select(order_status.c.datetime, order_status.c.note,
                                                   order_status.c.addr_name, order_status.c.addr_country,
                                                   order_status.c.addr_state, order_status.c.addr_city,
                                                   order_status.c.addr_street, order_status.c.addr_zipcode,
                                                   peewee.fn.Count(order_status.c.game).alias('quantity'),
                                                   order_status.c.status, peewee.fn.Sum(db.Game.price).alias('price'),
                                                   db.Game.name) \
                .join(order_status, on=(order_status.c.game == db.Game.id)) \
                .where(order_status.c.datetime == detail) \
                .group_by(order_status.c.game)
            return render_template("order.html", orderDetailList=list(customer_order_detail.dicts()),
                                   info='Order Detail')
    else:
        return render_template("profile.html", c=list(customer.dicts())[0])



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
