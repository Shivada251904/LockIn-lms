from flask import jsonify, request, session, redirect, url_for
from . import enrollments_bp
from lms_app.models import Enrollment, db
from lms_app.auth.jwt_utils import call_auth

#Enrolling a student#
@enrollments_bp.route("/", methods=["POST"])
def enroll_student():
    
    if "user_id" not in session or session.get("role") != "student":
        return redirect(url_for("users.sign_in_page"))
    
    course_id = request.form.get("course_id")
    
    if not course_id:
        return "Missing course ID", 400
    
    raw_user_id = session["user_id"]
    clean_user_id = raw_user_id[0] if isinstance(raw_user_id, tuple) else int(raw_user_id)
    

    enrollment = Enrollment(
        student_id=clean_user_id,
        course_id=int(course_id)
    )

    db.session.add(enrollment)
    db.session.commit()

    return redirect(
        url_for("users.lms_dashboard")
    )

#Getting all enrollments info#
@enrollments_bp.route("/", methods=["GET"])
@call_auth("student")
def secure_enrollments(payload):
    enrollments = Enrollment.query.all()
    return jsonify([{
        "id": e.id,
        "student_id": e.student_id,
        "course_id": e.course_id
    } for e in enrollments])

#Deleting enrollments info#
@enrollments_bp.route("/<int:enrollment_id>", methods=["DELETE"])
@call_auth("teacher")
def delete_enrollment(payload, enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({"message": "Removed Enrollment"})