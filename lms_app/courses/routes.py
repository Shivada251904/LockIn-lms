from flask import jsonify, request
from . import courses_bp
from lms_app.models import Course, db

#Making the courses#
@courses_bp.route("/", methods=["POST"])
def build_course():
    data = request.json
    course = Course(
        title=data["title"],
        description=data["description"],
        teacher_id=data["teacher_id"]
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({"message": "Created Course", "id": course.id})

#Reading all courses info#
@courses_bp.route('/', methods=["GET"])
def secure_courses():
    courses = Course.query.all()
    return jsonify([{
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "teacher_id": c.teacher_id
    } for c in courses])

#Reading one courses info#
@courses_bp.route('/<int:course_id>', methods=["GET"])
def secure_course(course_id):
    course = Course.query.get_or_404(course_id)
    return jsonify({
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "teacher_id": course.teacher_id
    })

#Updating the courses info#
@courses_bp.route("/<int:course>", methods=["PUT"])
def update_course(course_id):
    course = Course.query.get_or_404(course_id)
    data = request.json
    
    course.title = data.get("title", course.title)
    course.description = data.get("description", course.description)
    course.teacher_id = data.get("teacher_id", course.teacher_id)
    
    db.session.commit()
    return jsonify({"message": "Updated Course"})

#Deleting Courses info#
@courses_bp.route("/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Deleted Course"})