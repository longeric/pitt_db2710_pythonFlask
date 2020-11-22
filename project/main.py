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
@login_required
@role_required(['customer'])
def profile():
    customer = db.Customer.select().where(db.Customer.account == current_user.email)
    customer_id = list(customer.dicts())[0].get('id')
    page = request.args.get('page')
    detail = request.args.get('detail', '')
    if page == 'order':
        order_info = db.Order.select(db.Order.datetime, db.Order.id.alias('order_id'),
                                     db.OrderContains.game.alias('game'),
                                     db.Order.addr_name, db.Order.addr_country, db.Order.addr_state,
                                     db.Order.addr_city, db.Order.addr_street, db.Order.addr_zipcode,
                                     db.OrderContains.number, db.OrderContains.per_price) \
            .join(db.OrderContains) \
            .where(db.Order.customer == customer_id).alias('order_info')

        if detail == '':
            customer_order = db.Game.select(order_info.c.datetime, order_info.c.game, order_info.c.order_id,
                                            peewee.fn.Sum(order_info.c.number).alias('quantity'),
                                            peewee.fn.Sum(order_info.c.number * order_info.c.per_price).alias(
                                                "amount")) \
                .join(order_info, on=(order_info.c.game == db.Game.id)) \
                .group_by(order_info.c.order_id).order_by(order_info.c.datetime.desc())

            return render_template("order.html", orderList=list(customer_order.dicts()), info='Order')
        else:
            order_detail = db.Game.select(order_info.c.datetime, db.Game.platform,
                                          order_info.c.addr_name, order_info.c.addr_country,
                                          order_info.c.addr_state, order_info.c.addr_city,
                                          order_info.c.addr_street, order_info.c.addr_zipcode,
                                          order_info.c.number.alias('quantity'), db.Game.name,
                                          (order_info.c.number * order_info.c.per_price).alias('price')) \
                .join(order_info, on=(order_info.c.game == db.Game.id)) \
                .where(order_info.c.order_id == detail) \
                .group_by(order_info.c.game).order_by(order_info.c.datetime.asc())
            order_status = db.Order.select(db.OrderStatus.note, db.OrderStatus.datetime, db.OrderStatus.status) \
                .join(db.OrderStatus).where(db.Order.id == detail).order_by(db.OrderStatus.datetime.desc())
            return render_template("order.html", q=request.args.get('q', ''), a=request.args.get('a', ''),
                                   orderDetailList=list(order_detail.dicts()), info='Order Detail',
                                   orderStatusList=list(order_status.dicts()))
    else:
        return render_template("profile.html", c=list(customer.dicts())[0])


@main.route('/profile', methods=['POST'])
@login_required
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
