__author__ = 'pankajg'
import os
#from src import db
from src import create_app
from flask.ext.script import Manager
from src.model import User, db
from flask.ext.admin import Admin



app = create_app(os.getenv('FLASK_CONFIG') or 'default')


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

db.create_all()

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
    user = User(uid=uid, password = password, is_admin = admin )
    db.session.add(user)
    db.session.commit()
    print ("User {0} was added successfully ".format(uid))

if __name__ == '__main__':
    manager.run()