__author__ = 'pankajg'

from flask.ext.wtf import Form

from flask_wysiwyg.wysiwyg import WysiwygField
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField, SelectMultipleField, TextAreaField, widgets
from wtforms.validators import Required, Length, Email, EqualTo
from flask.ext.login import login_user, login_required, current_user

class CKTextAreaWidget(widgets.TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class_', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field,
            **kwargs)


class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()



class EnterKnowledge(Form):
    #question = StringField('Question', validators=[Required(), Length(1, 64)], body=WysiwygField(u"texteditor",validators=[Required()])
    #question = WysiwygField("txteditor", validators=[Required()])
    question = CKTextAreaField('Question')

    topic = SelectMultipleField('Topic',choices=[('Jenkins', 'Jenkins'), ('Perforce', 'Perforce'), ('Git', 'Git'),
                                                 ('Ec','Electric Command'), ('unix','unix')])
    submit = SubmitField('Submit')

class UserRegistration(Form):
    username = StringField('Username')
    subscription = SelectMultipleField('Subscribe to Topic(s)',choices=[('Jenkins', 'Jenkins'), ('Perforce', 'Perforce'), ('Git', 'Git'),
                                                 ('Ec','Electric Command'), ('unix','unix')])

    email_me_for_new_question = BooleanField('Email me for new Questions (only for subscribed topics)')

    email_me_for_updates = BooleanField('Email me for updates (only for subscribed topics)')

    password = PasswordField('New Password', [Required(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    submit = SubmitField('Submit')

class ChangePassword(Form):
    password = PasswordField('New Password', [Required(), EqualTo('confirm', message='Passwords must match')])
    confirm  = PasswordField('Repeat Password')
    submit = SubmitField('Submit')

class Login(Form):
    username = StringField('Username')
    password  = PasswordField('Password')
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')

class Preference(Form):
    #from ..model import db
    subscription = SelectMultipleField('Modify Subscription',choices=[('Jenkins', 'Jenkins'), ('Perforce', 'Perforce'), ('Git', 'Git'),
                                                 ('Ec','Electric Command'), ('unix','unix')])

    email_me_for_new_question = BooleanField('Email me for new Questions (only for subscribed topics)')

    email_me_for_updates = BooleanField('Email me on for updates (only for subscribed topics)')

    submit = SubmitField('Submit')




class AnswerForm(Form):
    answer = CKTextAreaField('Answer')
    submit = SubmitField('Submit')


class UpvoteForm(Form):
    upvote = SubmitField('Upvote')