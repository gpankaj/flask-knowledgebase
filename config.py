__author__ = 'pankajg'
import os


class Auth:
    """Google Project Credentials"""

    CLIENT_ID = ('563959952938-r23rkq28rs5mm3netmk9di3ne8kpr3f8.apps.googleusercontent.com')
    CLIENT_SECRET = 'KLn0sUmsXUkEfviIUsabmaAr'
    #REDIRECT_URI = 'http://lc-blr-292.ban.broadcom.com/gCallback'

    REDIRECT_URI = 'http://localhost:5000/gCallback'
    REDIRECT_URI = 'http://ec2-54-255-134-178.ap-southeast-1.compute.amazonaws.com:5000/gCallback'

    AUTH_URI = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URI = 'https://accounts.google.com/o/oauth2/token'
    USER_INFO = 'https://www.googleapis.com/userinfo/v2/me'
    SCOPE = ['profile', 'email']

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    WTF_CSRF_CHECK_DEFAULT =False
    SQLALCHEMY_TRACK_MODIFICATIONS=False
    DEBUG = False

class DevelopmentConfig(Config):
    DEBUG=False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 't0p s3r3t'


class TestingConfig(Config):
    TESTING=True

class ProductionConfig(Config):
    pass

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
