from flask import jsonify, request, render_template, session, redirect, url_for
from . import assignments_bp
from lms_app.models import Assignment, db
from lms_app.auth.jwt_utils import call_auth
from datetime import datetime

#Creating assignments info#
@assignments_bp.route("/", methods=["POST"])
@call_auth("teacher")
def build_assignment(payload):
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        required_fields = [
            "course_id",
            "title",
            "description",
            "due_date"
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({
                    "error": f"Missing field: {field}"
                }), 400
        #Avoding crashes in sqlite database with a parse string date alter#
        try:
            parsed_date = datetime.fromisoformat(data["due_date"].replace("Z", ""))
        except ValueError:
            return jsonify({"error": "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400

        assignment = Assignment(
            course_id=data["course_id"],
            title=data["title"],
            description=data["description"],
            due_date=parsed_date
        )

        db.session.add(assignment)
        db.session.commit()

        return jsonify({
            "message": "Created Assignment",
            "id": assignment.id
        }), 201

    except Exception as e:
        db.session.rollback()

        return jsonify({
            "error": "Assignment creation failed",
            "details": str(e)
        }), 500

#Getting all assigments info#
@assignments_bp.route("/", methods=["GET"])
@call_auth()
def secure_assignments(payload):
    assignments = Assignment.query.all()
    return jsonify([{
        "id": a.id,
        "course_id": a.course_id,
        "title": a.title,
        "description": a.description,
        "due_date": a.due_date.isoformat() if a.due_date else None 
    } for a in assignments])

#Updating assignment info#
@assignments_bp.route("/<int:assignment_id>", methods=["PUT"])
@call_auth("teacher")
def update_assignment(payload, assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    assignment.title = data.get("title", assignment.title)
    assignment.description = data.get("description", assignment.description)
    
    if "due_date" in data:
        try:
            assignment.due_date = datetime.fromisoformat(data["due_date"].replace("Z", ""))
        except ValueError:
            return jsonify({"error": "Invalid date format"}), 400
    
    db.session.commit()
    return jsonify({"message": "Updated Assignment"})

#Deleting assignment info#
@assignments_bp.route("/<int:assignment_id>", methods=['DELETE'])
@call_auth("teacher")
def delete_assignment(payload, assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)
    db.session.commit()
    return jsonify({"message": "Deleted Assignment"})

#adding assignment detail route view#
@assignments_bp.route("/view/<int:assignment_id>")
def assignment_page(assignment_id):
    
    if "user_id" not in session:
        return redirect(url_for("users.sign_in_page"))

    assignment = Assignment.query.get_or_404(
        assignment_id
    )

    
    return render_template(
        "assignment_detail.html",
        assignment=assignment
    )