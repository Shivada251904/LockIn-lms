from flask import jsonify, request
from . import assignments_bp
from lms_app.models import Assignment, db
from lms_app.auth.jwt_utils import call_auth

#Creating assignments info#
@assignments_bp.route("/", methods=["POST"])
@call_auth("teacher")
def build_assignment(payload):
    data = request.json
    
    assignment = Assignment(
        course_id=data["course_id"],
        title=data["title"],
        description=data["description"],
        due_date=data["due_date"]
    )
    db.session.add(assignment)
    db.session.commit()
    return jsonify({"message": "Created Assignment", "id": assignment})

#Getting all assigments info#
@assignments_bp.route("/", methods=["GET"])
def secure_assignments():
    assignments = Assignment.query.all()
    return jsonify([{
        "id": a.id,
        "course_id": a.course_id,
        "title": a.title,
        "description": a.description,
        "due_date": a.due_date      
    } for a in assignments])

#Getting one assignment info#
@assignments_bp.route("/<int:assignment_id>", methods=["GET"])
def secure_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    return jsonify({
        "id": assignment.id,
        "course_id": assignment.course_id,
        "title": assignment.title,
        "description": assignment.description,
        "due_date": assignment.due_date
    })

#Updating assignment info#
@assignments_bp.route("/<int:assignment_id>", methods=["PUT"])
def update_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    data = request.json
    
    assignment.title = data.get("title", assignment.title)
    assignment.description = data.get("description", assignment.description)
    assignment.due_date = data.get("due_date", assignment.due_date)
    
    db.session.commit()
    return jsonify({"message": "Updated Assignment"})

#Deleting assignment info#
@assignments_bp.route("/<int:assignment_id>", methods=['DELETE'])
def delete_assignment(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    return jsonify({"message": "Deleted Assignment"})