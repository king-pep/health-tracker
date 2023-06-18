from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from sqlalchemy.testing import db
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Validate input fields
        if not username or not password:
            flash('Please enter a username and password.', 'error')
            return redirect(url_for('auth.register'))

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('auth.register'))

        # Create a new user and store in the database
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by their username
        user = User.query.filter_by(username=username).first()

        # Validate the user's credentials
        if user and check_password_hash(user.password, password):
            # Set the user's ID in the session
            session['user_id'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password. Please try again.', 'error')
        return redirect(url_for('auth.login'))

    return render_template('login.html')
