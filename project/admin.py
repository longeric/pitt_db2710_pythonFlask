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


GameForm = model_form(db.Game, exclude=('release_date', 'image', 'hard_copy', 'alternate_images'))
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
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        ext = get_ext(file.filename)
        if ext not in ALLOWED_EXTENSIONS:
            flash('File type not allowed')
            return redirect(request.url)
        def save_image(file):
            unique_filename = '.'.join((str(uuid.uuid4()), ext))
            file.save(os.path.join(
                current_app.config['UPLOAD_FOLDER'], unique_filename))
            return unique_filename
        unique_filename = save_image(file)
        additional_files = []
        if request.files['file1'].filename != '':
            additional_files.append(save_image(request.files['file1']))
        if request.files['file2'].filename != '':
            additional_files.append(save_image(request.files['file2']))
        try:
            form = dict(**(request.form))
            form['image'] = unique_filename
            form['hard_copy'] = 0
            form['alternate_images'] = ';'.join(additional_files)
            game = db.Game.create(**form)
            return redirect(url_for('admin.game_list'))
        except db.IntegrityError:
            flash('DB conflict items')
            return redirect(request.url)
    else:
        form = GameForm()
        image_label = '<label for="file">Image</label>'
        image_input = '<input id="file" type="file" name="file" accept="image/png, image/jpeg, image/jpg" required>'
        
        add_image_label = '<label for="file1">Additional Image (optional)</label>'
        add_image_input = '<input id="file1" type="file" name="file1" accept="image/png, image/jpeg, image/jpg">'

        add_image_label2 = '<label for="file2">Additional Image (optional)</label>'
        add_image_input2 = '<input id="file2" type="file" name="file2" accept="image/png, image/jpeg, image/jpg">'

        date_label = '<label for="date">Release Date</label>'
        date_input = '<input type="date" id="date" name="release_date" required>'
        return render_template('adminEdit.html', form=form, additional=(
            (date_label, date_input),
            (image_label, image_input),
            (add_image_label, add_image_input),
            (add_image_label2, add_image_input2)
        ))


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
            print(type(supply.copies))
            supply.game.hard_copy += int(supply.copies)
            supply.game.save()
        except db.IntegrityError:
            flash('DB conflict items')
            return redirect(request.url)
        return redirect(url_for('admin.supply_history'))
    else:
        form = SupplyForm()
        return render_template('adminEdit.html', form=form)


@admin.route('/admin/trans/history', methods=['GET'])
@role_required(['admin', 'casher'])
def trans_history():
    trans = db.Transaction.select()
    d = trans.dicts()
    headers = []
    if d:
        for ti, di in zip(trans, d):
            di['email'] = ti.order.customer.account.email
        headers = list(d[0].keys())
    return render_template('adminTrans.html', headers=headers, content=d)


@admin.route('/admin/trans/refund', methods=['GET'])
@role_required(['admin', 'casher'])
def trans_refund():
    id = request.args.get('trans')
    trans = db.Transaction.get_by_id(id)
    ref = db.Transaction.select().where((db.Transaction.order == trans.order) & (db.Transaction.type == 'refund'))
    if len(ref) > 0:
        flash('already refund')
        return redirect(url_for('admin.trans_history'))
    d = shortcuts.model_to_dict(trans)
    del d['id']
    del d['order']
    d['order'] = trans.order
    d['type'] = 'refund'
    db.Transaction.create(**d)
    # Refund the customer
    return redirect(url_for('admin.trans_history'))


@admin.route('/admin/sales', methods=['GET'])
@role_required(['admin', 'casher'])
def sales_board():
    by = request.args.get('by', 'sum_qty')
    r = db.Game.select(
        db.Game.id, db.Game.name, peewee.fn.AVG(db.Game.price).alias('price_per_item'),
        peewee.fn.SUM(db.OrderContains.number).alias('sum_qty'),
        peewee.fn.SUM(db.OrderContains.number * db.OrderContains.per_price).alias('sum_price')
    ).join(db.OrderContains).group_by(db.Game.id).order_by(peewee.SQL(by).desc()).dicts()
    headers = []
    if r:
        headers = r[0].keys()
    return render_template('adminSaleBoard.html', headers=headers, content=r)


@admin.route('/admin/order/list', methods=['GET'])
@role_required(['admin', 'casher'])
def order_list():
    data = []
    for order in db.Order.select():
        item = {
            'id': order.id,
            'email': order.customer.account.email,
            'status': order.order_statuses.order_by(db.OrderStatus.datetime)[-1].status,
            'time': order.order_statuses.order_by(db.OrderStatus.datetime)[-1].datetime,
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
        if order.order_statuses.order_by(db.OrderStatus.datetime)[-1].status == 'delivered':
            cur = ''
        else:
            cur = sc[sc.index(order.order_statuses.order_by(db.OrderStatus.datetime)[-1].status) + 1]

        return render_template('adminOrderDetail.html', order=order, total=total, next_status=cur, db=db)
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
    try:
        order = db.Order.get_by_id(id)
        order_status = db.OrderStatus.create(order=order, status=status, note="", datetime=datetime.datetime.now())
        
        if status == 'shipped':
            total = sum((contains.per_price * contains.number) for contains in order.order_contains)
            db.Transaction.create(
                order=order, type='pay', amount=total,
                card_num=order.card_number, card_holder=order.card_holder_name,
                datetime=datetime.datetime.now(), note=''
            )
            # TODO: pay me the money!

        return redirect(url_for("admin.order_detail", id=id))
    except peewee.DoesNotExist:
        return abort(404)
