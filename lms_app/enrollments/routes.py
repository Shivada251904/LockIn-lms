from flask import jsonify, request
from . import enrollments_bp
from lms_app.models import Enrollment, db

#Enrolling a student#
@enrollments_bp.route("/", methods=["POST"])
def enroll_student():
    data = request.json
    enrollment = Enrollment(
        student_id=data["student_id"],
        course_id=data["course_id"]
    )
    db.session.add(enrollment)
    db.session.commit()
    return jsonify({"message": "Student enrolled", "id": enrollment})

#Getting all enrollments info#
@enrollments_bp.route("/", methods=["GET"])
def secure_enrollments():
    enrollments = Enrollment.query.all()
    return jsonify([{
        "id": e.id,
        "student_id": e.student_id,
        "course_id": e.course_id
    } for e in enrollments])

#Deleting enrollments info#
@enrollments_bp.route("/<int:enrollment_id>", methods=["DELETE"])
def delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)
    db.session.delete(enrollment)
    db.session.commit()
    return jsonify({"message": "Removed Enrollment"})