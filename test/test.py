import unittest
from app import create_app
from flask_testing import TestCase
from app.models import db, User, Restaurant, RestaurantComment, Reservation, Table
from datetime import datetime, timedelta


class TestViews(TestCase):
    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:2xy1605b@localhost:5432/lab5'
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('home.html')



    def test_login_invalid_user(self):
        response = self.client.post('/login', data={'email': 'nonexistent@example.com', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('login.html')
        self.assertIn(b'Invalid login', response.data)

    def test_cancel_reservation_authenticated_user(self):
        test_reservation = Reservation(user_id=1, table_id=1)
        db.session.add(test_reservation)
        db.session.commit()

        with self.client:
            self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})
            response = self.client.post(f'/cancel_reservation/{test_reservation.reservation_id}')
            self.assertEqual(response.status_code, 302)

    def test_view_restaurant_authenticated_user(self):
        test_restaurant = Restaurant(name='Test Restaurant')
        db.session.add(test_restaurant)
        db.session.commit()

        with self.client:
            self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})
            response = self.client.get(f'/restaurant/{test_restaurant.restaurant_id}')
            self.assertEqual(response.status_code, 200)
            self.assert_template_used('restaurant.html')


    def test_booking_page_authenticated_user(self):
        with self.client:
            self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})
            response = self.client.get('/booking')
            self.assertEqual(response.status_code, 200)
            self.assert_template_used('booking.html')


    def test_main_page_authenticated_user(self):
        with self.client:
            self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})
            response = self.client.get('/main')
            self.assertEqual(response.status_code, 200)
            self.assert_template_used('main.html')


    def test_signup_valid_user(self):
        response = self.client.post('/signup', data={'username': 'newuser4', 'email': 'newuser4@example.com',
                                                     'password': 'newpassword4'})
        self.assertEqual(response.status_code, 302)

    def test_signup_existing_user(self):
        existing_user = User(username='existinguser3', email='existing3@example.com', password='existingpassword3')
        db.session.add(existing_user)
        db.session.commit()

        response = self.client.post('/signup', data={'username': 'existinguser4', 'email': 'existing4@example.com',
                                                     'password': 'existingpassword4'})
        self.assertEqual(response.status_code, 200)
        self.assert_template_used('signup.html')
        self.assertIn(b'User already exists', response.data)



    def test_invalid_route(self):
        response = self.client.get('/invalid_route')
        self.assertEqual(response.status_code, 404)

    def test_logout_authenticated_user(self):
        with self.client:
            self.client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})
            response = self.client.post('/logout')
            self.assertEqual(response.status_code, 302)


if __name__ == '__main__':
    unittest.main()
