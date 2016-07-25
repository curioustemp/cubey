# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from flask_user import UserMixin
from flask_user.forms import RegisterForm
from flask_wtf import Form
from wtforms import StringField, SubmitField, validators
from app import db

from datetime import datetime


# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    username = db.Column(db.String(10), nullable=False, unique=True)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True)
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    reset_password_token = db.Column(db.String(100), nullable=False, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    banned = db.Column(db.Boolean(), nullable=False, server_default='0')
    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    # Relationships
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))


# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields
class MyRegisterForm(RegisterForm):
    submit = SubmitField('Submit')


# Define the User profile form
class UserProfileForm(Form):
    email = StringField('email', validators=[
        validators.DataRequired('Must supply email')])
    submit = SubmitField('Save')

class Upvote(db.Model):
    __tablename__ = 'upvotes'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    plugin_id = db.Column(db.Integer(), db.ForeignKey('plugins.id', ondelete='CASCADE'))

    plugin = db.relationship("Plugin", back_populates="upvotes")

    def __init__(self, user_id, plugin_id):
        self.user_id = user_id
        self.plugin_id = plugin_id

def _get_date():
    return datetime.utcnow() 

class Plugin(db.Model):
    __tablename__ = 'plugins'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    name = db.Column(db.String(50), nullable=False, server_default=u'')
    description = db.Column(db.String(300), nullable=False, server_default=u'')
    repo_url = db.Column(db.String(300), nullable=False, server_default=u'')
    readme = db.Column(db.String(5000), nullable=False, server_default=u'')
    created_at = db.Column(db.DateTime, default=_get_date)
    updated_at = db.Column(db.DateTime, onupdate=_get_date)
    image_url = db.Column(db.String(300))

    upvotes = db.relationship('Upvote', order_by=Upvote.id, back_populates="plugin", lazy='dynamic')

    def __init__(self, name, description, user_id, repo_url, image_url, created_at=None):
        self.name = name
        self.description = description
        self.user_id = user_id
        self.repo_url = repo_url
        self.image_url = image_url
        if created_at is None:
            created_at = datetime.utcnow()
        self.created_at = created_at
