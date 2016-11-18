__author__ = 'pankajg'


from sqlalchemy import Table,Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from src import login_manager
from . import db


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    #return User.query.filter_by(id=user_id).first()


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

class Question(db.Model):
    __tablename__= 'questions'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(256),nullable=False)

    private = db.Column(db.Boolean,default=False)

    visible = db.Column(db.Boolean, default=True)

    question = db.Column(db.TEXT(524288), nullable=False)
    #question_answers = relationship("Answer")
    # One Question will have one username
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    #user_uid = db.Column(db.String(20))
    date = db.Column(DateTime, default=func.now())
    topics = db.relationship('Topic',lazy='dynamic', backref = 'topic')

    #one question can have multiple topics/tags
    #question_topics = relationship("Topic")
    answers = db.relationship('Answer', lazy='dynamic', backref='question')
    #If the question was modified by author
    edited_count = db.Column(db.Integer, autoincrement=True)
    edited_date = db.Column(DateTime,default=func.now())
    flag_offensive = db.Column(db.Boolean, default=False)
    visitor_count=db.Column(db.Integer)


# one question can have multiple answers.
class Answer(db.Model):
    __tablename__= 'answers'
    id= db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer,ForeignKey('questions.id'))
    #user_uid = db.Column(db.String(20))
    answer = db.Column(db.TEXT(524288), nullable=False)
    # One Answer will have one user name
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(DateTime, default=func.now())
    reply_of_id=db.Column(db.Integer)
    edited_count = db.Column(db.Integer, autoincrement=True)
    edited_date = db.Column(DateTime, default=func.now())
    flag_offensive = db.Column(db.Boolean, default=False)
    verified = db.Column(db.Boolean, default=False)
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


class AllTopic(db.Model):
    __tablename__='alltopics'
    id = db.Column(db.Integer, primary_key=True)
    topic_category = db.Column(db.String(32), nullable=False)
    topic_name = db.Column(db.String(32), nullable=False)
    date = db.Column(DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    def __init__(self):
        obj1 = AllTopic(topic_category='_Add New_', topic_name='_Add New_', user_id=1)
        obj2 = AllTopic(topic_category='SCM', topic_name='Git', user_id=1)
        db.session.add(obj1)
        db.session.add(obj2)
        db.session.commit()


class Blog(db.Model):
    __tablename__='blogs'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(256), nullable=False)
    blog_text = db.Column(db.UnicodeText, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    private = db.Column(db.Boolean, default=False)
    visitor_count = db.Column(db.Integer)
    date = db.Column(DateTime, default=func.now())

class Comment(db.Model):
    __tablename__='comments'
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, ForeignKey('answers.id'))
    comment_text = db.Column(db.String(512), nullable=False)
    question_id = db.Column(db.Integer, ForeignKey('questions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date = db.Column(DateTime, default=func.now())
    offensive = db.Column(db.Boolean,default=False)


class User(UserMixin,db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=False)
    tokens = db.Column(db.Text)
    created_at = db.Column(DateTime, default=func.now())

    is_admin = db.Column(db.Boolean)

    email_me_for_new_question = db.Column(db.Boolean)
    email_me_for_updates = db.Column(db.Boolean)

    questions = db.relationship('Question', backref='author', lazy='dynamic')
    answers = db.relationship('Answer', backref='author', lazy='dynamic')
    topics = db.relationship('Topic', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref = 'author', lazy='dynamic')


class AnswerRequestedFromTable(db.Model):
    __tablename__='requested_answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, ForeignKey('questions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    requester_email_id = db.Column(db.String(100), nullable=False)
    date = db.Column(DateTime, default=func.now())
