__author__ = 'pankajg'


from sqlalchemy import Table,Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
#from . import db
from flask.ext.login import UserMixin
from src import login_manager
from flask.ext.sqlalchemy import SQLAlchemy
from . import create_app


db = SQLAlchemy(create_app('development'), use_native_unicode=True)


class Question(db.Model):
    __tablename__= 'questions'
    id = db.Column(db.Integer, primary_key=True)

    question = db.Column(db.UnicodeText, nullable=False)
    #question_answers = relationship("Answer")
    # One Question will have one username
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    #user_uid = db.Column(db.String(20))
    date = db.Column(DateTime, default=func.now())
    topics = db.relationship('Topic',lazy='dynamic', backref = 'topic')

    #one question can have multiple topics/tags
    #question_topics = relationship("Topic")
    answers = db.relationship('Answer', lazy='dynamic', backref='question')
    visitor_count=db.Column(db.Integer)


# one question can have multiple answers.
class Answer(db.Model):
    __tablename__= 'answers'
    id= db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer,ForeignKey('questions.id'))
    #user_uid = db.Column(db.String(20))
    answer = db.Column(db.String(5026), nullable=False)
    # One Answer will have one user name
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(DateTime, default=func.now())
    visitor_count=db.Column(db.Integer)


class Upvote(db.Model):
    __tablename__='upvotes'
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'))
    question_id = db.Column(db.Integer,ForeignKey('questions.id'))
    date = db.Column(DateTime, default=func.now())
    user_name = db.Column(db.String(100))

class Visitor(db.Model):
    __tablename__='visitors'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer,ForeignKey('questions.id'))
    date = db.Column(DateTime, default=func.now())
    user_name = db.Column(db.String(100))

class Topic(db.Model):
    __tablename__= 'topics'
    id = db.Column(db.Integer, primary_key=True)
    topic_name = db.Column(db.String(32), nullable=False)
    question_id = db.Column(db.Integer,ForeignKey('questions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    #user_uid = db.Column(db.String(20))




class User(UserMixin,db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=False)
    tokens = db.Column(db.Text)
    created_at = db.Column(DateTime, default=func.now())

    #uid = db.Column(db.String(20), unique=True)
    is_admin = db.Column(db.Boolean)
    #password_hash = db.Column(db.String(128))
    email_me_for_new_question = db.Column(db.Boolean)
    email_me_for_updates = db.Column(db.Boolean)

    #topics = db.Column(db.String(512))
    #One user can subscribe to multiple topics
    #user_topics = relationship("Topic")

    questions = db.relationship('Question', backref='author', lazy='dynamic')
    answers = db.relationship('Answer', backref='author', lazy='dynamic')
    topics = db.relationship('Topic', backref='author', lazy='dynamic')




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from requests_oauthlib import OAuth2Session

def get_google_auth(state=None, token=None):
    from config import Auth
    if token:
        return OAuth2Session(Auth.CLIENT_ID, token=token)
    if state:
        return OAuth2Session(
            Auth.CLIENT_ID,
            state=state,
            redirect_uri=Auth.REDIRECT_URI)
    oauth = OAuth2Session(
        Auth.CLIENT_ID,
        redirect_uri=Auth.REDIRECT_URI,
        scope=Auth.SCOPE)
    return oauth


from flask_admin.contrib import sqla
from src.knowledge.form import CKTextAreaField

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.UnicodeText)


class TestAdmin(sqla.ModelView):
    form_overrides = dict(text=CKTextAreaField)

    create_template = 'edit.html'
    edit_template = 'edit.html'


