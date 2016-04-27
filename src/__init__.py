__author__ = 'pankajg'

from flask import Flask
from config import config



from flask.ext.bootstrap import Bootstrap

#from flask.ext.sqlalchemy import SQLAlchemy

from flask.ext.login import LoginManager
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.misaka import Misaka

moment = Moment()
misaka= Misaka()

bootstrap = Bootstrap()
login_manager = LoginManager()


# if a protected URL is tried to access you will be redirected to this URL
login_manager.login_view = 'knowledge.login'

#db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/knowledgebase'
    print("App created")

    from knowledge import knowledge as knowledge_blueprint
    app.register_blueprint(knowledge_blueprint)
    moment.init_app(app)
    misaka.init_app(app)

    bootstrap.init_app(app)

    #from auth import auth as auth_blueprint
    #app.register_blueprint(auth_blueprint, url_prefix='/auth')

    #db.init_app(app)
    login_manager.init_app(app)
    return app
