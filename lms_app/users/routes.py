from flask import jsonify, request
from . import users_bp
from lms_app.extensions import bcrypt
from lms_app.models import User, db
from lms_app.auth.jwt_utils import build_token, call_auth

#Taking user credentials#
@users_bp.route("/", methods=["POST"])
def build_user():
    data = request.json
    
    #Checking if email is in use and exists#
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email in use, please try again"}), 400
    
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
    
    return jsonify({"message": "Created User", "id": user.id})

#Logging on to the LMS#
@users_bp.route("/login", methods=["POST"])
def sign_in():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    
    if not user:
        return jsonify({"error": "Invalid email"}), 400
    
    if not bcrypt.check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid password"}), 400
    
    token = build_token(user.id, user.role)
    
    return jsonify({
        "message": "Sign in successfull",
        "token": token,
        "user_id": user.id,
        "role": user.role
    })

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
    data = request.json
    
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

#Extra for testing implementation(delete later)#
"""@users_bp.route("/me", methods=["GET"])
@call_auth()
def get_my_profile(payload):
    user = User.query.get(payload["user_id"])

    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })"""


 
    