import datetime
import json
import peewee
from flask_login import login_required, current_user
from playhouse import shortcuts
from . import models as db

from flask import Blueprint, request, g, render_template, redirect, url_for, flash, abort, session, jsonify

cart = Blueprint('cart', __name__)

### Sample js post
# var xhr = new XMLHttpRequest();
# xhr.open("POST", "api/cart/set", true);
# xhr.setRequestHeader('Content-Type', 'application/json');
# xhr.send(JSON.stringify({
#     game: 3,
#     number: 0	
# }));


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

    session.modified = True

    return 'ok'


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

    session.modified = True

    return 'ok'

@cart.route('/api/cart/get', methods=['GET'])
def get():
    def get_obj(id, number):
        try:
            game = db.Game.get_by_id(id)
            return {
                "id": id,
                "name": game.name + ' | ' + game.platform,
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

    if 'cart' not in session:
        session['cart'] = {}
    
    data = [get_obj(id, number) for id, number in session['cart'].items()]

    return jsonify(data)


@cart.route('/api/cart/simple', methods=['GET'])
def simple():
    if 'cart' not in session:
        session['cart'] = {}

    return jsonify(session['cart'])


@cart.route('/api/cart/clear', methods=['GET'])
def clear():
    session['cart'] = {}
    session.modified = True

    return jsonify(session['cart'])

