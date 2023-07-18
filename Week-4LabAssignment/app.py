from flask import Flask, request, render_template
import matplotlib.pyplot as plt

f = open("data.csv", "r") # Open the data file
c = f.readline()  # Skip the header row
c = f.readline()  # Read the first line
d = c.split(",")
data = {}
data["student id"] = [d[0]]
data["course id"] = [d[1]]
data["marks"] = [int(d[2])]

# Read data from the file and store it in the data dictionary
while c != "":
    c = f.readline()
    d = c.split(",")
    if c != "":
        data["student id"].append(d[0])
        new_s = d[1].strip()
        data["course id"].append(new_s)
        new_m = int(d[2].strip())
        data["marks"].append(new_m)
f.close()

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def student_id():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        Id = request.form["ID"]
        #! student_id
        if Id == "student_id":
            Id_value = request.form["id_value"]
            if Id_value in data["student id"]:
                # Filter data based on student id
                list_Student = data["student id"]
                list_Course = data["course id"]
                list_marks = data["marks"]
                total = 0
                a = {"S_id": [], "C_id": [], "marks": []}
                for i in range(len(list_Student)):
                    if list_Student[i] == Id_value:
                        a["S_id"].append(list_Student[i])
                        a["C_id"].append(list_Course[i])
                        a["marks"].append(list_marks[i])
                        total += list_marks[i]
                return render_template("student_id.html", total=total, a=a)
            else:
                return render_template("error.html")
        #! course id
        elif Id == "course_id":
            Id_value = request.form["id_value"]
            if Id_value in data["course id"]:
                # Filter data based on course id
                list_Course = data["course id"]
                list_marks = data["marks"]
                required_marks = []
                for i in range(len(list_Course)):
                    if list_Course[i] == Id_value:
                        required_marks.append(list_marks[i])
                avg = sum(required_marks) / len(required_marks)
                maxi = max(required_marks)
                
                # Create the histogram
                plt.hist(required_marks, bins=5, edgecolor="black")

                # Set labels and title
                plt.ylabel("Frequency")
                plt.xlabel("Marks")

                # Save the plot to a file
                plot_path = "static/histogram.png"
                plt.savefig(plot_path)
                plt.close()

                return render_template(
                    "course_id.html", avg=avg, maxi=maxi, plot_path=plot_path
                )
            else:
                return render_template("error.html")


if __name__ == "__main__":
    app.run()
