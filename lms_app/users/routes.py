from flask import (jsonify, request, render_template, session, redirect, url_for)
from . import users_bp
from lms_app.extensions import bcrypt
from lms_app.models import User, db
from lms_app.auth.jwt_utils import build_token, call_auth
import re

#Taking user credentials#
@users_bp.route("/", methods=["POST"])
def build_user():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        if not data:
            return jsonify({
                "error": "No data issued"
            }), 400
        
        required_entries = [
            "name",
            "email",
            "password",
            "role"
        ]
        
        for entry in required_entries:
            if entry not in data:
                return jsonify({
                    "error": f"Missing entry: {entry}"
                }), 400
    
        #Checking if email is in use and exists#
        if User.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email in use, please try again"}), 400
        
        allowed_roles = ["student", "teacher"]
        
        if "role" in data:
            if data["role"] not in allowed_roles:
                return jsonify({
                    "error": "Invalid role"
                }), 400 
    
        #password hashing generator kit#
        pw_hashed = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    
        user = User(
            name=data["name"],
            email=data["email"],
            password_hash=pw_hashed,
            role=data["role"]
        )
                        
        db.session.add(user)
        db.session.commit()
    
        return redirect(url_for("users.sign_in_page"))
    
    except Exception as e:
        db.session.rollback()
        
        return jsonify({
            "error": "User not created",
            "details": str(e)
        }), 500

#Logging on to the LMS#
@users_bp.route("/login", methods=["POST"])
def sign_in():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        if not data:
            return jsonify({
                "error": "No login data issued"
            }), 400
        
        email = data.get("email")
        password = data.get("password")
        
        if not email or not password:
            return jsonify({
                "error": "Email and password needed"
            }), 400   
            
        user = User.query.filter_by(email=email).first()
    
        if not user:
            return jsonify({"error": "Invalid details"}), 401
    
        if not bcrypt.check_password_hash(user.password_hash, data["password"]):
            return jsonify({"error": "Invalid details"}), 401
    
        token = build_token(user.id, user.role)
    
        session["token"] = token
        session["user_id"] = user.id
        session["role"] = user.role
        
        return redirect(url_for("users.lms_dashboard"))
    
    except Exception as e:
        return jsonify({
            "error": "Login failed",
            "details": str(e)
        }), 500

@users_bp.route("/login", methods=["GET"])
def sign_in_page():
    return render_template("login.html")

@users_bp.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

#LMS Dashboard display view
@users_bp.route("/dashboard", methods=["GET"])
def lms_dashboard():
    
    if "user_id" not in session:
        return redirect(url_for("users.sign_in_page"))

    user = User.query.get_or_404(session["user_id"])
    
    courses = []

    if user.role == "student":
        courses = [
            enrollment.course
            for enrollment in user.enrollments
        ]

    elif user.role == "teacher":
        courses = user.courses_taught
    
    total_assignments = sum(
    len(course.assignments)
    for course in courses
    )
    

    return render_template(
        "dashboard.html",
        user=user,
        courses=courses,
        total_assignments=total_assignments
        )

#Reading all the user's info#
@users_bp.route("/secure", methods=["GET"])
@call_auth("teacher")
def secure_users(payload):
    users = User.query.all()
    
    return jsonify([{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
    }for u in users]) 

#Reading one user's info"
@users_bp.route("/<int:user_id>", methods=["GET"])
def secure_user(user_id):
    user = User.query.get_or_404(user_id)
        
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })

#Viewing worload as both student and teacher(jwt connector)#
@users_bp.route("/", methods=["GET"])
@call_auth()
def get_my_profile(payload):
    user = User.query.get(payload["user_id"])

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })
    
#Updating the user's info
@users_bp.route("/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    user.role = data.get("role", user.role)

    db.session.commit()
    return jsonify({"message": "Updated User"})

#Deleting the user's info#
@users_bp.route("/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "Deleted user"})
#Logout#
@users_bp.route("/logout")
def sign_out():
    session.clear()
    return redirect(url_for("users.sign_in_page"))
 
    