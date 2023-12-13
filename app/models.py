from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))

    reservations = db.relationship('Reservation', back_populates='user')
    comments = db.relationship('RestaurantComment', back_populates='user')

    def __repr__(self):
        return f"<User {self.username}>"


    def get_id(self):
        return str(self.user_id)

    def is_active(self):
        return self.is_active


class Restaurant(db.Model):
    __tablename__ = 'restaurants'

    restaurant_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255))
    description = db.Column(db.String(255))
    name = db.Column(db.String(255))

    tables = db.relationship('Table', back_populates='restaurant')
    comments = db.relationship('RestaurantComment', back_populates='restaurant')


class Table(db.Model):
    __tablename__ = 'tables'

    table_id = db.Column(db.Integer, primary_key=True)
    table_number = db.Column(db.Integer)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.restaurant_id'))
    is_booked = db.Column(db.Boolean)

    restaurant = db.relationship('Restaurant', back_populates='tables')
    reservations = db.relationship('Reservation', back_populates='table')


class Reservation(db.Model):
    __tablename__ = 'reservations'

    reservation_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    table_id = db.Column(db.Integer, db.ForeignKey('tables.table_id'))
    reservation_time = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', back_populates='reservations')
    table = db.relationship('Table', back_populates='reservations')


class RestaurantComment(db.Model):
    __tablename__ = 'restaurant_comments'

    comment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.restaurant_id'))
    comment_text = db.Column(db.Text)
    rating = db.Column(db.Integer)

    user = db.relationship('User', back_populates='comments')
    restaurant = db.relationship('Restaurant', back_populates='comments')
