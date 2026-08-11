from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)
from werkzeug.security import generate_password_hash
from database import get_connection
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import math
from datetime import datetime, date

# ----------------------------------------------------
# Flask Configuration
# ----------------------------------------------------

app = Flask(__name__)
app.secret_key = "studenthub123"

UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ----------------------------------------------------
# HOME PAGE
# ----------------------------------------------------

@app.route("/")
def home():
    return redirect(url_for("student_login"))
@app.route("/home")
def home_page():
    page = request.args.get("page", 1, type=int)
    per_page = 6
    offset = (page - 1) * per_page

    search = request.args.get("search", "").strip()
    category = request.args.get("category", "")
    sort = request.args.get("sort", "upcoming")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT *
        FROM events
        WHERE event_name LIKE %s
    """

    params = [f"%{search}%"]

    if category:
        query += " AND category=%s"
        params.append(category)

    if sort == "latest":
        query += " ORDER BY created_at DESC"
    elif sort == "oldest":
        query += " ORDER BY event_date ASC"
    else:
        query += " ORDER BY event_date ASC"

    count_query = query.replace("*", "COUNT(*) AS total")

    cursor.execute(count_query, params)
    total_events = cursor.fetchone()["total"]

    query += " LIMIT %s OFFSET %s"
    params.extend([per_page, offset])

    cursor.execute(query, params)
    events = cursor.fetchall()

    total_pages = math.ceil(total_events / per_page)

    cursor.execute("""
        SELECT *
        FROM events
        ORDER BY event_date ASC
        LIMIT 3
    """)

    upcoming_events = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "home.html",
        events=events,
        upcoming_events=upcoming_events,
        page=page,
        total_pages=total_pages,
        total_events=total_events,
        search=search,
        category=category,
        sort=sort
    )

# ----------------------------------------------------
# STUDENT SIGNUP
# ----------------------------------------------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = generate_password_hash(request.form["password"])

        roll_no = request.form.get("roll_no", "").strip()
        department = request.form.get("department", "").strip()
        year = request.form.get("year", "").strip()

        # Allow only SVECW email
        if not email.endswith("@svecw.edu.in"):
            flash("Please use your SVECW email address.", "danger")
            return redirect(url_for("signup"))

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if email already exists
        cursor.execute(
            "SELECT id FROM students WHERE email=%s",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()

            flash("Email already registered.", "danger")
            return redirect(url_for("signup"))

        # Insert new student
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students
            (
                full_name,
                email,
                password,
                roll_no,
                department,
                year
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            full_name,
            email,
            password,
            roll_no,
            department,
            year
        ))

        conn.commit()

        cursor.close()
        conn.close()

        flash("Account created successfully!", "success")

        return redirect(url_for("student_login"))

    return render_template("signup.html")

# ----------------------------------------------------
# STUDENT LOGIN
# ----------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def student_login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM students WHERE email=%s",
            (email,)
        )

        student = cursor.fetchone()

        cursor.close()
        conn.close()

        if student and check_password_hash(student["password"], password):

            session.clear()

            session["student_id"] = student["id"]
            session["student_name"] = student["full_name"]

            flash("Login Successful!", "success")

            return redirect(url_for("home_page"))

        flash("Invalid Email or Password.", "danger")

    return render_template("login.html")

# ----------------------------------------------------
# STUDENT DASHBOARD
# ----------------------------------------------------
@app.route("/student_dashboard")
def student_dashboard():
    return redirect(url_for("home_page"))

# ----------------------------------------------------
# PROFILE
# ----------------------------------------------------

@app.route("/profile")
def profile():

    if "student_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("student_login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM students
        WHERE id=%s
        """,
        (session["student_id"],)
    )

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template(
        "profile.html",
        student=student
    )


# ----------------------------------------------------
# STUDENT LOGOUT
# ----------------------------------------------------

@app.route("/student_logout")
def student_logout():
    session.pop("student_id", None)
    session.pop("student_name", None)

    flash("Logged out successfully!", "success")

    return redirect(url_for("student_login"))

# ----------------------------------------------------
# CAMPUS EVENTS
# ----------------------------------------------------

@app.route("/campus-events")
def campus_events():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM events
        WHERE college_name LIKE '%SVECW%'
           OR college_name LIKE '%Shri Vishnu%'
        ORDER BY event_date ASC
    """)

    events = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "campus.html",
        events=events
    )

@app.route("/offcampus-events")
def offcampus_events():

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT *
        FROM events
        WHERE college_name NOT LIKE '%SVECW%'
          AND college_name NOT LIKE '%Shri Vishnu%'
        ORDER BY event_date ASC
    """

    cursor.execute(query)

    events = cursor.fetchall()

    # Debug Output
    print("\n========== OFF CAMPUS EVENTS ==========")
    print("Total Events Found:", len(events))

    for event in events:
        print(event)

    print("=======================================\n")

    cursor.close()
    conn.close()

    return render_template(
        "offcampus.html",
        events=events
    )
# ----------------------------------------------------
# EVENT DETAILS
# ----------------------------------------------------

@app.route("/event/<int:event_id>")
def event_details(event_id):

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT *
        FROM events
        WHERE id=%s
        """,
        (event_id,)
    )

    event = cursor.fetchone()

    cursor.close()
    conn.close()

    if event is None:
        flash("Event not found.", "danger")
        return redirect(url_for("campus_events"))

    return render_template(
        "event_details.html",
        event=event
    )


# ----------------------------------------------------
# ADMIN LOGIN
# ----------------------------------------------------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM admin WHERE username=%s",
            (username,)
        )

        admin = cursor.fetchone()

        cursor.close()
        conn.close()

        if admin and admin["password"] == password:

            session.clear()
            session["admin"] = admin["username"]

            flash("Admin Login Successful!", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid Username or Password.", "danger")

    return render_template("admin_login.html")

# ----------------------------------------------------
# ADMIN DASHBOARD
# ----------------------------------------------------

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        flash("Please login as admin.", "warning")
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Total Events
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM events
    """)
    total_events = cursor.fetchone()["total"]

    # Total Students
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM students
    """)
    total_students = cursor.fetchone()["total"]

    # Upcoming Events
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM events
        WHERE event_date >= CURDATE()
    """)
    upcoming_events = cursor.fetchone()["total"]

    # Category Statistics
    cursor.execute("""
        SELECT
            category,
            COUNT(*) AS total
        FROM events
        GROUP BY category
    """)
    category_stats = cursor.fetchall()

    # Recent Events
    cursor.execute("""
        SELECT *
        FROM events
        ORDER BY created_at DESC
        LIMIT 5
    """)
    events = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "dashboard.html",
        events=events,
        total_events=total_events,
        total_students=total_students,
        upcoming_events=upcoming_events,
        category_stats=category_stats
    )
    



# ----------------------------------------------------
# ADMIN LOGOUT
# ----------------------------------------------------

@app.route("/admin_logout")
def admin_logout():

    session.pop("admin", None)

    flash("Logged out successfully!", "success")

    return redirect(url_for("admin_login"))


# ----------------------------------------------------
# ADD EVENT
# ----------------------------------------------------



@app.route("/add_event", methods=["GET", "POST"])
def add_event():

    if "admin" not in session:
        flash("Please login as admin.", "warning")
        return redirect(url_for("admin_login"))

    if request.method == "POST":

        event_name = request.form["event_name"]
        category = request.form["category"]
        college_name = request.form["college_name"]
        event_date = request.form["event_date"]
        last_date = request.form["last_date"]
        venue = request.form["venue"]
        description = request.form["description"]
        registration_link = request.form["registration_link"]

        # ---------------- DATE VALIDATION ----------------

        event_date_obj = datetime.strptime(event_date, "%Y-%m-%d").date()
        last_date_obj = datetime.strptime(last_date, "%Y-%m-%d").date()
        today = date.today()

        # Event date cannot be before today
        if event_date_obj < today:
            flash("Event date cannot be in the past.", "danger")
            return redirect(url_for("add_event"))

        # Registration last date cannot be before today
        if last_date_obj < today:
            flash("Registration last date cannot be in the past.", "danger")
            return redirect(url_for("add_event"))

        # Registration last date must be before or on the event date
        # Event date must be selected
        if not event_date:
            flash("Please select Event Date first.", "danger")
            return redirect(url_for("add_event"))

# Registration last date must be before or equal to Event Date
        if last_date_obj > event_date_obj:
            flash("Registration Last Date cannot be after the Event Date.", "danger")
            return redirect(url_for("add_event"))

        # ---------------- IMAGE UPLOAD ----------------

        image = request.files.get("image")
        filename = ""

        if image and image.filename:

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        # ---------------- DATABASE INSERT ----------------

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO events
            (
                event_name,
                category,
                college_name,
                event_date,
                last_date,
                venue,
                description,
                registration_link,
                image
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            event_name,
            category,
            college_name,
            event_date,
            last_date,
            venue,
            description,
            registration_link,
            filename
        ))

        conn.commit()

        cursor.close()
        conn.close()

        flash("Event Added Successfully!", "success")

        return redirect(url_for("view_events"))

    return render_template("add_event.html")


# ----------------------------------------------------
# VIEW EVENTS
# ----------------------------------------------------

@app.route("/view_events")
def view_events():

    if "admin" not in session:
        flash("Please login as admin.", "warning")
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM events
        ORDER BY created_at DESC
    """)

    events = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "view_events.html",
        events=events
    )


# ----------------------------------------------------
# EDIT EVENT
# ----------------------------------------------------

@app.route("/edit_event/<int:event_id>", methods=["GET", "POST"])
def edit_event(event_id):

    if "admin" not in session:
        flash("Please login as admin.", "warning")
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":

        event_name = request.form["event_name"]
        category = request.form["category"]
        college_name = request.form["college_name"]
        event_date = request.form["event_date"]
        last_date = request.form["last_date"]
        venue = request.form["venue"]
        description = request.form["description"]
        registration_link = request.form["registration_link"]

        image = request.files.get("image")

        if image and image.filename:

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

            cursor.execute("""
            UPDATE events
            SET
                event_name=%s,
                category=%s,
                college_name=%s,
                event_date=%s,
                last_date=%s,
                venue=%s,
                description=%s,
                registration_link=%s,
                image=%s
            WHERE id=%s
            """,
            (
                event_name,
                category,
                college_name,
                event_date,
                last_date,
                venue,
                description,
                registration_link,
                filename,
                event_id
            ))

        else:

            cursor.execute("""
            UPDATE events
            SET
                event_name=%s,
                category=%s,
                college_name=%s,
                event_date=%s,
                last_date=%s,
                venue=%s,
                description=%s,
                registration_link=%s
            WHERE id=%s
            """,
            (
                event_name,
                category,
                college_name,
                event_date,
                last_date,
                venue,
                description,
                registration_link,
                event_id
            ))

        conn.commit()

        flash("Event Updated Successfully!", "success")

        return redirect(url_for("view_events"))

    cursor.execute(
        "SELECT * FROM events WHERE id=%s",
        (event_id,)
    )

    event = cursor.fetchone()

    cursor.close()
    conn.close()

    if event is None:
        flash("Event not found.", "danger")
        return redirect(url_for("view_events"))

    return render_template(
        "edit_event.html",
        event=event
    )


# ----------------------------------------------------
# DELETE EVENT
# ----------------------------------------------------

@app.route("/delete_event/<int:event_id>")
def delete_event(event_id):

    if "admin" not in session:
        flash("Please login as admin.", "warning")
        return redirect(url_for("admin_login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM events WHERE id=%s",
        (event_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    flash("Event Deleted Successfully!", "success")

    return redirect(url_for("view_events"))


# ----------------------------------------------------
# RUN APPLICATION
# ----------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        use_reloader=False
    )