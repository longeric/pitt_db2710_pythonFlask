import datetime
import json
import os
import uuid

import peewee
import wtforms
from flask import (Blueprint, abort, current_app, flash, g, jsonify, redirect,
                   render_template, request, session, url_for)
from flask_login import current_user, login_required
from playhouse import shortcuts
from werkzeug.utils import secure_filename
from wtfpeewee.fields import ModelHiddenField
from wtfpeewee.orm import ModelConverter, model_form

from . import models as db
from . import role_required

admin = Blueprint('admin', __name__)


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


def get_ext(filename):
    if '.' in filename:
        return secure_filename(filename.rsplit('.', 1)[1].lower())
    else:
        return ''


class MyForeignKeyConverter(ModelConverter):
    def handle_foreign_key(self, model, field, **kwargs):
        def func(x):
            if isinstance(x, db.Game):
                return ' | '.join((x.name, str(x.id), x.platform))
            elif isinstance(x, db.Supplier):
                return ' | '.join((x.name, str(x.id), x.email))
            else:
                return str(x)
        kwargs['get_label'] = func
        return super().handle_foreign_key(model, field, **kwargs)


GameForm = model_form(db.Game, exclude=('release_date', 'image', 'hard_copy'))
SupplierForm = model_form(db.Supplier)
SupplyForm = model_form(db.Supply, exclude=(
    'date',), converter=MyForeignKeyConverter())


@admin.route('/admin/game/list', methods=['GET'])
@role_required(['admin', 'supplier'])
def game_list():
    games = db.Game.select(db.Game.id, db.Game.name, db.Game.type, db.Game.release_date, db.Game.platform,
                           db.Game.price, db.Game.hard_copy).dicts()
    headers = []
    if games:
        headers = list(games[0].keys())
    return render_template('adminTable.html', headers=headers, content=games)


@admin.route('/admin/game/add', methods=['GET', 'POST'])
@role_required(['admin', 'supplier'])
def game_add():
    if request.method == 'POST':
        print(request.files)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        ext = get_ext(file.filename)
        if ext in ALLOWED_EXTENSIONS:
            unique_filename = '.'.join((str(uuid.uuid4()), ext))
            file.save(os.path.join(
                current_app.config['UPLOAD_FOLDER'], unique_filename))
            try:
                form = dict(**(request.form))
                form['image'] = unique_filename
                form['hard_copy'] = 0
                game = db.Game.create(**form)
                return redirect(url_for('admin.game_list'))
            except db.IntegrityError:
                flash('DB conflict items')
                return redirect(request.url)
        else:
            flash('File type not allowed')
            return redirect(request.url)
    else:
        form = GameForm()
        image_label = '<label for="file">Image</label>'
        image_input = '<input id="file" type="file" name="file" required>'

        date_label = '<label for="date">Release Date</label>'
        date_input = '<input type="date" id="date" name="release_date" required>'
        return render_template('adminEdit.html', form=form, additional=((date_label, date_input), (image_label, image_input)))


@admin.route('/admin/supplier/list', methods=['GET'])
@role_required(['admin', 'supplier'])
def supplier_list():
    suppliers = db.Supplier.select(
        db.Supplier.id, db.Supplier.name, db.Supplier.email, db.Supplier.phone).dicts()
    headers = []
    if suppliers:
        headers = list(suppliers[0].keys())
    return render_template('adminTable.html', headers=headers, content=suppliers)


@admin.route('/admin/supplier/add', methods=['GET', 'POST'])
@role_required(['admin', 'supplier'])
def supplier_add():
    if request.method == 'POST':
        try:
            supplier = db.Supplier.create(**(request.form))
        except db.IntegrityError:
            flash('DB conflict items')
            return redirect(request.url)
        return redirect(url_for('admin.supplier_list'))
    else:
        form = SupplierForm()
        return render_template('adminEdit.html', form=form)


@admin.route('/admin/supply/history', methods=['GET'])
@role_required(['admin', 'supplier'])
def supply_history():
    supplies = db.Supply.select().dicts()
    headers = []
    if supplies:
        headers = list(supplies[0].keys())
    return render_template('adminTable.html', headers=headers, content=supplies)


@admin.route('/admin/supply/add', methods=['GET', 'POST'])
@role_required(['admin', 'supplier'])
def supply_add():
    if request.method == 'POST':
        try:
            form = dict(**(request.form))
            form['date'] = datetime.datetime.today()
            supply = db.Supply.create(**(form))
        except db.IntegrityError:
            flash('DB conflict items')
            return redirect(request.url)
        return redirect(url_for('admin.supply_history'))
    else:
        form = SupplyForm()
        return render_template('adminEdit.html', form=form)


@admin.route('/admin/order/list', methods=['GET'])
@role_required(['admin', 'casher'])
def order_list():
    data = []
    for order in db.Order.select():
        item = {
            'id': order.id,
            'email': order.customer.account.email,
            'status': order.order_statuses[-1].status,
            'time': order.order_statuses[-1].datetime,
            'pay': 0
        }
        for contains in order.order_contains:
            item['pay'] += (contains.per_price * contains.number)
        data.append(item)

    return render_template('adminOrder.html', headers=['id', 'email', 'status', 'time', 'pay'], content=data)


@admin.route('/admin/order/show/<id>', methods=['GET'])
@role_required(['admin', 'casher'])
def order_detail(id):
    sc = ('created', 'shipped', 'delivered')
    try:
        order = db.Order.get_by_id(id)
        total = sum((contains.per_price * contains.number) for contains in order.order_contains)
        if order.order_statuses[-1].status == 'delivered':
            cur = ''
        else:
            cur = sc[sc.index(order.order_statuses[-1].status) + 1]

        return render_template('adminOrderDetail.html', order=order, total=total, next_status=cur)
    except peewee.DoesNotExist:
        return abort(404)


@admin.route('/admin/order/change', methods=['POST'])
@role_required(['admin', 'casher'])
def order_change():
    sc = ('created', 'shipped', 'delivered')
    status = request.form['status']
    id = request.form['id']

    if status not in sc:
        return abort(404)
    if status == 'shipped':
        pass
        # TODO: pay me the money!
    try:
        order = db.Order.get_by_id(id)
        order_status = db.OrderStatus.create(order=order, status=status, note="", datetime=datetime.datetime.now())

        return redirect(url_for("admin.order_detail", id=id))
    except peewee.DoesNotExist:
        return abort(404)
