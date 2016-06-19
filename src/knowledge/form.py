__author__ = 'pankajg'

from flask.ext.wtf import Form

from flask_wysiwyg.wysiwyg import WysiwygField
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField, SelectMultipleField, TextAreaField
from wtforms.validators import Required, Length, Email, EqualTo
from flask.ext.login import login_user, login_required, current_user
from flaskckeditor import CKEditor

class CKEditorForm(Form, CKEditor):
    title =  StringField()
    ckdemo = TextAreaField()
    submit = SubmitField('submit')

class EnterKnowledge(Form, CKEditor):
    #question = StringField('Question', validators=[Required(), Length(1, 64)], body=WysiwygField(u"texteditor",validators=[Required()])
    #question = WysiwygField("txteditor", validators=[Required()])
    subject = StringField('Title')
    question = TextAreaField('Question')

    topic = SelectMultipleField('Topic',default='unknown', choices=[('Jenkins', 'Jenkins'), ('Perforce', 'Perforce'), ('Git', 'Git'),
                                                 ('Ec','Electric Command'), ('unix','unix'),('unknown','No Topic Set'), ('aws','AWS'),('flask','Python Flask'),('angular','Angular'),
                                                                    ('html','HTML'),('css','CSS'),('js','javascript')])

    private = BooleanField('Private')
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
                                                 ('Ec','Electric Command'), ('unix','unix'), ('aws','AWS'),('flask','Python Flask'),('angular','Angular'),
                                                                    ('html','HTML'),('css','CSS'),('js','javascript')])

    email_me_for_new_question = BooleanField('Email me for new Questions (only for subscribed topics)')

    email_me_for_updates = BooleanField('Email me on for updates (only for subscribed topics)')

    submit = SubmitField('Submit')

class AnswerForm(Form,CKEditor):
    answer_text = TextAreaField('answer_text')
    submit = SubmitField('submit')

class UpvoteForm(Form):
    upvote = SubmitField('Upvote')