import datetime
import json
import peewee
from flask_login import login_required, current_user
from playhouse import shortcuts
from . import models as db
from .import role_required

from flask import Blueprint, request, g, render_template, redirect, url_for, flash, abort, session, jsonify

cart = Blueprint('cart', __name__)


def valid_cart():
    if 'cart' not in session:
        session['cart'] = {}
    msg = []
    tobe_del = []
    for id in session['cart']:
        try:
            game = db.Game.get_by_id(id)
            if game.hard_copy < session['cart'][id]:
                session['cart'][id] = game.hard_copy
                session.modified = True
                msg.append((game.name, game.platform, game.hard_copy))
                if session['cart'][id] <= 0:
                    tobe_del.append(id)
        except peewee.DoesNotExist:
            tobe_del.append(id)
    for i in tobe_del:
        del session['cart'][i]
        session.modified = True

    return msg


def get_game_info(id, number):
    try:
        game = db.Game.get_by_id(id)
        return {
            "id": id,
            "name": game.name,
            "price": game.price,
            "image": game.image if game.image.startswith('http') else url_for('main.image_files', filename=game.image),
            "number": number
        }
    except:
        return {
            "id": id,
            "name": "N/A",
            "price": "N/A",
            "image": "#",
            "number": number
        }


@cart.route('/checkout', methods=['GET', 'POST'])
@role_required(['customer'])
def checkout():
    customer = db.Customer.get(db.Customer.account == current_user)

    cart_data = [get_game_info(id, number)
                 for id, number in session['cart'].items()]
    cart_data = [item for item in cart_data if item['name'] != "N/A"]
    if request.method == 'POST':
        customer.first_name = request.form['first_name']
        customer.last_name = request.form['last_name']
        customer.addr_country = request.form['addr_country']
        customer.addr_street = request.form['addr_street']
        customer.addr_city = request.form['addr_city']
        customer.addr_state = request.form['addr_state']
        customer.addr_zipcode = request.form['addr_zipcode']
        customer.phone = request.form['phone']
        customer.card_holder_name = request.form['card_holder_name']
        customer.card_number = request.form['card_number']
        customer.card_expire_at = request.form['card_expire_at']
        customer.card_cvv = request.form['cvv']
        customer.save()

        order = db.Order.create(
            customer=customer,
            datetime=datetime.datetime.now(),
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            addr_country=request.form['addr_country'],
            addr_street=request.form['addr_street'],
            addr_city=request.form['addr_city'],
            addr_state=request.form['addr_state'],
            addr_zipcode=request.form['addr_zipcode'],
            phone=request.form['phone'],
            card_holder_name=request.form['card_holder_name'],
            card_number=request.form['card_number'],
            card_expire_at=request.form['card_expire_at'],
            card_cvv=request.form['cvv']
        )

        order_status = db.OrderStatus.create(order=order, status="created", note="", datetime=datetime.datetime.now())

        for item in cart_data:
            db.OrderContains.create(
                order=order,
                game=item['id'],
                number=item['number'],
                per_price=item['price']
            )
            try:
                game = db.Game.get_by_id(item['id'])
                game.hard_copy = game.hard_copy - item['number']
                game.save()
            except peewee.DoesNotExist:
                pass
        session['cart'] = {}
        session.modified = True
        return redirect(url_for("main.profile", page="orderDetail", id=order.id))
    else:
        if not cart_data:
            flash("You don't have any items in your cart. ")
            return redirect(url_for("main.index"))
        total = sum(item['price']*item['number'] for item in cart_data)
        return render_template('checkout.html', data=cart_data, total=total, customer=customer)


@cart.route('/api/cart/add', methods=['POST'])
def add():
    form = request.form
    if not form:
        form = request.get_json()
    game = str(form.get('game'))
    number = int(form.get('number'))

    if 'cart' not in session:
        session['cart'] = {}
    if game not in session['cart']:
        session['cart'][game] = 0
    session['cart'][game] += number
    if number <= 0:
        del session['cart'][game]

    msg = valid_cart()
    session.modified = True

    return jsonify({'msg': '<br/>'.join(f"{i[0]}|{i[1]} only has {i[2]} in stock." for i in msg)})


@cart.route('/api/cart/set', methods=['POST'])
def set():
    form = request.form
    if not form:
        form = request.get_json()
    game = str(form.get('game'))
    number = int(form.get('number'))

    if 'cart' not in session:
        session['cart'] = {}
    session['cart'][game] = number
    if number <= 0:
        del session['cart'][game]

    msg = valid_cart()
    session.modified = True

    return jsonify({'msg': '<br/>'.join(f"{i[0]}|{i[1]} only has {i[2]} in stock." for i in msg)})


@cart.route('/api/cart/get', methods=['GET'])
def get():
    if 'cart' not in session:
        session['cart'] = {}

    msg = valid_cart()
    data = [get_game_info(id, number)
            for id, number in session['cart'].items()]

    return jsonify({
        'data': data,
        'msg': '<br/>'.join(f"{i[0]}|{i[1]} only has {i[2]} in stock." for i in msg)
    })


@cart.route('/api/cart/clear', methods=['GET'])
def clear():
    session['cart'] = {}
    session.modified = True

    return jsonify(session['cart'])
