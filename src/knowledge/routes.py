
from . import knowledge
from flask import render_template, url_for, flash, redirect, request,session,abort,jsonify
from form import EnterKnowledge, AnswerForm,AddTopicForm,EditQuestionForm
from flask_login import login_user, login_required, current_user, logout_user

def populate_topics():
    from src.model import AllTopic

    all_topics_with_categories = AllTopic.query.filter_by().all()
    category_dict = {}
    list_of_tuples=[]

    for all_topics_with_categorie in all_topics_with_categories:
        if all_topics_with_categorie.topic_category == '_AddNew_' or all_topics_with_categorie.topic_category == '_AddNew_':
            print "Skipping adding _Add New_"
            continue

        if all_topics_with_categorie.topic_category in category_dict:
            list_of_tuples = category_dict[all_topics_with_categorie.topic_category]
            list_of_tuples.append((all_topics_with_categorie.topic_name, all_topics_with_categorie.topic_name))
            category_dict[all_topics_with_categorie.topic_category] = list_of_tuples
        else:
            list_of_tuples.append((all_topics_with_categorie.topic_name,all_topics_with_categorie.topic_name))
            category_dict[all_topics_with_categorie.topic_category] = list_of_tuples

        # we need to remove previous items from list.
        list_of_tuples=[]

    # Below converts list to tuples in dict value.
    for k,v in category_dict.items():
        category_dict[k] = tuple(v)

    topic_group = tuple(category_dict.iteritems())

    return topic_group
########################################################################################################


def gen_rnd_filename():
    import datetime, random
    filename_prefix = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    return '%s%s' % (filename_prefix, str(random.randrange(1000, 10000)))

@knowledge.route('/ckupload/', methods=['POST', 'OPTIONS'])
def ckupload():
    """CKEditor file upload"""
    import os
    from flask import make_response
    from manage import app
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        fileobj = request.files['upload']
        fname, fext = os.path.splitext(fileobj.filename)
        rnd_name = '%s%s' % (gen_rnd_filename(), fext)
        filepath = os.path.join(app.static_folder, 'upload', rnd_name)
        dirname = os.path.dirname(filepath)
        if not os.path.exists(dirname):
            try:
                os.makedirs(dirname)
            except:
                error = 'ERROR_CREATE_DIR'
        elif not os.access(dirname, os.W_OK):
            error = 'ERROR_DIR_NOT_WRITEABLE'
        if not error:
            fileobj.save(filepath)
            url = url_for('static', filename='%s/%s' % ('upload', rnd_name))
    else:
        error = 'post error'
    res = """<script type="text/javascript">
             window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
             </script>""" % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response

########################################################################################################
#################################################
#
#
#
#
#
#
#################################################

def get_all_questions(my_only=False):
    from src.model import Question, Topic,User,Visitor
    question_topic = None

    if my_only:
        question_topic = Question.query.join(Topic).join(User,User.id==Question.user_id).add_columns(User.email,User.name,Question.subject, Question.private,Question.question, Question.date, Topic.topic_name, Question.id, Topic.question_id)\
            .filter(Question.user_id == current_user.id).filter(Question.id == Topic.question_id).filter(Question.private==0).all()
    else:
        question_topic = Question.query.join(Topic).join(User, User.id == Question.user_id).add_columns(User.email,
                                                                                                        User.name,
                                                                                                        Question.subject,
                                                                                                        Question.private,
                                                                                                        Question.question,
                                                                                                        Question.date,
                                                                                                        Topic.topic_name,
                                                                                                        Question.id,
                                                                                                        Topic.question_id) \
            .filter(Question.id == Topic.question_id).filter(Question.private == 0).all()


    new_question_topic = [r for r in question_topic]
    #print len(question_topic)
    # If there is no question existing in system, redirect user to ask a question
    if(not question_topic):
        flash('Currently there is no question asked by you, ask a question. Redirecting to index page')
        return redirect(url_for('knowledge.question'))

    for q in question_topic:
        print "Inside get_all_questions" + q.topic_name

    #Below logic is to create a set of topic, with same question there can be more than one tag and multiple entry for that in Topics table.
    compress_question_topic = {}

    seen = {}

    for q_t in new_question_topic:
        print q_t.id
        if q_t.id in seen:

            print "q_t has topic_name as " + q_t.topic_name
            print "Seen has values as  " + seen[q_t.id]
            print "question id is " + str(q_t.id)

            seen[q_t.id] = str(seen[q_t.id]) + ", " + q_t.topic_name

            q_t.topic_name = str(seen[q_t.id])

            #setattr(q_t, 'topic_name', q_t.topic_name + str(seen[q_t.id]))

            print "New topic name is " + q_t.topic_name
            #print "Topic name " + q_t.new_topic_name

            compress_question_topic[q_t.id] = q_t
            #print "Reading question is " + q_t.question

        else:
            #print "Inside Else block  question is " + q_t.question
            print "Added first time..."
            compress_question_topic[q_t.id] = q_t
            seen[q_t.id] = q_t.topic_name
    #print len(compress_question_topic)

    question_with_visitor=[]
    for question in compress_question_topic.values():
        all_visitors = Visitor.query.filter(Visitor.question_id == question.id).count()
        question.visitor = all_visitors
        question_with_visitor.append(question)

    return question_with_visitor



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
@knowledge.route('/index')
def index():
    from src.model import get_google_auth, Visitor,Answer,Upvote,AnswerRequestedFromTable,User
    from config import Auth

    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state

    question_with_visitor=[]
    all_question = get_all_questions()
    if (isinstance(all_question, list)):
        for question in get_all_questions():
            #Answer.query.filter(Answer.question_id==question.id).
            """
            question_topic = Question.query.join(Topic).join(User,User.id==Question.user_id).add_columns(User.email,Question.subject, Question.private,Question.question, Question.date, Topic.topic_name, Question.id, Topic.question_id)\
            .filter(Question.id == Topic.question_id).filter(Question.private==0).all()

            """
            upvotes_on_answer = Answer.query.join(Upvote).add_columns(Answer.id,Answer.answer,Upvote.answer_id).filter(Answer.question_id==question.id).filter(Answer.id==Upvote.answer_id).count()
            answered = Answer.query.filter(Answer.question_id == question.id).order_by(Answer.date.desc()).first()

            all_requested = AnswerRequestedFromTable.query.join(User).add_columns(User.id, User.name, User.email,
                                                                                  AnswerRequestedFromTable.question_id,
                                                                                  AnswerRequestedFromTable.user_id,
                                                                                  AnswerRequestedFromTable.date,
                                                                                  AnswerRequestedFromTable.requester_email_id). \
                                                                                        filter(AnswerRequestedFromTable.question_id==question.id).all()

            for request in all_requested:
                print request.requester_email_id

            question.requested = all_requested

            question.upvotes_on_answer = upvotes_on_answer
            question.answered = answered

            question_with_visitor.append(question)
    else:
        return render_template('knowledge/index.html', auth_url=auth_url, question_topic=question_with_visitor)

    #from operator import  attrgetter
    #sorted_question_with_visitors = sorted(question_with_visitor, key=attrgetter('all_visitors'), reverse=True)
    if current_user.is_authenticated():
        #find his preferences
        return render_template('knowledge/index.html', question_topic=question_with_visitor)

    print("Message from index - you are unauthorized, builgin URL to use for login")

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

    question_topic = Question.query.join(Topic).join(User,User.id==Question.user_id).add_columns(User.email,Question.subject, Question.private, Question.visible, Question.question, Question.date, Topic.topic_name, Question.user_id, Question.id, Topic.question_id)\
        .filter(Question.user_id == current_user.id).filter(Question.private==1).filter(Question.visible==1)\
        .filter(Question.id == Topic.question_id).all()

    # If there is no question existing in system, redirect user to ask a question
    if(not question_topic):
        flash('Currently there is no questions in draft')
        return redirect(url_for('knowledge.all_questions'))

    #Below logic is to create a set of topic, with same question there can be more than one tag and multiple entry for that in Topics table.
    compress_question_topic = {}
    seen = {}

    for q_t in question_topic:
        print q_t.id
        if q_t.id in seen:

            print "q_t has topic_name as " + q_t.topic_name
            print "Seen has values as  " + seen[q_t.id]
            print "question id is " + str(q_t.id)


            seen[q_t.id] = str(seen[q_t.id]) + ", " + q_t.topic_name

            q_t.topic_name = str(seen[q_t.id])

            # setattr(q_t, 'topic_name', q_t.topic_name + str(seen[q_t.id]))

            print "New topic name is " + q_t.topic_name
            # print "Topic name " + q_t.new_topic_name

            compress_question_topic[q_t.id] = q_t
            # print "Reading question is " + q_t.question

        else:
            # print "Inside Else block  question is " + q_t.question
            print "Added first time..."
            compress_question_topic[q_t.id] = q_t
            seen[q_t.id] = q_t.topic_name


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
@login_required
def all_questions():
    #################################################################################
    from src.model import get_google_auth, Answer, Upvote
    from config import Auth

    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
#################################################################################

    question_with_visitor = []

    all_question = get_all_questions(my_only=True)
    if (isinstance(all_question, list)):
        for question in all_question:

            upvotes_on_answer = Answer.query.join(Upvote).add_columns(Answer.id, Upvote.answer_id).filter(
                Answer.question_id == question.id).filter(Answer.id == Upvote.answer_id).count()
            answered = Answer.query.filter(Answer.question_id == question.id).order_by(Answer.date.desc()).first()

            question.upvotes_on_answer = upvotes_on_answer
            question.answered = answered

            question_with_visitor.append(question)
    else:
        return redirect(url_for('knowledge.index'))

    if (bool(question_with_visitor)):
        return render_template('knowledge/allquestions.html', question_topic=question_with_visitor,auth_url=auth_url)
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

    form.topic.choices = populate_topics()

    if form.validate_on_submit():
        from src.model import Topic, db, Question
        my_data = form.question.data
        question_obj = Question(question=my_data,subject=form.subject.data, private=form.private.data, user_id=current_user.id)

        db.session.add(question_obj)
        db.session.commit()
        """
        for t in form.topic.data:
            topic_obj = Topic(question_id=question_obj.id, topic_name = t)
            print "Topic is set to " + t
            db.session.add(topic_obj)
            db.session.commit()
        """

        #print "Topics are " + str(form.topic.choices)
        # http://stackoverflow.com/questions/23205577/python-flask-immutablemultidict
        print "request.values + " + str(request.values)
        for item in request.form.getlist('topic'):
            topic_obj = Topic(question_id=question_obj.id, topic_name=item)
            print "Topic is set to " + item
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
    else:
        flash("Please fill all the required fields")
    return render_template('knowledge/question.html', form=form)


@knowledge.route('/add_topic',methods=['GET','POST'])
@login_required
def add_topic():
    if (not current_user.id):
        flash("Please logout and login again")
        return redirect(url_for('knowledge.index'))

    form = AddTopicForm()
    from src.model import AllTopic, db
    all_categories_and_topics = AllTopic.query.filter_by().all()

    form.old_category.choices=set([(all_categories_and_topic.topic_category, all_categories_and_topic.topic_category) for all_categories_and_topic in all_categories_and_topics])

    if form.validate_on_submit():
        try:
            new_topic=None
            if(form.new_category.data):
                new_topic = AllTopic(topic_category=form.new_category.data,topic_name=form.topic_name.data, user_id=current_user.id)
            elif(form.old_category.data):
                print "Old category after validation is " + form.old_category.data
                new_topic = AllTopic(topic_category=form.old_category.data,topic_name=form.topic_name.data, user_id=current_user.id)
            else:
                flash('Error')
                return redirect(url_for('knowledge.AddTopic'))

            db.session.add(new_topic)
            db.session.commit()
            flash('Added topic : ' + form.topic_name.data  + " in category : " + new_topic.topic_category +" You can ask the question now selecting this category")
            return redirect(url_for('knowledge.question'))

        except Exception as e:
            flash('Faiiled to add category... please retry ' + str(e.message))
            return redirect(url_for('knowledge.add_topic'))
    else:
        print "Old category is " + str(form.old_category.data)
        print "Form not validated"

    return render_template('knowledge/add_new_category.html',form=form)


@knowledge.route('/question_autocomplete', methods=['GET'])
@login_required
def question_autocomplete():
    search = request.args.get('term')

    print "Searching for " + str(search)

    from src.model import Question
    from flask import jsonify
    results = Question.query.with_entities(Question.subject, Question.id,Question.private,Question.visible,Question.user_id).filter(Question.subject.ilike('%'+search+'%')).all()
    final_result=[]
    for result in results:
        t = (result.id,result.subject)
        #take out private question which are not owned by same owner
        if(result.private==1 and result.user_id == current_user.id and result.visible==1):
            final_result.append(t)
        elif(result.private==0 and result.visible==1):
            final_result.append(t)
        else:
            print "We are excluding question " + str(result.id)
            print "result.user_id " + str(result.user_id)
            print "current_user.id " + str(current_user.id)

    return jsonify(result=final_result)

#################################################

@knowledge.route('/question/edit/<int:question_id>', methods = ['GET', 'POST'])
@login_required
def editable_question(question_id):
    from src.model import db,Question

    previous_question = Question.query.filter_by(id=question_id).first()

    print "Current user id " + str(current_user.id)
    print "previous answer user id " + str(previous_question.user_id)
    if(current_user.id != previous_question.user_id):
        flash("You can not modify this question")
        return redirect(url_for('knowledge.answer', question_id=previous_question.id))
    if (previous_question.visible == 0):
        flash("You can modify a deleted question")
        return redirect(url_for('knowledge.my_questions'))

    print "Rephrasing " + str(question_id)

    form = EditQuestionForm()
    form.question.data = previous_question.question
    form.subject.data = previous_question.subject
    if(previous_question.private):
        form.private.data = 1
    else:
        form.private.data = 0

    #form.topic.data=topics

    #answer = previous_answer.answer[3:]
    #print "After removing para " + answer[:-6]
    #form.answer.data = answer[:-6]

    if form.validate_on_submit():
        print "New data is " + request.form['question']

        Question.query.filter_by(id=question_id).update(dict(question=request.form['question']))
        Question.query.filter_by(id=question_id).update(dict(subject=request.form['subject']))

        if 'private' in request.form:
            print "Yes it has private field"
            Question.query.filter_by(id=question_id).update(dict(private=1))
        else:
            Question.query.filter_by(id=question_id).update(dict(private=0))
            flash("Updated Question as Publicly Viewable")
        db.session.commit()
        flash("Changes are saved!!")

        return redirect(url_for('knowledge.answer', question_id=previous_question.id))
    return render_template('knowledge/edit_question_form.html',form=form)

@knowledge.route('/question/delete/<int:question_id>', methods = ['GET', 'POST'])
@login_required
def delete_private_question(question_id):
    from src.model import db,Question
    Question.query.filter_by(id=question_id).update(dict(visible=0))
    db.session.commit()
    flash("Deleted your question " + str(question_id))
    return redirect(url_for('knowledge.my_questions'))



#################################################
#
#
#
#
#
#
#################################################

@knowledge.route('/reset')
def reset(default='index'):
    redirect_to = request.args.get('next') or request.referrer or default
    return redirect (redirect_to)


@knowledge.route('/cancel')
def cancel(default='index'):
    redirect_to = request.args.get('next') or request.referrer or default
    return redirect (url_for('knowledge.index'))


@knowledge.route('/question/<int:question_id>', methods = ['GET', 'POST'])
def answer(question_id):
    from src.model import db,Question,Answer,User, Upvote,Topic

    question_text = Question.query.join(User).add_columns(Question.question, User.email, User.id, Question.subject, Question.private, Question.visible, Question.user_id, Question.id, Question.date, Question.topics).filter(Question.visible==1).filter(Question.id==question_id).first()
    if (not question_text):
        flash( str(question_id) + 'This question does not exist. Redirecting to index page')
        return redirect(url_for('knowledge.index'))
    if (current_user.is_authenticated()):
        if(question_text.private==1 and question_text.email != current_user.email) :
            flash("You do not own this private question with ID : " + str(question_text.id))
            return redirect(url_for('knowledge.index'))

    #################################################################################
    from src.model import get_google_auth, Visitor,Comment
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

    previous_answers = Answer.query.join(User).add_columns(Answer.answer, Answer.date, Answer.user_id, Answer.question_id, User.email, User.id,Answer.id)\
	                            .filter(Answer.question_id==question_id).filter(Answer.user_id==User.id).order_by(Answer.date.desc()).all()



    all_visitors = Visitor.query.filter(Visitor.question_id==question_id).count()
    # Add visitor data to question_text object
    question_text.visitors = all_visitors

    topics_for_question = Topic.query.filter_by(question_id=question_text.id).all()
    question_text.topics_for_question = ""
    for topic in topics_for_question:
        if question_text.topics_for_question != "" :
            question_text.topics_for_question = topic.topic_name  + " ," + question_text.topics_for_question
        else:
            question_text.topics_for_question = topic.topic_name

    #UserImage.query.filter(UserImage.user_id == 1).count()
    previous_answers_with_upvote = []

    for previous_answer in previous_answers:
        upvoted_answer = Upvote.query.filter_by(answer_id=previous_answer.id).count()
        print "upvoted_answer" + str(upvoted_answer)
        previous_answer.upvote = upvoted_answer

        comments_of_answer = Comment.query.filter_by(answer_id=previous_answer.id).all()
        previous_answer.comments = comments_of_answer

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
            if  ( re.match('', form.answer_text.data)):
                if ( re.match('[^\s]', form.answer_text.data)) :
                    answer_obj = Answer(answer=form.answer_text.data, question_id = question_id, user_id=current_user.id)
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

#'/capture_email?question_id=' + question_id + '&email_id=' + $("#email"+question_id).val() + '&requesting_user_id='+ requesting_user_id,
@knowledge.route('/capture_email', methods=['GET','POST'])
@login_required
def capture_email():
    from src.model import AnswerRequestedFromTable, db
    if (request.args.get('question_id') and request.args.get('email_id') and request.args.get('requesting_user_id')):
        already_asked_from_same_user = AnswerRequestedFromTable.query.filter(AnswerRequestedFromTable.question_id==request.args.get('question_id')).filter(AnswerRequestedFromTable.requester_email_id==request.args.get('email_id')).first()
        if(not already_asked_from_same_user is None):
            print "Question was already asked by someone.."
            flash("Question from same user was already asked ")
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

        add_request_email_obj = AnswerRequestedFromTable(question_id=request.args.get('question_id'),user_id=request.args.get('requesting_user_id'),
                                                         requester_email_id=request.args.get('email_id'))

        db.session.add(add_request_email_obj)
        db.session.commit()
        flash("Requested " + request.args.get('email_id') + " for help on this question.")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@knowledge.route('/capture_comment', methods=['GET','POST'])
@login_required
def capture_comment():
    from src.model import Comment,db
    if (request.args.get('comment_text') and request.args.get('answer_id')):
        add_comment_obj = Comment(answer_id= request.args.get('answer_id') , comment_text = request.args.get('comment_text'),user_id=current_user.id)
        db.session.add(add_comment_obj)
        db.session.commit()
        print "Answer id was " + str(request.args.get('answer_id'))
        print "Comment was " + request.args.get('comment_text')
        flash("Success in adding comment")
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        flash("Some problem...")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

"""
    from flask import jsonify
    #return redirect(url_for('knowledge.answer',question_id=request.args.get('question_id')))
    #return jsonify({'result': 'success'})
    from src.model import db, Question, Answer, User, Upvote, Topic
    question_id = request.args.get('question_id')
    question_text = Question.query.join(User).add_columns(Question.question, User.email, User.id, Question.subject,
                                                          Question.private, Question.user_id, Question.id,
                                                          Question.date, Question.topics).filter(
        Question.id == question_id).first()
    if (not question_text):
        flash(str(question_id) + ' This question does not exist. Redirecting to index page')
        return redirect(url_for('knowledge.index'))
    if (current_user.is_authenticated()):
        if (question_text.private == 1 and question_text.email != current_user.email):
            flash("You do not own this private question with ID : " + str(question_text.id))
            return redirect(url_for('knowledge.index'))

    #################################################################################
    from src.model import get_google_auth, Visitor, Comment
    from config import Auth

    google = get_google_auth()
    auth_url, state = google.authorization_url(
        Auth.AUTH_URI, access_type='offline')
    session['oauth_state'] = state
    #################################################################################

    # update visitor count for question if logged in
    if (current_user.is_authenticated()):
        visitor = Visitor.query.filter(Visitor.question_id == question_id).filter(
            Visitor.user_name == current_user.email).first()
        if visitor is not None:
            visitor.user_name = current_user.email
            db.session.commit()

    previous_answers = Answer.query.join(User).add_columns(Answer.answer, Answer.date, Answer.user_id,
                                                           Answer.question_id, User.email, User.id, Answer.id) \
        .filter(Answer.question_id == question_id).filter(Answer.user_id == User.id).order_by(Answer.date.desc()).all()

    all_visitors = Visitor.query.filter(Visitor.question_id == question_id).count()
    # Add visitor data to question_text object
    question_text.visitors = all_visitors

    topics_for_question = Topic.query.filter_by(question_id=question_text.id).first()
    question_text.topics_for_question = topics_for_question.topic_name

    # UserImage.query.filter(UserImage.user_id == 1).count()
    previous_answers_with_upvote = []

    for previous_answer in previous_answers:
        upvoted_answer = Upvote.query.filter_by(answer_id=previous_answer.id).count()
        print "upvoted_answer" + str(upvoted_answer)
        previous_answer.upvote = upvoted_answer

        comments_of_answer = Comment.query.filter_by(answer_id=previous_answer.id).all()
        previous_answer.comments = comments_of_answer

        previous_answers_with_upvote.append(previous_answer)

    if not current_user.is_authenticated():
        flash('View only mode, login to modify')

    form = AnswerForm()
    if current_user.is_authenticated():

        already_visited = Visitor.query.filter(Visitor.question_id == question_id).filter(
            Visitor.user_name == current_user.email).first()
        if (already_visited is None):
            new_visitor = Visitor(question_id=question_id, user_name=current_user.email)
            db.session.add(new_visitor)
            db.session.commit()

        if form.validate_on_submit():
            import re
            if (re.match('', form.answer_text.data)):
                if (re.match('[^\s]', form.answer_text.data)):
                    answer_obj = Answer(answer=form.answer_text.data, question_id=question_id, user_id=current_user.id)
                    db.session.add(answer_obj)
                    db.session.commit()
                    # return render_template('knowledge/answer.html',question_text = question_text, previous_answers = previous_answers, form=form)
                    return redirect(url_for('knowledge.answer', question_id=question_id))
                else:
                    flash('Can not submit an empty answer')
            else:
                flash('Can not submit an empty answer')
                # print "Capturing and showing answers for question id " + str(question_id)

    return render_template('knowledge/answer.html', question_text=question_text,
                           previous_answers=previous_answers_with_upvote, form=form, auth_url=auth_url)

"""


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



@knowledge.route('/answer/edit/<int:answer_id>', methods = ['GET', 'POST'])
@login_required
def editable_answer(answer_id):
    from src.model import db,Question,Answer,User
    previous_answer = Answer.query.filter_by(id=answer_id).add_columns(Answer.answer, Answer.date, Answer.user_id,Answer.question_id,Answer.id).first()
    print "Current user id " + str(current_user.id)
    print "previous answer user id " + str(previous_answer.user_id)
    if(current_user.id != previous_answer.user_id):
        flash("You can not modify this answer")
        return redirect(url_for('knowledge.answer', question_id=previous_answer.question_id))
    print "Rephrasing " + str(answer_id)

    form = AnswerForm(answer_text=previous_answer.answer)
    #form.answer.data = previous_answer.answer
    #answer = previous_answer.answer[3:]
    #print "After removing para " + answer[:-6]
    #form.answer.data = answer[:-6]

    if form.validate_on_submit():
        flash("Changes are saved!!")

        print "New data is " + request.form['answer_text']
        Answer.query.filter_by(id=answer_id).update(dict(answer=request.form['answer_text']))
        db.session.commit()
        return redirect(url_for('knowledge.answer', question_id=previous_answer.question_id))
    return render_template('knowledge/edit_answer_form.html',form=form)



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
    from form import Preference
    form = Preference()
    form.subscription.choices = populate_topics()


    from src.model import Topic, db, User
    #from .. import db
    #current_prefernces = Topic.query.with_entities(Topic.topic_name).filter_by(user_id=current_user.id).all()
    current_prefernces = Topic.query.filter_by(user_id=current_user.id).all()

    selected_options = []
    for c in current_prefernces:
        # topics.append(c.topic_name)
        print "user had " + c.topic_name
        selected_options.append(c.topic_name)
    #form.subscription.data=selected_options


    if form.validate_on_submit():

        updated_user_preferences = User.query.filter_by(id=current_user.id).update(dict(email_me_for_new_question=form.email_me_for_new_question.data,
                                                                      email_me_for_updates=form.email_me_for_updates.data ))
        db.session.commit()


        Topic.query.filter_by(user_id=current_user.id).delete()

        print "request.values + " + str(request.values)

        for item in request.form.getlist('subscription'):
            topic_obj = Topic(user_id=current_user.id, topic_name=item)
            print "Subscription is set to " + item
            db.session.add(topic_obj)
            db.session.commit()

        flash ('Successfully updated your preferences')
        return redirect(url_for('knowledge.all_questions'))

    user_preferences = User.query.filter_by(id=current_user.id).first()
    form.email_me_for_new_question.data = user_preferences.email_me_for_new_question
    form.email_me_for_updates.data = user_preferences.email_me_for_updates
    print "Current preferences email_me_for_new_question " + str(form.email_me_for_new_question.data)
    print "Current preferences email_me_for_updates " + str(form.email_me_for_updates.data)

    return render_template('knowledge/preference.html', form = form,selected_options=selected_options)



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
        """
        if ( 'oauth_state' in session):
            google = get_google_auth(state=session['oauth_state'])
        try:
            token = google.fetch_token(
                Auth.TOKEN_URI,
                client_secret=Auth.CLIENT_SECRET,
                authorization_response=request.url)
        except HTTPError:
            return 'HTTPError occurred.'
        """

        token = google.fetch_token(
            Auth.TOKEN_URI,
            client_secret=Auth.CLIENT_SECRET,
            authorization_response=request.url)
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
                return redirect(url_for('knowledge.index'))
        return 'Could not fetch your information.'