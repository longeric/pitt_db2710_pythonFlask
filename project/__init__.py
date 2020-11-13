from functools import wraps
from flask import Flask, g, render_template, current_app
from flask_login import LoginManager, current_user
from . import models as db


def role_required(roles):
    def wrapper(func):
        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            elif current_user.role not in roles:
                return current_app.login_manager.unauthorized()
            return func(*args, **kwargs)
        return decorated_view
    return wrapper


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = '_5c#yf2L"F4Q8z\n\xec]kdlshfieo12'
    app.config['UPLOAD_FOLDER'] = app.root_path + '/../uploads'

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.Account.get_by_id(user_id)
        except db.DoesNotExist:
            return None

    @app.before_request
    def before_request():
        g.db = db.database
        g.db.connect()


    @app.after_request
    def after_request(response):
        g.db.close()
        return response


    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404


    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .cart import cart as cart_blueprint
    app.register_blueprint(cart_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app