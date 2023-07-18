from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"

db = SQLAlchemy(app)

app.app_context().push()

# Declare Model


class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String(30), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=True)
    courses = db.relationship("Course", secondary="enrollments")


class Course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String(30), nullable=False, unique=True)
    course_name = db.Column(db.String(30), nullable=False)
    course_description = db.Column(db.String(30), nullable=True)


class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(
        db.Integer, db.ForeignKey("student.student_id"), nullable=False
    )
    ecourse_id = db.Column(
        db.Integer, db.ForeignKey("course.course_id"), nullable=False
    )


# Declare Flask Routes
@app.route("/")
def home():
    students = Student.query.all()
    return render_template("index.html", students=students)


@app.route("/student/create", methods=["GET", "POST"])
def add_student():
    courses = Course.query.all()
    if request.method == "POST":
        roll_number = request.form.get("r_no")
        first_name = request.form.get("f_name")
        last_name = request.form.get("l_name")

        # Execute Statement
        existing_student = Student.query.filter_by(roll_number=roll_number).first()
        if existing_student:
            return render_template("error.html")
        new_student = Student(
            roll_number=roll_number, first_name=first_name, last_name=last_name
        )
        db.session.add(new_student)
        db.session.commit()  # Commit the student record to get the student_id

        course = request.form.getlist("courses")
        for course_id in course:
            enrollment = Enrollments(
                estudent_id=new_student.student_id, ecourse_id=course_id
            )
            db.session.add(enrollment)

        db.session.commit()
        return redirect("/")
    return render_template("addStudent.html", courses=courses)


@app.route("/student/<int:student_id>/update", methods=["GET", "POST"])
def update_student(student_id):
    students = Student.query.get(student_id)
    courses = Course.query.all()
    if request.method == "POST":
        student = Student.query.get(student_id)
        student.first_name = request.form["f_name"]
        student.last_name = request.form["l_name"]
        db.session.commit()

        # students = Student.query.get(student_id)
        enrollments = Enrollments.query.filter_by(estudent_id=student_id).all()
        course_ids = request.form.getlist("courses")
        # Clear existing enrollments
        for enrollment in enrollments:
            db.session.delete(enrollment)

        for course_id in course_ids:
            enrollment = Enrollments(estudent_id=student_id, ecourse_id=course_id)
            db.session.add(enrollment)
        db.session.commit()
        return redirect("/")
    return render_template(
        "update.html",
        student_id=student_id,
        current_roll=students.roll_number,
        current_f_name=students.first_name,
        current_l_name=students.last_name,
        courses=courses,
    )


@app.route("/student/<int:student_id>/delete")
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        enrollments = Enrollments.query.filter_by(estudent_id=student_id).all()
        
        for enrollment in enrollments:
            db.session.delete(enrollment)
            
        # Delete the student and corresponding enrollments
        db.session.delete(student)
        db.session.commit()
    return redirect(url_for("home"))


@app.route("/student/<int:student_id>")
def student_details(student_id):
    # Retrieve the student and their enrollments from the database
    student = Student.query.get(student_id)
    enrollments = (
        db.session.query(Course)
        .join(Enrollments)
        .filter(Enrollments.estudent_id == student_id)
        .all()
    )
    return render_template("detail.html", student=student, enrollments=enrollments)


if __name__ == "__main__":
    app.run()
