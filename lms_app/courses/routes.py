from flask import jsonify, request, render_template, url_for, session, redirect
from . import courses_bp
from lms_app.models import User, Course, db
from lms_app.auth.jwt_utils import call_auth

#Making the courses for students#
@courses_bp.route("/", methods=["POST"])
@call_auth("teacher")
def build_course(payload):
    if "user_id" not in session or session.get("role") != "teacher":
        return redirect(url_for("users.sign_in_page"))
    
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        
        required_entries = [
                    "title",
                    "description",
                    "teacher_id"
                ]
                        
        for entry in required_entries:
            if entry not in data:
                return jsonify({
                    "error": f"Missing entry: {entry}"
                }), 400
        
        course = Course(
            title=data["title"],
            description=data["description"],
            teacher_id=data["teacher_id"]
        )       
        
        db.session.add(course)
        db.session.commit()
        
        if not request.is_json:
            return redirect(url_for("users.lms_dashboard"))
        
        return jsonify({"message": "Created Course", "id": course.id}), 201
    
    except Exception as e:
        db.session.rollback()
        
        return jsonify({
            "error": "Course creation failed",
            "details": str(e)
        }), 500

#Reading all courses info#
@courses_bp.route('/', methods=["GET"])
@call_auth()
def secure_courses(payload):
    courses = Course.query.all()
    return jsonify([{
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "teacher_id": c.teacher_id
    } for c in courses])

#adding course details pageview#
@courses_bp.route("/<int:course_id>")
@call_auth()
def course_page(course_id):
    
    if "user_id" not in session:
        return redirect(url_for("users.sign_in_page"))
    
    course = Course.query.get_or_404(course_id)
    user = User.query.get_or_404(session["user_id"])
    
    return render_template(
        "course_details.html",
        course=course,
        user=user
    )
#adding course template page#
@courses_bp.route("/all", methods=["GET"])
def courses_page():
    
    if "user_id" not in session:
        return redirect(url_for("users.sign_in_page"))

    courses = Course.query.all()

    return render_template(
        "courses.html",
        courses=courses
    )