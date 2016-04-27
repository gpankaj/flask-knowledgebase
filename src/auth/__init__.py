__author__ = 'pankajg'

from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import routes

