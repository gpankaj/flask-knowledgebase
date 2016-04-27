__author__ = 'pankajg'
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')


class DevelopmentConfig(Config):
    DEBUG=True
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