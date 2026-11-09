from flask import jsonify, request, render_template, session, redirect, url_for, flash
from . import submissions_bp
from lms_app.models import Submission, Assignment, db
from lms_app.auth.jwt_utils import call_auth

#Submitting assigment's info#
@submissions_bp.route("/submit/<int:assignment_id>", methods=["POST"])
@call_auth("student")
def submit_assignment(payload, assignment_id):
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    if "context" not in data:
                return jsonify({
                    "error": "Submission content required"
                }), 400

    submission = Submission(
        assignment_id=assignment_id,
        student_id=payload["user_id"],
        context=data["context"]
    )

    db.session.add(submission)
    db.session.commit()

    return jsonify({"message": "Uploaded Submission"})
    
#Submiting assignments page index#
@submissions_bp.route("/form/<int:assignment_id>", methods=["GET"])
@call_auth("student")
def submit_page(assignment_id):
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("users.sign_in_page"))
    
    if session.get("role") != "student":
        flash("Access Denied: Instructors cannot enter assessment sessions.", "danger")
    return redirect(url_for("users.lms_dashboard"))
    
    assignment = Assignment.query.get_or_404(assignment_id)
    
    return render_template(
        "submit_assignment.html",
        assignment=assignment)

#Viewing grades on assignments#
@submissions_bp.route("/grades", methods=["GET"])
def grades_page():
    
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("users.sign_in_page"))

    submissions = Submission.query.filter_by(student_id=session["user_id"]).all()
    
    return render_template(
        "grades.html",
        submissions=submissions
    )