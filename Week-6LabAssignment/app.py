from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse
from werkzeug.exceptions import HTTPException
from flask_cors import CORS


# Instantiate App
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///api_database.sqlite3"

db = SQLAlchemy(app)
api = Api(app)
CORS(app)

app.app_context().push()

parser = reqparse.RequestParser()
parser.add_argument("roll_number", type=str)
parser.add_argument("first_name", type=str)
parser.add_argument("last_name", type=str)
parser.add_argument("course_id", type=int)
parser.add_argument("course_name", type=str)
parser.add_argument("course_code", type=str)
parser.add_argument("course_description", type=str)


# Declare Model


class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)
    courses = db.relationship("Course", secondary="enrollments")


class Course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String, nullable=False)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_description = db.Column(db.String)


class Enrollment(db.Model):
    __tablename__ = "enrollments"
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    )
    course_id = db.Column(
        db.Integer, db.ForeignKey("course.course_id"), nullable=False
    )


# Error Codes and Messages
class Error(HTTPException):
    def __init__(self, status, code, msg):
        message = {"error_code": code, "error_message": msg}
        self.response = make_response(message, status)


def validate_course_exists(course_id):
    course = Course.query.get(course_id)
    if course is None:
        raise Error(400, "ENROLLMENT001", "Course does not exist")


def validate_student_exists(student_id):
    student = Student.query.get(student_id)
    if student is None:
        raise Error(400, "ENROLLMENT002", "Student does not exist")


def validate_course_data(course_data):
    if not course_data.get("course_name"):
        raise Error(400, "COURSE001", "Course Name is required")
    if not course_data.get("course_code"):
        raise Error(400, "COURSE002", "Course Code is required")


def validate_student_data(student_data):
    if not student_data.get("roll_number"):
        raise Error(400, "STUDENT001", "Roll Number required")
    if not student_data.get("first_name"):
        raise Error(400, "STUDENT002", "First Name required")


class StudentApi(Resource):
    def get(self, student_id):
        student = Student.query.get(student_id)
        if student is not None:
            this_student = {
                "student_id": student.student_id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "roll_number": student.roll_number,
            }
            return this_student
        else:
            return "Student not found", 404

    def put(self, student_id):
        student = Student.query.get(student_id)
        if student:
            student_data = parser.parse_args()
            validate_student_data(student_data)
            student.roll_number = student_data["roll_number"]
            student.first_name = student_data["first_name"]
            student.last_name = student_data.get("last_name")
            db.session.commit()
            return {
                "student_id": student.student_id,
                "first_name": student.first_name,
                "last_name": student.last_name,
                "roll_number": student.roll_number,
            }, 200
        else:
            return "Student not found", 404

    def delete(self, student_id):
        this_student = Student.query.get(student_id)
        if this_student is not None:
            db.session.delete(this_student)
            db.session.commit()
            return "Successfully Deleted", 200
        else:
            return "Student not found", 404

    def post(self):
        student_data = parser.parse_args()
        validate_student_data(student_data)
        student = Student.query.filter_by(
            roll_number=student_data["roll_number"]
        ).first()
        if student is not None:
            return "Student already exist", 409

        new_student = Student(
            first_name=student_data["first_name"],
            last_name=student_data.get("last_name"),
            roll_number=student_data["roll_number"],
        )
        db.session.add(new_student)
        db.session.commit()
        student = Student.query.filter_by(
            roll_number=student_data["roll_number"]
        ).first()
        return {
            "student_id": student.student_id,
            "first_name": student.first_name,
            "last_name": student.last_name,
            "roll_number": student.roll_number,
        }, 201


class CourseApi(Resource):
    def get(self, course_id):
        course = Course.query.get(course_id)
        if course is not None:
            this_course = {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "course_code": course.course_code,
                "course_description": course.course_description,
            }
            return this_course
        else:
            return "Course not found", 404

    def put(self, course_id):
        course = Course.query.get(course_id)
        if course is not None:
            course_data = parser.parse_args()
            validate_course_data(course_data)
            course.course_name = course_data["course_name"]
            course.course_code = course_data["course_code"]
            course.course_description = course_data.get("course_description")
            db.session.commit()
            return {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "course_code": course.course_code,
                "course_description": course.course_description,
            }, 200
        else:
            return "Course not found", 404

    def delete(self, course_id):
        this_course = Course.query.get(course_id)
        if this_course is not None:
            db.session.delete(this_course)
            db.session.commit()
            return "Successfully Deleted", 200
        else:
            return "Course not found", 404

    def post(self):
        course_data = parser.parse_args()
        validate_course_data(course_data)
        course = Course.query.filter_by(course_code=course_data["course_code"]).first()
        if course is not None:
            return "course_code already exist", 409

        new_course = Course(
            course_name=course_data["course_name"],
            course_code=course_data["course_code"],
            course_description=course_data["course_description"],
        )
        db.session.add(new_course)
        db.session.commit()
        course = Course.query.filter_by(course_code=course_data["course_code"]).first()
        return {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "course_code": course.course_code,
            "course_description": course.course_description,
        }, 201


class EnrollmentApi(Resource):
    def get(self, student_id):
        validate_student_exists(student_id)
        enrollments = Enrollment.query.filter_by(student_id=student_id).all()
        if enrollments is not None:
            enrollment_list = []
            for enrollment in enrollments:
                enrollment_list.append({
                    "enrollment_id": enrollment.enrollment_id,
                    "student_id": enrollment.student_id,
                    "course_id": enrollment.course_id,
                })
            return enrollment_list, 200
        else:
            return "Student is not enrolled in any course", 404

    def post(self, student_id):
        validate_student_exists(student_id)
        course_data = parser.parse_args()
        course_id = course_data["course_id"]
        validate_course_exists(course_id)

        new_enrollment = Enrollment(student_id=student_id, course_id=course_id)
        db.session.add(new_enrollment)
        db.session.commit()
        enrollment = Enrollment.query.filter_by(student_id=student_id, course_id=course_id).first()
        return {
            "enrollment_id": enrollment.enrollment_id,
            "student_id": enrollment.student_id,
            "course_id": enrollment.course_id,
        }, 201

    def delete(self, student_id, course_id):
        validate_student_exists(student_id)
        validate_course_exists(course_id)

        enrollment = Enrollment.query.filter_by(
            student_id=student_id, course_id=course_id
        ).first()
        if enrollment:
            db.session.delete(enrollment)
            db.session.commit()
            return "Successfully deleted", 200
        else:
            return "Enrollment for the student not found", 404


api.add_resource(CourseApi, "/api/course/<int:course_id>", "/api/course")
api.add_resource(StudentApi, "/api/student/<int:student_id>", "/api/student")
api.add_resource(
    EnrollmentApi,
    "/api/student/<int:student_id>/course",
    "/api/student/<int:student_id>/course/<int:course_id>",
)

if __name__ == "__main__":
    app.run(debug=True)
