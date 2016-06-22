__author__ = 'pankajg'
import os
#from src import db
from src import create_app
from flask.ext.script import Manager

from flask.ext.admin import Admin


from flask.ext.sqlalchemy import SQLAlchemy
app = create_app(os.getenv('FLASK_CONFIG') or 'default')
db = SQLAlchemy(app, use_native_unicode=True)
db.create_all()


def setup_db():
    from src.model import AllTopic
    obj_exists = AllTopic.query.filter_by().all()
    initilized = 0
    for obj in obj_exists:
        if (obj.topic_category != '_Add New_'):
            initilized = 1

    if (initilized == 0):
        obj1 = AllTopic(topic_category='_Add New_', topic_name='_Add New_', user_id=1)
        obj2 = AllTopic(topic_category='SCM', topic_name='Git', user_id=1)
        db.session.add(obj1)
        db.session.add(obj2)
        db.session.commit()

#setup_db()

import re
from jinja2 import evalcontextfilter, Markup, escape
_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')
@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))

    if eval_ctx.autoescape:
        result = Markup(result)
    return result


admin = Admin(app)
manager = Manager(app)




##################################################
#create some initial data


##################################################

@manager.command
def adduser(uid, admin=False):
    #Register a new User
    from getpass import getpass
    password = getpass()
    password2 = getpass(prompt="confirm: ")
    if password != password2:
        import sys
        sys.exit('Error : Password do not match')
    #db.create_all()
    from src.model import User
    user = User(uid=uid, password = password, is_admin = admin )
    db.session.add(user)
    db.session.commit()
    print ("User {0} was added successfully ".format(uid))

if __name__ == '__main__':
    manager.run()