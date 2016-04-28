__author__ = 'pankajg'

from flask import Flask
from config import config



from flask.ext.bootstrap import Bootstrap

#from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.misaka import Misaka
from flask_wtf.csrf import CsrfProtect

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['WTF_CSRF_CHECK_DEFAULT'] = 'False'

moment = Moment()
misaka= Misaka()

csrf = CsrfProtect()

bootstrap = Bootstrap()
login_manager = LoginManager()


# if a protected URL is tried to access you will be redirected to this URL
#login_manager.login_view = 'knowledge.login'


#db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/knowledgebase'
    print("App created")
    csrf.init_app(app)
    from knowledge import knowledge as knowledge_blueprint

    login_manager.init_app(app)


    app.register_blueprint(knowledge_blueprint)

    moment.init_app(app)
    misaka.init_app(app)

    bootstrap.init_app(app)

    login_manager.login_view = 'knowledge.login'
    login_manager.session_protection = "strong"

    #from auth import auth as auth_blueprint
    #app.register_blueprint(auth_blueprint, url_prefix='/auth')

    #db.init_app(app)

    return app


