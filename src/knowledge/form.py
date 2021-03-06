__author__ = 'pankajg'

from flask_wtf import Form

from flask_wysiwyg.wysiwyg import WysiwygField
from wtforms import StringField, PasswordField, BooleanField, SubmitField,SelectField, SelectMultipleField, TextAreaField,validators, HiddenField
from wtforms.validators import Required, Length, Email, EqualTo
from wtform_extended_selectfield import ExtendedSelectField


class CKEditorForm(Form):
    title =  StringField()
    ckdemo = TextAreaField()
    submit = SubmitField('submit')

class AddTopicForm(Form):
    old_category = SelectField('Name of the category',choices="", validators=[validators.optional()])
    new_category=StringField('Name of category if you want to add new',validators=[validators.optional()])

    topic_name=StringField('Topic Name')
    #private = BooleanField('Private', default=False)
    submit = SubmitField('Submit')
class EditQuestionForm(Form):
    subject = StringField('Title')
    question = TextAreaField('Question')
    private = BooleanField('Private')
    submit = SubmitField('Submit')

class EnterKnowledge(Form):
    #question = StringField('Question', validators=[Required(), Length(1, 64)], body=WysiwygField(u"texteditor",validators=[Required()])
    #question = WysiwygField("txteditor", validators=[Required()])
    subject = StringField('Title')
    question = TextAreaField('Question')


    topic_group=(
            ('SCM', (
                ('Jenkins', 'Jenkins'),
                ('Perforce', 'Perforce'),
                ('Git', 'Git'),
                ('Electric_Commander', 'ElectricCommander'),
                ('Gerrit', 'Gerrit'),
            )),
            ('Unix', (
                ('Unix', 'Unix'),
                ('Shell', 'Shell'),
            )),
            ('Application Programming', (
                ('Perl', 'Perl'),
                ('Python', 'Python'),
                ('Android', 'Android'),
                ('Web', 'HTML/CSS/Jquery/JavaScript'),
                ('C++', 'C++'),
                ('Java', 'Java'),
            )),
            ('System Programming', (
                ('Verilog', 'Verilog'),
                ('C', 'C'),
                ('C++','C++')
            )),
            ('Tools', (
                ('Coverity', 'Coverity'),
            )),

        )
    """
    topic = SelectField('Topic',default='unknown', choices=[('Jenkins', 'Jenkins'), ('Perforce', 'Perforce'), ('Git', 'Git'),
                                                 ('Ec','Electric Command'), ('unix','unix'),('unknown','No Topic Set'), ('aws','AWS'),('flask','Python Flask'),('angular','Angular'),
                                                                 ('html','HTML'),('css','CSS'),('js','javascript')])"""
    #https://github.com/industrydive/wtforms_extended_selectfield
    topics = ()
    topic = ExtendedSelectField('Topic',choices=topics, render_kw={"multiple":True})

    #topic = StringField('topic',render_kw={'multiple': True, "placeholder": "Categories which applies to above question...."},)

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
    topics = ()
    subscription = ExtendedSelectField('Modify Subscription', choices=topics, render_kw={"multiple": True})
    """
    subscription = SelectField('Modify Subscription',choices=[('Jenkins', 'Jenkins'), ('Perforce', 'Perforce'), ('Git', 'Git'),
                                                 ('Ec','Electric Command'), ('unix','unix'), ('aws','AWS'),('flask','Python Flask'),('angular','Angular'),
                                                                    ('html','HTML'),('css','CSS'),('js','javascript')])
    """

    email_me_for_new_question = BooleanField('Email me for new Questions (only for subscribed topics)')
    email_me_for_updates = BooleanField('Email me on for all updates (only for subscribed topics)')
    submit = SubmitField('Submit')

class AnswerForm(Form):
    answer_text = TextAreaField('answer_text')
    submit = SubmitField('submit')

class UpvoteForm(Form):
    upvote = SubmitField('Upvote')