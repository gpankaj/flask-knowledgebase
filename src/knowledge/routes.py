
from . import knowledge
from flask import render_template, url_for, flash, redirect, request, abort, g, session
from form import EnterKnowledge, AnswerForm
from form import Preference, CKEditorForm
from form import Login
from var_dump import var_dump
from flask.ext.login import login_user, login_required, current_user, logout_user




#################################################
#
#
#
#
#
#
#################################################

def get_all_questions():
    from src.model import Question, Topic,User
    question_topic = Question.query.join(Topic).join(User,User.id==Question.user_id).add_columns(User.email,Question.question, Question.date, Topic.topic_name, Question.id, Topic.question_id)\
        .filter(Question.id == Topic.question_id).\
                    order_by(Question.date.desc()).all()

    #print len(question_topic)
    # If there is no question existing in system, redirect user to ask a question
    if(not question_topic):
        flash('Currently there is no question in database, ask a question')
        return redirect(url_for('knowledge.question'))


    #Below logic is to create a set of topic, with same question there can be more than one tag and multiple entry for that in Topics table.
    compress_question_topic = {}
    seen = {}
    for q_t in question_topic:
        print q_t.id
        if q_t.id in seen:
            q_t.topic_name += seen[q_t.id]
            compress_question_topic[q_t.id] = q_t
            #print "Reading question is " + q_t.question

        else:
            #print "Inside Else block  question is " + q_t.question
            compress_question_topic[q_t.id] = q_t
            seen[q_t.id] = " ,  " + q_t.topic_name
    #print len(compress_question_topic)
    return compress_question_topic



#################################################
#
#
#
#
#
#
#################################################


@knowledge.route('/help')
def help():
    from src.model import get_google_auth
    from config import Auth
    if current_user.is_authenticated():
        return render_template('knowledge/help.html')

    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state

    return render_template('knowledge/help.html', auth_url=auth_url)


#################################################
#
#
#
#
#
#
#################################################

@knowledge.route('/')
def index():
    from src.model import get_google_auth, Visitor
    from config import Auth


    question_with_visitor=[]
    if (bool(get_all_questions()) and isinstance(get_all_questions(), dict)):
        for question in get_all_questions().values():
            all_visitors = Visitor.query.filter(Visitor.question_id==question.id).count()
            question.visitor = all_visitors
            question_with_visitor.append(question)


    if current_user.is_authenticated():
        return render_template('knowledge/index.html', question_topic=question_with_visitor)

    print("Message from index - you are unauthorized, builgin URL to use for login")
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state

    return render_template('knowledge/index.html', auth_url=auth_url, question_topic=question_with_visitor)



#################################################
#
#
#
#
#
#
#################################################


@knowledge.route('/my_questions')
@login_required
def my_questions():
    from src.model import Topic, Question,User
    #my_questions = Question.query.filter_by(user_id=current_user.id).all()

    question_topic = Question.query.join(Topic).join(User,User.id==Question.user_id).add_columns(User.email,Question.question, Question.date, Topic.topic_name, Question.user_id, Question.id, Topic.question_id)\
        .filter(Question.user_id == current_user.id)\
        .filter(Question.id == Topic.question_id).all()


    # If there is no question existing in system, redirect user to ask a question
    if(not question_topic):
        flash('Currently there is no question asked by you, do you want to ask a question')
        return redirect(url_for('knowledge.question'))

    #Below logic is to create a set of topic, with same question there can be more than one tag and multiple entry for that in Topics table.
    compress_question_topic = {}
    seen = {}
    for q_t in question_topic:
        if q_t.id in seen:
            q_t.topic_name += seen[q_t.id]
            print "Topic Name " + q_t.topic_name
            compress_question_topic[q_t.id] = q_t
            seen[q_t.id] = " ,  " + q_t.topic_name
        else:
            compress_question_topic[q_t.id] = q_t
            seen[q_t.id] = " ,  " + q_t.topic_name
    return render_template('knowledge/my_questions.html', question_topic=compress_question_topic.values())


#################################################
#
#
#
#
#
#
#################################################


@knowledge.route('/allquestions')
def all_questions():
    #################################################################################
    from src.model import get_google_auth, Visitor, Question
    from config import Auth

    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
#################################################################################
    if (bool(get_all_questions()) and isinstance(get_all_questions(), dict)):
        return render_template('knowledge/allquestions.html', question_topic=get_all_questions().values(),auth_url=auth_url)
    else:
        return render_template('knowledge/index.html', auth_url=auth_url, question_topic=[])



#################################################
#
#
#
#
#
#
#################################################


@knowledge.route('/question/', methods = ['GET', 'POST'])
@login_required
def question():
    form = EnterKnowledge()
    if form.validate_on_submit():
        from src.model import Topic, db, Question
        my_data = form.question.data
        question_obj = Question(question=my_data,user_id=current_user.id)

        db.session.add(question_obj)
        db.session.commit()

        for t in form.topic.data:
            topic_obj = Topic(question_id=question_obj.id, topic_name = t)
            print "Topic is set to " + t
            db.session.add(topic_obj)
            db.session.commit()

        mail_message(question_obj, None,form.topic.data )
        if not form.topic.data:
            print "Setting topic data"
            topic_obj = Topic(question_id=question_obj.id, topic_name = "unknown")
            print "Topic is set to " + "unknown"
            db.session.add(topic_obj)
            db.session.commit()



        return redirect(url_for('knowledge.my_questions'))
    return render_template('knowledge/question.html', form=form)




#################################################
#
#
#
#
#
#
#################################################


@knowledge.route('/question/<int:question_id>', methods = ['GET', 'POST'])
def answer(question_id):
    from src.model import db,Question,Answer,User, Upvote, Visitor

    #question_text = Question.query.filter_by(id=question_id).first()
    question_text = Question.query.join(User).add_columns(Question.question, User.email, User.id, Question.user_id, Question.id, Question.date, Question.topics).filter(Question.id==question_id).first()



    #################################################################################
    from src.model import get_google_auth, Visitor, Question
    from config import Auth

    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    #################################################################################

    # update visitor count for question if logged in
    if(current_user.is_authenticated()):
        visitor = Visitor.query.filter(Visitor.question_id==question_id).filter(Visitor.user_name==current_user.email).first()
        if visitor is not None:
            visitor.user_name=current_user.email
            db.session.commit()



    #previous_answers = Answer.query.filter_by(question_id=question_id).all()
    previous_answers = Answer.query.join(User).add_columns(Answer.answer, Answer.date, Answer.user_id, Answer.question_id, User.email, User.id,Answer.id)\
	                            .filter(Answer.question_id==question_id).filter(Answer.user_id==User.id).order_by(Answer.date.desc()).all()


    all_visitors = Visitor.query.filter(Visitor.question_id==question_id).count()
    # Add visitor data to question_text object
    question_text.visitors = all_visitors

    #UserImage.query.filter(UserImage.user_id == 1).count()
    previous_answers_with_upvote = []
    for previous_answer in previous_answers:
        upvoted_answer = Upvote.query.filter_by(answer_id=previous_answer.id).count()
        print "upvoted_answer" + str(upvoted_answer)
        previous_answer.upvote = upvoted_answer
        previous_answers_with_upvote.append(previous_answer)

    if not current_user.is_authenticated():
        flash('View only mode, login to modify')


    form = AnswerForm()
    if current_user.is_authenticated():

        already_visited = Visitor.query.filter(Visitor.question_id==question_id).filter(Visitor.user_name==current_user.email).first()
        if(already_visited is None):
            new_visitor = Visitor(question_id=question_id,user_name=current_user.email)
            db.session.add(new_visitor)
            db.session.commit()


        if form.validate_on_submit():
            import re
            if  ( re.match('', form.answer.data)):
                if ( re.match('[^\s]', form.answer.data)) :
                    answer_obj = Answer(answer=form.answer.data, question_id = question_id, user_id=current_user.id)
                    db.session.add(answer_obj)
                    db.session.commit()
                    #return render_template('knowledge/answer.html',question_text = question_text, previous_answers = previous_answers, form=form)
                    return redirect(url_for('knowledge.answer',question_id=question_id))
                else:
                    flash('Can not submit an empty answer')
            else:
                flash('Can not submit an empty answer')
        #print "Capturing and showing answers for question id " + str(question_id)

    return render_template('knowledge/answer.html', question_text = question_text, previous_answers = previous_answers_with_upvote, form=form, auth_url=auth_url)



#################################################
#
#
#
#
#
#
#################################################


@knowledge.route('/upvote/answer/<int:answer_id>', methods = ['GET', 'POST'])
def upvote(answer_id):
    from src.model import db, Upvote, Answer

    already_visited = Upvote.query.filter(Upvote.answer_id==answer_id).filter(Upvote.user_name==current_user.email).first()
    if(already_visited is None):
        upvote_obj = Upvote(answer_id=answer_id, user_name = current_user.email)
        print "Upvoting " + str(answer_id)
        db.session.add(upvote_obj)
        db.session.commit()
    else:
        flash('You have already upvoted this answer')
    # from answer id find question id user = User.query.filter_by(uid = form.username.data).first()
    answer_obj = Answer.query.filter_by(id=answer_id).first()
    return redirect(url_for('knowledge.answer',question_id=answer_obj.question_id))


#################################################
# TODO: Edit an answer
#
#
#
#
#
#################################################



@knowledge.route('/question/<int:question_id>/edit/<int:answer_id>', methods = ['GET', 'POST'])
def editable_answer(question_id,answer_id):
    from src.model import db,Question,Answer,User

    question_text = Question.query.filter_by(id=question_id).first()
    #previous_answers = Answer.query.filter_by(question_id=question_id).all()
    previous_answers = Answer.query.join(User).add_columns(Answer.answer, Answer.date, Answer.user_id, Answer.question_id, User.email, User.id,Answer.id)\
	                            .filter(Answer.question_id==question_id).filter(Answer.user_id==User.id).all()


    if not current_user.is_authenticated():
        flash('View only mode, login to modify')
        return render_template('knowledge/answer.html',question_text = question_text, previous_answers = previous_answers)

    form = AnswerForm()
    if form.validate_on_submit():
        answer_obj = Answer(answer=form.answer.data, question_id = question_id, user_id=current_user.id)
        db.session.add(answer_obj)
        db.session.commit()
        return render_template('knowledge/answer.html',question_text = question_text, previous_answers = previous_answers, form=form)
    #print "Capturing and showing answers for question id " + str(question_id)
    return render_template('knowledge/answer.html', question_text = question_text, previous_answers = previous_answers, form=form)


#################################################
#
#
#
#
#
#
#################################################


@knowledge.route('/logout')
@login_required
def logout():
    logout_user()
    #session.pop('email', '')
    #session.pop('oauth_state','')
    flash('You have been logged out.')
    return redirect(url_for('knowledge.index'))



#################################################
#
#
#
#
#
#
#################################################



@knowledge.route('/preference', methods = ['GET', 'POST'])
@login_required
def preference():
    form = Preference()
    from src.model import Topic, db, User
    #from .. import db
    #current_prefernces = Topic.query.with_entities(Topic.topic_name).filter_by(user_id=current_user.id).all()
    current_prefernces = Topic.query.filter_by(user_id=current_user.id).all()



    if form.validate_on_submit():

        updated_user_preferences = User.query.filter_by(id=current_user.id).update(dict(email_me_for_new_question=form.email_me_for_new_question.data,
                                                                      email_me_for_updates=form.email_me_for_updates.data ))
        db.session.commit()


        Topic.query.filter_by(user_id=current_user.id).delete()

        for topic in form.subscription.data:
            topic_obj = Topic(topic_name = topic, user_id=current_user.id)
            db.session.add(topic_obj)
            db.session.commit()
        flash ('Successfully updated your preferences')
        return redirect(url_for('knowledge.all_questions'))

    topics=[]
    for c in current_prefernces:
        topics.append(c.topic_name)

    form.subscription.data=topics

    user_preferences = User.query.filter_by(id=current_user.id).first()
    form.email_me_for_new_question.data = user_preferences.email_me_for_new_question
    form.email_me_for_updates.data = user_preferences.email_me_for_updates
    print "Current preferences email_me_for_new_question " + str(form.email_me_for_new_question.data)
    print "Current preferences email_me_for_updates " + str(form.email_me_for_updates.data)

    return render_template('knowledge/preference.html', form = form)



#################################################
# TODO:
#
#
#
#
#
#################################################


def mail_message(question,answer, topics):
    print "Sending mail from " + current_user.email
    print "Topics " + str(topics)
    print "Sending mail to all subsribed user to topic " + str(topics)
    print "Message " + question.question
    from src.model import Topic, User

    #query = Notification.query.filter(Notification.id.in_(my_list)).all()
    topic_obj = Topic.query.filter(Topic.user_id,Topic.topic_name.in_(topics)).all()

    for topic in topic_obj:
        print topic.user_id
        #print "\""+str(holder)+"\""
        obj = User.query.filter_by(id=int(topic.user_id)).first()
        if obj is None:
            print "obj is emptry "
        print obj.email


#################################################
#
#
#
#
#
#
#################################################


@knowledge.route('/login')
def login():
    from src.model import get_google_auth
    from config import Auth
    if current_user.is_authenticated():
        flash("You are already authenticated ")
        return render_template('knowledge/index.html')
    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    return render_template('knowledge/login.html', auth_url=auth_url)




#################################################
# Purpose: CallBack
#
#
#
#
#
#################################################


import json
from urllib2 import HTTPError

@knowledge.route('/gCallback')
def callback():
    from config import Auth
    from src.model import get_google_auth
    from src.model import User, db
    # Redirect user to home page if already logged in.
    if current_user is not None and current_user.is_authenticated():
        print("You are authorized...woo")
        return redirect(url_for('knowledge.index'))
    if 'error' in request.args:
        if request.args.get('error') == 'access_denied':
            return 'You denied access.'
        return 'Error encountered.'
    if 'code' not in request.args and 'state' not in request.args:
        return redirect(url_for('login'))
    else:
        # Execution reaches here when user has
        # successfully authenticated our app.

        google = get_google_auth()
        if ( 'oauth_state' in session):
            google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'

        google = get_google_auth(token=token)
        resp = google.get(Auth.USER_INFO)
        if resp.status_code == 200:
            user_data = resp.json()
            email = user_data['email']
            print "Email id is " + email
            user = User.query.filter_by(email=email).first()
            exited = True
            if user is None:
                exited = False
                user = User()
                user.email = email
            user.name = user_data['name']
            print "User name is "+ user.name
            user.tokens = json.dumps(token)
            user.avatar = user_data['picture']
            db.session.add(user)
            db.session.commit()
            login_user(user)
            if (not exited):
                flash("Successfully logged in, have a check on your preferences")
                return redirect(url_for('knowledge.preference'))
            else:
                return redirect(url_for('knowledge.preference'))
        return 'Could not fetch your information.'