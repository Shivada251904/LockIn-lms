from flask import Flask, redirect, url_for
from .extensions import bcrypt
from .models import db
import os

def build_app():
    app = Flask(__name__)
    
    #Configuration base for the LMS features#
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretkey123')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lockin-lms.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    #Intializing the database and bcrypt password hashing spec#
    db.init_app(app)
    bcrypt.init_app(app)
    
    #Getting blueprints from the database and importing to routes#
    from .users.routes import users_bp
    from .courses.routes import courses_bp
    from .enrollments.routes import enrollments_bp
    from .assignments.routes import assignments_bp
    from .submissions.routes import submissions_bp
    #Lockdown modes feature implementation#
    from .lockdown.routes import lockdown_bp
    
    #Registering blueprints for user interaction#
    app.register_blueprint(users_bp, url_prefix='/users')
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(enrollments_bp, url_prefix='/enrollments')
    app.register_blueprint(assignments_bp, url_prefix='/assignments')
    app.register_blueprint(submissions_bp, url_prefix='/submissions')
    app.register_blueprint(lockdown_bp, url_prefix='/lockdown')
    
    @app.route("/")
    def home():
        return redirect(url_for("users.sign_in_page"))
    
    #Creating tables for the database#
    with app.app_context():
        from . import models
        db.create_all()
    return app