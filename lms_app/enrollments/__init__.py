from flask import Blueprint

enrollments_bp = Blueprint('enrollments', __name__)

from . import routes 
