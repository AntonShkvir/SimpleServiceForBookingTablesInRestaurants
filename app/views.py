from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime

views_bp = Blueprint('views', __name__)
from app.models import db, User, Restaurant, RestaurantComment, Reservation, Table

from flask_login import login_user, login_manager, login_required, logout_user, current_user
login_manager.login_view = 'login'


@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        email = data['email']
        password = data['password']
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            return render_template('login.html', message='Invalid login. Please check your email and password.')

        if existing_user.password == password:
            login_user(existing_user)
            return redirect('/main')
        else:
            print("invalid")
            return render_template('login.html', message='Invalid login. Please check your username and password.')
    else:
        return render_template('login.html')


@views_bp.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@views_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', current_user=current_user)


@views_bp.route('/add_comment/<int:restaurant_id>', methods=['POST'])
@login_required
def add_comment(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    comment_text = request.form.get('comment_text')
    rating = int(request.form.get('rating'))

    # Создание нового комментария
    new_comment = RestaurantComment(
        user=current_user,
        restaurant=restaurant,
        comment_text=comment_text,
        rating=rating
    )

    db.session.add(new_comment)
    db.session.commit()

    flash('Comment added successfully!', 'success')
    return redirect(url_for('views.view_restaurant', restaurant_id=restaurant.restaurant_id))


@views_bp.route('/cancel_reservation/<int:reservation_id>', methods=['POST'])
@login_required
def cancel_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)

    if current_user.user_id != reservation.user_id:
        return redirect(url_for('views.profile'))

    canceled_table = reservation.table
    canceled_table.is_booked = False

    db.session.delete(reservation)
    db.session.commit()

    return redirect(url_for('views.profile'))


@views_bp.route('/restaurant/<restaurant_id>')
@login_required
def view_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    return render_template('restaurant.html', restaurant=restaurant)


@views_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()

    return redirect(url_for('views.home'))


@views_bp.route('/booking')
@login_required
def booking():
    restaurants = Restaurant.query.all()
    return render_template('booking.html', restaurants=restaurants)


@views_bp.route('/main')
@login_required
def main_page():
    return render_template('main.html')


@views_bp.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        existing_user_username = User.query.filter_by(username=username).first()
        if existing_user_username:
            return render_template('signup.html', message='User already exists')
        else:
            new_user = User(username=username, email=email, password=password)

            db.session.add(new_user)
            db.session.commit()
            # Successful login
            return redirect("/login")
    else:
        return render_template('signup.html')



@views_bp.route('/booking/<int:restaurant_id>/<int:table_id>', methods=['GET', 'POST'])
@login_required
def book_table(restaurant_id, table_id):
    if request.method == 'POST':
        date = request.form.get('date')


        reservation = Reservation(
            user_id=current_user.id,
            table_id=table_id,
            reservation_time=date
        )

        db.session.add(reservation)
        db.session.commit()

        return redirect(url_for('views.booking_success'))

    table = Table.query.get(table_id)

    return render_template('booking.html', restaurant_id=restaurant_id, table_id=table_id, table=table)


@views_bp.route('/select_time/<int:restaurant_id>', methods=['GET'])
@login_required
def select_time(restaurant_id):
    selected_table_id = int(request.args.get('table'))
    selected_table_number = next(
        (table.table_number for table in Table.query.filter_by(table_id=selected_table_id, is_booked=False)), None)
    return render_template('select_time.html', restaurant=Restaurant.query.get_or_404(restaurant_id),
                           restaurant_id=restaurant_id, selected_table_id=selected_table_id,
                           selected_table_number=selected_table_number)


@views_bp.route('/confirm_booking/<int:restaurant_id>/<int:table_id>', methods=['POST'])
@login_required
def confirm_booking(restaurant_id, table_id):
    selected_date = request.form.get('date')
    selected_time = request.form.get('time')

    booked_table = Table.query.get_or_404(table_id)

    new_reservation = Reservation(user=current_user, table=booked_table,
                                  reservation_time=datetime.strptime(f"{selected_date} {selected_time}",
                                                                     "%Y-%m-%d %H:%M"))

    db.session.add(new_reservation)
    db.session.commit()

    booked_table.is_booked = True
    db.session.commit()

    return redirect(url_for('views.view_restaurant', restaurant_id=restaurant_id))
