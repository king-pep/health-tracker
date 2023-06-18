from flask_login import UserMixin
from peewee import *

db = SqliteDatabase('health_tracker.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    password = CharField()
    active = BooleanField(default=True)

    @property
    def is_active(self):
        return self.active


class Activity(BaseModel):
    name = CharField()
    duration = IntegerField()
    calories = IntegerField()
    username = CharField()  # Add the username field to the Activity model
    user = ForeignKeyField(User, backref='activities')


class SleepEntry(BaseModel):
    date = DateField()
    start_time = DateTimeField()
    end_time = DateTimeField()
    duration = IntegerField()
    quality = CharField()
    username = CharField()  # Add the username field to the SleepEntry model
    user = ForeignKeyField(User, backref='sleep_entries')

    def determine_sleep_quality(self):
        if self.duration < 6:
            self.quality = 'poor'
        elif self.duration < 8:
            self.quality = 'fair'
        elif self.duration < 10:
            self.quality = 'good'
        else:
            self.quality = 'excellent'


class WaterEntry(BaseModel):
    timestamp = DateTimeField()
    amount = FloatField()
    username = CharField()  # Add the username field to the WaterEntry model
    user = ForeignKeyField(User, backref='water_entries')


class NutritionEntry(BaseModel):  # Add the NutritionEntry model
    food_item = CharField()
    calories = IntegerField()
    macronutrients = CharField()
    username = CharField()  # Add the username field to the NutritionEntry model
    user = ForeignKeyField(User, backref='nutrition_entries')


class Goal(BaseModel):
    username = CharField()
    name = CharField()
    target_value = IntegerField(default=0)
    user = ForeignKeyField(User, backref='goals')


class Progress(BaseModel):
    timestamp = DateTimeField()
    current_value = FloatField()
    goal = ForeignKeyField(Goal, backref='progress')


class Exercise(BaseModel):
    name = CharField()
    description = TextField()
    muscle_group = CharField()
    difficulty = CharField()


class Workout(BaseModel):
    username = CharField()
    name = CharField()
    description = TextField()
    exercises = ManyToManyField(Exercise, backref='workouts')
    user = ForeignKeyField(User, backref='workouts')


class Reminder(BaseModel):
    title = CharField()
    description = TextField()
    timestamp = DateTimeField()
    username = CharField()  # Add the username field to the Reminder model
    user = ForeignKeyField(User, backref='reminders')
