
from . import knowledge
from flask import render_template, url_for, flash, redirect, request, abort, g
from form import EnterKnowledge, AnswerForm
from form import UserRegistration
from form import Preference
from form import Login
from var_dump import var_dump
from flask.ext.login import login_user, login_required, current_user, logout_user


@knowledge.route('/')
def index():
    print "Checking index page"
    return render_template('knowledge/index.html')


@knowledge.route('/my_questions')
@login_required
def my_questions():
    from src.model import Topic, Question,User
    #my_questions = Question.query.filter_by(user_id=current_user.id).all()

    question_topic = Question.query.join(Topic).join(User,User.id==Question.user_id).add_columns(User.uid,Question.question, Question.date, Topic.topic_name, Question.user_id, Question.id, Topic.question_id)\
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
            compress_question_topic[q_t.id] = q_t
        else:
            compress_question_topic[q_t.id] = q_t
            seen[q_t.id] = " ,  " + q_t.topic_name
    return render_template('knowledge/my_questions.html', question_topic=compress_question_topic.values())


@knowledge.route('/allquestions')
def all_questions():
    from src.model import Topic, db, Question, User

    #http://stackoverflow.com/questions/27900018/flask-sqlalchemy-query-join-relational-tables
    question_topic = Question.query.join(Topic).join(User,User.id==Question.user_id).add_columns(User.uid,Question.question, Question.date, Topic.topic_name, Question.id, Topic.question_id)\
        .filter(Question.id == Topic.question_id).\
                    order_by(Question.date.desc()).all()


    # If there is no question existing in system, redirect user to ask a question
    if(not question_topic):
        flash('Currently there is no question in database, ask a question')
        return redirect(url_for('knowledge.question'))

    #Below logic is to create a set of topic, with same question there can be more than one tag and multiple entry for that in Topics table.
    compress_question_topic = {}
    seen = {}
    for q_t in question_topic:
        if q_t.id in seen:
            q_t.topic_name += seen[q_t.id]
            compress_question_topic[q_t.id] = q_t
            print "Reading question is " + q_t.question

        else:
            compress_question_topic[q_t.id] = q_t
            seen[q_t.id] = " ,  " + q_t.topic_name
    return render_template('knowledge/allquestions.html', question_topic=compress_question_topic.values())



@knowledge.route('/topic/<topic_name>')
def topics(topic_name):
    return render_template('knowledge/topics.html', topic_name = topic_name)


@knowledge.route('/question/', methods = ['GET', 'POST'])
@login_required
def question():
    form = EnterKnowledge()
    if form.validate_on_submit():
        from src.model import Topic, db, Question
        my_data = "'" + form.question.data + "'"
        question_obj = Question(question=my_data,user_id=current_user.id)

        db.session.add(question_obj)
        db.session.commit()

        mail_message(question_obj, None,form.topic.data )
        for t in form.topic.data:
            topic_obj = Topic(question_id=question_obj.id, topic_name = t)
            db.session.add(topic_obj)
            db.session.commit()

        return redirect(url_for('knowledge.my_questions'))
    return render_template('knowledge/question.html', form=form)



@knowledge.route('/question/<int:question_id>', methods = ['GET', 'POST'])
def answer(question_id):
    from src.model import db,Question,Answer,User, Upvote, Visitor

    #question_text = Question.query.filter_by(id=question_id).first()
    question_text = Question.query.join(User).add_columns(Question.question, User.uid, User.id, Question.user_id, Question.id, Question.date, Question.topics).filter(Question.id==question_id).first()

    # update visitor count for question
    visitor_count = Visitor.query.filter_by(question_id=question_id).count()
    if visitor_count is not None:
        visitor_count = visitor_count+1



    #previous_answers = Answer.query.filter_by(question_id=question_id).all()
    previous_answers = Answer.query.join(User).add_columns(Answer.answer, Answer.date, Answer.user_id, Answer.question_id, User.uid, User.id,Answer.id)\
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

    if not current_user.is_authenticated:
        flash('View only mode, login to modify')



    form = AnswerForm()
    if current_user.is_authenticated:

        already_visited = Visitor.query.filter(Visitor.question_id==question_id).filter(Visitor.user_name==current_user.uid).first()
        if(already_visited is None):
            new_visitor = Visitor(question_id=question_id,user_name=current_user.uid)
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

    return render_template('knowledge/answer.html', question_text = question_text, previous_answers = previous_answers_with_upvote, form=form)


@knowledge.route('/upvote/answer/<int:answer_id>', methods = ['GET', 'POST'])
def upvote(answer_id):
    from src.model import db, Upvote, Answer

    already_visited = Upvote.query.filter(Upvote.answer_id==answer_id).filter(Upvote.user_name==current_user.uid).first()
    if(already_visited is None):
        upvote_obj = Upvote(answer_id=answer_id, user_name = current_user.uid)
        print "Upvoting " + str(answer_id)
        db.session.add(upvote_obj)
        db.session.commit()
    else:
        flash('You have already upvoted this answer')
    # from answer id find question id user = User.query.filter_by(uid = form.username.data).first()
    answer_obj = Answer.query.filter_by(id=answer_id).first()
    return redirect(url_for('knowledge.answer',question_id=answer_obj.question_id))


@knowledge.route('/question/<int:question_id>/edit/<int:answer_id>', methods = ['GET', 'POST'])
def editable_answer(question_id,answer_id):
    from src.model import db,Question,Answer,User

    question_text = Question.query.filter_by(id=question_id).first()
    #previous_answers = Answer.query.filter_by(question_id=question_id).all()
    previous_answers = Answer.query.join(User).add_columns(Answer.answer, Answer.date, Answer.user_id, Answer.question_id, User.uid, User.id,Answer.id)\
	                            .filter(Answer.question_id==question_id).filter(Answer.user_id==User.id).all()


    if not current_user.is_authenticated:
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



@knowledge.route('/register', methods = ['GET', 'POST'])
def register():
    form = UserRegistration()
    if form.validate_on_submit():
        print form.subscription.data

        from src.model import User, Topic, db
        #from .. import db

        existing_user_name = User.query.filter_by(uid=form.username.data).first()

        #create user if not existing
        if existing_user_name is None:
            user = User(uid=form.username.data, password = form.password.data, email_me_for_new_question=form.email_me_for_new_question.data, email_me_for_updates=form.email_me_for_updates.data )
            db.session.add(user)
            db.session.commit()
            for topic in form.subscription.data:
                topic_obj = Topic(topic_name = topic, user_id= user.id)
                db.session.add(topic_obj)
                db.session.commit()
            flash ('Successfully Registered and updated your preference to subscribe to '  + str(form.subscription.data))
            return redirect(url_for('.my_questions'))
        else:
            flash ('Username already existing ')

    return render_template('knowledge/register.html', form = form)


@knowledge.route('/login',methods = ['GET','POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.')
        return redirect(url_for('.my_questions'))
    form = Login()
    if form.validate_on_submit():
        from src.model import User, db
        #from .. import db
        user = User.query.filter_by(uid = form.username.data).first()
        if user is None:
            flash('User does not exist: ' + form.username.data )
            return render_template('/knowledge/login.html', form=form)
        elif(not user.verify_password(form.password.data)):
            flash('Wrong Password')
            return redirect(url_for('.login'))
        else:
            print "Logging using " + form.username.data

            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('knowledge.index'))
            flash('You have been logged in.')
    return render_template('/knowledge/login.html', form=form)



@knowledge.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('knowledge.login'))




@knowledge.route('/preference', methods = ['GET', 'POST'])
@login_required
def preference():
    form = Preference()
    from src.model import Topic, db, User
    #from .. import db
    #current_prefernces = Topic.query.with_entities(Topic.topic_name).filter_by(user_id=current_user.id).all()
    current_prefernces = Topic.query.filter_by(user_id=current_user.id).all()

    for c in current_prefernces:
        print c.topic_name
        #print "email_me_for_new_question " + c.email_me_for_new_question



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
        return redirect(url_for('knowledge.preference'))

    user_preferences = User.query.filter_by(id=current_user.id).first()
    form.email_me_for_new_question.data = user_preferences.email_me_for_new_question
    form.email_me_for_updates.data = user_preferences.email_me_for_updates
    print "Current preferences email_me_for_new_question " + str(form.email_me_for_new_question.data)
    print "Current preferences email_me_for_updates " + str(form.email_me_for_updates.data)

    return render_template('knowledge/preference.html', form = form, preferences = current_prefernces)


def mail_message(question,answer, topics):
    print "Sending mail from " + current_user.uid
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
        print obj.uid


