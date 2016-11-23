__author__ = 'pankajg'

from flask import Flask
from config import config
from flask_jsglue import JSGlue
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_wtf.csrf import CsrfProtect
from flaskext.markdown import Markdown
from flask_misaka import Misaka


import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['WTF_CSRF_CHECK_DEFAULT'] = 'False'

moment = Moment()
misaka= Misaka()
csrf = CsrfProtect()

bootstrap = Bootstrap()
login_manager = LoginManager()
#http://stewartjpark.com/Flask-JSGlue/
jsglue = JSGlue()

# if a protected URL is tried to access you will be redirected to this URL
#login_manager.login_view = 'knowledge.login'


#db = SQLAlchemy()
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root1234@knowledgebase2017.cd3pupo3w3sq.ap-southeast-1.rds.amazonaws.com/knowledgebase'

    db.init_app(app)

    print("App created")
    csrf.init_app(app)
    from knowledge import knowledge as knowledge_blueprint

    # login_manager.session_protection = "strong"
    login_manager.init_app(app)
    login_manager.login_view = 'knowledge.login'


    app.register_blueprint(knowledge_blueprint)

    moment.init_app(app)
    misaka.init_app(app)

    bootstrap.init_app(app)

    jsglue = JSGlue(app)
    Markdown(app)

    return app


from . import model
