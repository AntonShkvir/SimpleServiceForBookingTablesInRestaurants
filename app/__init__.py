from flask import Flask, redirect, url_for
from flask_admin.contrib.sqla import ModelView
from app.models import db, User, Restaurant, RestaurantComment, Reservation, Table
from flask_admin import Admin, AdminIndexView

from flask_login import LoginManager, current_user, login_required


def create_app(testing=False):

    app = Flask(__name__)
    if testing:
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2xy1605b@localhost:5432/lab5_test'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2xy1605b@localhost:5432/lab5'

    login_manager = LoginManager(app)
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2xy1605b@localhost:5432/lab5'
    login_manager.init_app(app)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))


    class MyAdminIndexView(AdminIndexView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.admin

        def inaccessible_callback(self, name, **kwargs):
            return redirect(url_for('log'))

    admin = Admin(app, name='Store', template_mode='bootstrap3', index_view=MyAdminIndexView())

    class AuthModelView(ModelView):
        @login_required
        def is_accessible(self):
            return current_user.is_authenticated and current_user.admin

    admin.add_view(AuthModelView(User, db.session, name='Users'))
    admin.add_view(AuthModelView(Restaurant, db.session, name='Restaurants'))
    admin.add_view(AuthModelView(Table, db.session, name='Tables'))
    admin.add_view(AuthModelView(RestaurantComment, db.session, name='RestaurantComments'))
    admin.add_view(AuthModelView(Reservation, db.session, name='Reservations'))

    from app.views import views_bp

    app.register_blueprint(views_bp)

    return app


