__author__ = 'pankajg'

from flask import Blueprint

knowledge = Blueprint('knowledge', __name__)
print "Blueprint Created"
from . import routes

