from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "internmatch.db"


# ---------------- DATABASE ----------------

def init_db():
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            degree TEXT NOT NULL,
            branch TEXT NOT NULL,
            graduation_year INTEGER NOT NULL,
            current_year TEXT NOT NULL,
            cgpa REAL NOT NULL,
            skills TEXT NOT NULL,
            location TEXT,
            work_type TEXT
        )
    """)

    connection.commit()
    connection.close()


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- PROFILE ----------------

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        degree = request.form.get("degree")
        branch = request.form.get("branch")
        graduation_year = request.form.get("graduation_year")
        current_year = request.form.get("current_year")
        cgpa = request.form.get("cgpa")
        skills = request.form.get("skills")
        location = request.form.get("location")
        work_type = request.form.get("work_type")

        connection = sqlite3.connect(DATABASE)

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO students (
                name,
                email,
                degree,
                branch,
                graduation_year,
                current_year,
                cgpa,
                skills,
                location,
                work_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            degree,
            branch,
            graduation_year,
            current_year,
            cgpa,
            skills,
            location,
            work_type
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("profile", saved="true"))

    saved = request.args.get("saved")

    return render_template(
        "profile.html",
        saved=saved
    )


# ---------------- INTERNSHIPS ----------------

@app.route("/internships")
def internships():

    return """
    <h1>Internships</h1>
    <p>Your recommended internships will appear here.</p>
    <a href="/">← Back to Home</a>
    """


# ---------------- SAVED ----------------

@app.route("/saved")
def saved():

    return """
    <h1>Saved Internships</h1>
    <p>Your saved internships will appear here.</p>
    <a href="/">← Back to Home</a>
    """


# ---------------- LOGIN ----------------

@app.route("/login")
def login():

    return """
    <h1>Login</h1>
    <p>Login functionality will be added soon.</p>
    <a href="/">← Back to Home</a>
    """


# ---------------- START APP ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)