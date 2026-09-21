from flask import jsonify, request
from . import submissions_bp
from lms_app.models import Submission, db
from lms_app.auth.jwt_utils import call_auth

#Creating submission info#
@submissions_bp.route("/", methods=["POST"])
def build_submission():
    data = request.json
    
    submission = Submission(
        assignment_id=data["assignment_id"],
        student_id=data["student_id"],
        context=data["context"],
        grade=data.get("grade"),
        submitted_at=data["submitted_at"]
    )
    db.session.add(submission)
    db.session.commit()
    
    return jsonify({"message": "Created Submission", "id": submission.id})

#Submitting assigment's info#
@submissions_bp.route("/submit/<int:assignment_id>", methods=["POST"])
@call_auth("student")
def submit_assignment(payload, assignment_id):
    data = request.json

    submission = Submission(
        assignment_id=assignment_id,
        student_id=payload["user_id"],
        context=data["context"]
    )

    db.session.add(submission)
    db.session.commit()

    return jsonify({"message": "Uploaded Submission"})

#Getting all submissions info#
@submissions_bp.route("/", methods=["GET"])
@call_auth("student")
def secure_submissions(payload):
    submissions = Submission.query.filter_by(student_id=payload["user_id"]).all()
    
    return jsonify([{
        "id": s.id,
        "assignment_id": s.assignment_id,
        "student_id": s.student_id,
        "context": s.context,
        "grade": s.grade,
        "submitted_at": s.submitted_at
    } for s in submissions])

#Getting one submission info#
@submissions_bp.route("/<int:submission_id>", methods=["GET"])
def secure_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    return jsonify({
        "id": submission.id,
        "assignment_id": submission.assignment_id,
        "student_id": submission.student_id,
        "context": submission.context,
        "grade": submission.grade,
        "submitted_at": submission.submitted_at
    })

#Updating submissions info(grading assignments)#
@submissions_bp.route("/grade/<int:submission_id>", methods=["PUT"])
@call_auth("teacher")
def update_submission(submission_id, payload):
    data = request.json
    
    submission = Submission.query.get_or_404(submission_id)
    submission.grade = data.get("grade", submission.grade)
    submission.context = data.get("context", submission.context)
    
    db.session.commit()
    return jsonify({"message": "Graded Submission"})

#Deleting submissions info#
@submissions_bp.route("/<int:submission_id>", methods=["DELETE"])
def delete_submission(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    
    db.session.delete(submission)
    db.session.commit()
    return jsonify({"message": "Submission deleted"})