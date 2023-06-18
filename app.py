from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import current_user, LoginManager, login_user, logout_user
from flask_bcrypt import Bcrypt
from peewee import SqliteDatabase
from health.models import User, Activity, SleepEntry, WaterEntry, Goal, Progress, Exercise, Workout, Reminder, \
    NutritionEntry

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Configure the database connection
db = SqliteDatabase('health_tracker.db')

# Connect to the database
db.connect()

# Create tables if they don't exist
db.create_tables([User, Activity, SleepEntry, WaterEntry, Goal, Progress, Exercise, Workout, Reminder])

# Initialize Flask-Bcrypt
bcrypt = Bcrypt(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


# Custom decorator for login required views
def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    return decorated_view


# Routes

@app.route('/')
def home():
    return render_template('login.html')


# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Please enter a username and password.', 'error')
            return redirect(url_for('register'))

        # Check if the username already exists
        existing_user = User.get_or_none(User.username == username)
        if existing_user:
            flash('Username already exists. Please choose a different username.', 'error')
            return redirect(url_for('register'))

        # Hash the password
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User.create(username=username, password=hashed_password)

        if not new_user:
            flash('Failed to create a new user. Please try again.', 'error')
            return redirect(url_for('register'))

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by their username
        user = User.select().where(User.username == username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)  # Log in the user
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid username or password. Please try again.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log out the user
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user  # Retrieve the current logged-in user
    # log the user object to the console
    print('User: ', user.username)
    activities = Activity.select().where(Activity.user == user)
    print('Activities: ', activities)
    sleep_entries = SleepEntry.select().where(SleepEntry.user == user)
    water_entries = WaterEntry.select().where(WaterEntry.user == user)
    goals = Goal.select().where(Goal.user == user)
    workouts = Workout.select().where(Workout.user == user)
    reminders = Reminder.select().where(Reminder.user == user)

    return render_template('dashboard.html', activities=activities, sleep_entries=sleep_entries,
                           water_entries=water_entries, goals=goals, workouts=workouts, reminders=reminders)


@app.route('/add_activity', methods=['GET', 'POST'])
@login_required
def add_activity():
    if request.method == 'POST':
        name = request.form['name']
        duration = int(request.form['duration'])
        calories_burned = int(request.form['calories_burned'])

        # Validate the form data
        if not name or duration <= 0 or calories_burned <= 0:
            flash('Please provide valid activity details.', 'error')
            return redirect(url_for('add_activity'))

        user = current_user  # Assuming you have a current_user object with the logged-in user's details
        # Create an Activity object and save it to the database
        activity = Activity(username=current_user.username, name=name, duration=duration,
                            calories=calories_burned, user=user)
        activity.save()

        flash('Activity added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_activity.html')


@app.route('/add_sleep', methods=['GET', 'POST'])
@login_required
def add_sleep():
    if request.method == 'POST':
        date = request.form['date']
        duration = int(request.form['duration'])

        # Validate the form data
        if not date or duration <= 0:
            flash('Please provide valid sleep details.', 'error')
            return redirect(url_for('add_sleep'))

        # Convert the date string to a datetime object
        start_time = datetime.strptime(date, '%Y-%m-%d')

        # Calculate the end time based on start time and duration
        end_time = start_time + timedelta(hours=duration)

        # Determine the sleep quality based on the duration
        if duration < 6:
            quality = 'poor'
        elif duration < 8:
            quality = 'fair'
        elif duration < 10:
            quality = 'good'
        else:
            quality = 'excellent'

        # Create a SleepEntry object and save it to the database
        sleep_entry = SleepEntry(username=current_user.username, start_time=start_time, end_time=end_time,
                                 duration=duration, quality=quality, date=date, user=current_user)
        sleep_entry.save()

        flash('Sleep entry added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_sleep.html')


@app.route('/add_nutrition', methods=['GET', 'POST'])
@login_required
def add_nutrition():
    if request.method == 'POST':
        food_item = request.form['food_item']
        calories = int(request.form['calories'])
        macronutrients = request.form['macronutrients']

        # Validate the form data
        if not food_item or calories <= 0 or not macronutrients:
            flash('Please provide valid nutrition details.', 'error')
            return redirect(url_for('add_nutrition'))

        # Create a NutritionEntry object and save it to the database
        nutrition_entry = NutritionEntry(username=current_user.username, food_item=food_item, calories=calories,
                                         macronutrients=macronutrients)
        nutrition_entry.save()

        flash('Nutrition entry added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_nutrition.html')


@app.route('/add_water', methods=['GET', 'POST'])
@login_required
def add_water():
    if request.method == 'POST':
        date = request.form['date']
        amount = int(request.form['amount'])

        # Validate the form data
        if not date or amount <= 0:
            flash('Please provide valid water intake details.', 'error')
            return redirect(url_for('add_water'))

        # Convert the date string to a datetime object
        timestamp = datetime.strptime(date, '%Y-%m-%d')

        # Create a WaterEntry object and save it to the database
        water_entry = WaterEntry(username=current_user.username, timestamp=timestamp,
                                 amount=amount, user=current_user)
        water_entry.save()

        flash('Water intake entry added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_water.html')


@app.route('/add_goal', methods=['GET', 'POST'])
@login_required
def add_goal():
    if request.method == 'POST':
        name = request.form['name']
        target = int(request.form['target_value'])

        # Validate the form data
        if not name or target <= 0:
            flash('Please provide valid goal details.', 'error')
            return redirect(url_for('add_goal'))

        # Create a Goal object and save it to the database
        goal = Goal(username=current_user.username, name=name, target_value=target, user=current_user)
        goal.save()

        flash('Goal added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_goal.html')


@app.route('/create_workout', methods=['GET', 'POST'])
@login_required
def create_workout():
    if request.method == 'POST':
        name = request.form['name']
        exercises = request.form.getlist('exercise')

        # Validate the form data
        if not name or not exercises:
            flash('Please provide valid workout details.', 'error')
            return redirect(url_for('create_workout'))

        # Create a Workout object and save it to the database
        workout = Workout(username=current_user.username, name=name)
        workout.save()

        # Create Exercise objects and associate them with the Workout
        for exercise_name in exercises:
            exercise = Exercise(workout=workout, name=exercise_name)
            exercise.save()

        flash('Workout created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_workout.html')


@app.route('/add_reminder', methods=['GET', 'POST'])
@login_required
def add_reminder():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        # Validate the form data
        if not title or not description:
            flash('Please provide valid reminder details.', 'error')
            return redirect(url_for('add_reminder'))

        # Create a Reminder object and save it to the database
        reminder = Reminder(username=current_user.username, title=title, description=description)
        reminder.save()

        flash('Reminder added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_reminder.html')


@app.route('/add_progress/<int:goal_id>', methods=['POST'])
@login_required
def add_progress(goal_id):
    goal = Goal.get_or_none(Goal.id == goal_id)

    if goal is None:
        flash('Goal not found.', 'error')
        return redirect(url_for('dashboard'))

    date = request.form['timestamp']
    progress = float(request.form['current_value'])

    # Validate the form data
    if not date or progress < 0:
        flash('Please provide valid progress details.', 'error')
        return redirect(url_for('view_progress', goal_id=goal_id))

    # Convert the date string to a datetime object
    timestamp = datetime.strptime(date, '%Y-%m-%d')

    # Create a Progress object and save it to the database
    progress_entry = Progress(goal=goal, current_value=progress, timestamp=timestamp)
    progress_entry.save()

    flash('Progress added successfully!', 'success')
    return redirect(url_for('view_progress', goal_id=goal_id))


@app.route('/update_progress/<int:goal_id>', methods=['GET', 'POST'])
@login_required
def update_progress(goal_id):
    goal = Goal.get_or_none(Goal.id == goal_id)

    if not goal:
        flash('Goal not found.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        progress = int(request.form['progress'])

        # Validate the form data
        if progress <= 0:
            flash('Please provide valid progress.', 'error')
            return redirect(url_for('update_progress', goal_id=goal_id))

        # Create a Progress object and save it to the database
        progress_entry = Progress(goal=goal, progress=progress)
        progress_entry.save()

        flash('Progress updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('update_progress.html', goal=goal)


@app.route('/view_workouts')
@login_required
def view_workouts():
    workouts = Workout.select().where(Workout.username == current_user.username)

    return render_template('view_workouts.html', workouts=workouts)


@app.route('/view_reminders')
@login_required
def view_reminders():
    reminders = Reminder.select().where(Reminder.username == current_user.username)

    return render_template('view_reminders.html', reminders=reminders)


@app.route('/view_progress/<int:goal_id>')
@login_required
def view_progress(goal_id):
    goal = Goal.get_or_none(id=goal_id, username=current_user.username)
    if not goal:
        flash('Invalid goal ID.', 'error')
        return redirect(url_for('dashboard'))

    progress_entries = Progress.select().where(Progress.goal == goal)

    # print each entry in the database
    for entry in progress_entries:
        print('entry', entry.goal)

    return render_template('view_progress.html', goal=goal, progress_entries=progress_entries)


if __name__ == '__main__':
    app.run(debug=True)
