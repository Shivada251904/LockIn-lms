from flask import Blueprint

lockdown_bp = Blueprint('lockdown', __name__)

from . import routes
