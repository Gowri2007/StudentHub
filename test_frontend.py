from flask import Flask, render_template

app = Flask(__name__)

events = [
    {
        "id": 1,
        "event_name": "AI Hackathon",
        "category": "Hackathon",
        "college_name": "SVECW",
        "event_date": "2026-07-25",
        "last_date": "2026-07-20",
        "venue": "Main Auditorium",
        "description": "Build AI applications using Python and AWS.",
        "registration_link": "https://example.com",
        "image": None
    },
    {
        "id": 2,
        "event_name": "Coding Contest",
        "category": "Coding",
        "college_name": "IIT Hyderabad",
        "event_date": "2026-08-10",
        "last_date": "2026-08-05",
        "venue": "Online",
        "description": "Competitive programming contest.",
        "registration_link": "https://example.com",
        "image": None
    }
]

student = {
    "name": "Archana",
    "email": "archana@example.com",
    "college": "SVECW",
    "branch": "CSE",
    "year": 3
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/campus")
def campus_events():
    return render_template(
        "campus.html",
        events=events,
        search="",
        category="",
        sort="latest"
    )


@app.route("/event/<int:event_id>")
def event_details(event_id):
    return render_template(
        "event_details.html",
        event=events[0]
    )


@app.route("/student_dashboard")
def student_dashboard():
    return render_template(
        "student_dashboard.html",
        student=student,
        events=events
    )


@app.route("/profile")
def profile():
    return render_template(
        "profile.html",
        student=student
    )


@app.route("/login")
def student_login():
    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)