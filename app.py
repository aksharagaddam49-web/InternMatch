from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "internmatch.db"


# =====================================================
# DATABASE
# =====================================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():

    connection = get_db_connection()
    cursor = connection.cursor()

    # Student table
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

    # Internship table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            work_type TEXT NOT NULL,
            min_cgpa REAL NOT NULL,
            eligible_years TEXT NOT NULL,
            required_skills TEXT NOT NULL,
            application_deadline TEXT NOT NULL,
            apply_link TEXT NOT NULL
        )
    """)

    connection.commit()

    # Add sample internships
    sample_internships = [

        (
            "AI / ML Intern",
            "TechNova Solutions",
            "Hyderabad",
            "Hybrid",
            7.0,
            "3rd Year,4th Year",
            "Python,Machine Learning,SQL",
            "2026-09-15",
            "#"
        ),

        (
            "Data Analyst Intern",
            "DataWorks",
            "Remote",
            "Remote",
            7.5,
            "2nd Year,3rd Year,4th Year",
            "Python,SQL,Excel",
            "2026-09-20",
            "#"
        ),

        (
            "Python Developer Intern",
            "CodeCraft Technologies",
            "Bangalore",
            "On-site",
            7.0,
            "3rd Year,4th Year",
            "Python,Flask,SQL",
            "2026-09-25",
            "#"
        ),

        (
            "Web Development Intern",
            "WebSphere Labs",
            "Remote",
            "Remote",
            6.5,
            "2nd Year,3rd Year,4th Year",
            "HTML,CSS,JavaScript",
            "2026-10-01",
            "#"
        ),

        (
            "Machine Learning Intern",
            "InnovateAI",
            "Bangalore",
            "Hybrid",
            8.0,
            "3rd Year,4th Year",
            "Python,Machine Learning,TensorFlow",
            "2026-09-30",
            "#"
        )

    ]

    for internship in sample_internships:

        cursor.execute("""
            INSERT OR IGNORE INTO internships (
                title,
                company,
                location,
                work_type,
                min_cgpa,
                eligible_years,
                required_skills,
                application_deadline,
                apply_link
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, internship)

    connection.commit()
    connection.close()
# =====================================================
# INTERNSHIP MATCHING
# =====================================================

def calculate_match(student, internship):

    # ---------- CGPA CHECK ----------

    student_cgpa = float(student["cgpa"])
    required_cgpa = float(internship["min_cgpa"])

    cgpa_eligible = student_cgpa >= required_cgpa


    # ---------- YEAR CHECK ----------

    student_year = student["current_year"]

    eligible_years = [
        year.strip()
        for year in internship["eligible_years"].split(",")
    ]

    year_eligible = student_year in eligible_years


    # ---------- SKILL CHECK ----------

    student_skills = {
        skill.strip().lower()
        for skill in student["skills"].split(",")
    }

    required_skills = {
        skill.strip().lower()
        for skill in internship["required_skills"].split(",")
    }

    matched_skills = student_skills.intersection(required_skills)

    missing_skills = required_skills - student_skills


    # ---------- SKILL SCORE ----------

    if len(required_skills) > 0:

        skill_score = (
            len(matched_skills)
            / len(required_skills)
        ) * 50

    else:

        skill_score = 50


    # ---------- CGPA SCORE ----------

    cgpa_score = 30 if cgpa_eligible else 0


    # ---------- YEAR SCORE ----------

    year_score = 20 if year_eligible else 0


    # ---------- TOTAL SCORE ----------

    match_score = round(
        cgpa_score +
        year_score +
        skill_score
    )


    # ---------- ELIGIBILITY ----------

    eligible = cgpa_eligible and year_eligible


    return {
        "eligible": eligible,
        "match_score": match_score,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills)
    }

# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================================
# PROFILE
# =====================================================

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

        connection = get_db_connection()

        connection.execute("""
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


# =====================================================
# INTERNSHIPS
# =====================================================
@app.route("/internships")
def internships():

    connection = get_db_connection()

    student = connection.execute("""
        SELECT * FROM students
        ORDER BY id DESC
        LIMIT 1
    """).fetchone()

    internships = connection.execute("""
        SELECT * FROM internships
        ORDER BY application_deadline
    """).fetchall()

    connection.close()

    internship_results = []

    if student:
        for internship in internships:

            match = calculate_match(student, internship)

            internship_results.append({
                "internship": internship,
                "eligible": match["eligible"],
                "match_score": match["match_score"],
                "matched_skills": match["matched_skills"],
                "missing_skills": match["missing_skills"]
            })

    return render_template(
        "internships.html",
        internship_results=internship_results,
        has_profile=student is not None
    )

# =====================================================
# SAVED
# =====================================================

@app.route("/saved")
def saved():

    return """
    <h1>Saved Internships</h1>
    <p>Your saved internships will appear here.</p>
    <a href="/">← Back to Home</a>
    """


# =====================================================
# LOGIN
# =====================================================

@app.route("/login")
def login():

    return """
    <h1>Login</h1>
    <p>Login functionality will be added soon.</p>
    <a href="/">← Back to Home</a>
    """


# =====================================================
# START APPLICATION
# =====================================================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)