import datetime
import peewee
import demo_db as db

from flask import Flask, request, g, render_template, redirect, url_for, flash
from markupsafe import escape

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]kdlshfieo12'

@app.before_request
def before_request():
    g.db = db.database
    g.db.connect()

@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def home_page():
    return render_template("home.html")

@app.route('/hello')
def hello():
    return 'Hello!'

@app.route('/shops/showall')
def shops():
    return render_template("shoplist.html", shop_list=db.Shop.select())

@app.route('/shops/show/<shopname>')
def show_shop(shopname):
    try:
        shop = db.Shop.get(db.Shop.name == shopname)
        return render_template("shopdetail.html", name='Home page of shop {}'.format(escape(shopname)), created_at=shop.create_at)
    except:
        # todo
        flash("Error")
    return redirect(url_for('home_page'))

@app.route('/shops/add', methods=['GET', 'POST'])
def add_shop():
    if request.method == 'POST' and request.form['name']:
        try:
            db.Shop.create(name=request.form['name'], create_at=datetime.date.today())
            return redirect(url_for('shops'))
        except peewee.IntegrityError:
            # todo
            flash("Error")
    return render_template("shopadd.html")

