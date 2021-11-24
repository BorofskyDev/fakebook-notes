from flask import Blueprint

bp = Blueprint('auth', __name__, url_prefix="/auth")

from . import routes, models

#If you get an ImportError, run 'python run.py' to get the specific error 

