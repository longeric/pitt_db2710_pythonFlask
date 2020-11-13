from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from . import models as db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False
    next_url = request.form.get("next")

    try:
        user = db.Account.get(db.Account.email == email)
        
        if not check_password_hash(user.password, password): 
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

        if not login_user(user, remember=remember):
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))
        if next_url:
            return redirect(next_url)
        return redirect(url_for('main.profile'))
    except db.DoesNotExist:
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if user doesn't exist or password is wrong, reload the page


@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    try:
        account = db.Account.get(db.Account.email == email)
        flash('User already exists, please try again.')
        return redirect(url_for('auth.login'))
    except db.DoesNotExist:
        pass

    new_account = db.Account.create(email=email, name=name, password=generate_password_hash(password, method='sha256'), role='customer')
    db.Customer.create(account=new_account)

    return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
