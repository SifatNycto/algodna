import os
import sqlite3
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "algodna.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key-before-deployment")
app.config["SESSION_PERMANENT"] = False


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                problem_name TEXT NOT NULL,
                platform TEXT NOT NULL,
                topic TEXT NOT NULL,
                difficulty TEXT NOT NULL CHECK (difficulty IN ('Beginner', 'Easy', 'Medium', 'Hard')),
                result TEXT NOT NULL CHECK (result IN ('Solved', 'Attempted')),
                attempts_count INTEGER NOT NULL CHECK (attempts_count >= 1),
                wrong_attempts INTEGER NOT NULL CHECK (wrong_attempts >= 0),
                notes TEXT NOT NULL DEFAULT '',
                solved_at TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_attempts_user ON attempts(user_id)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_attempts_topic ON attempts(user_id, topic)")
        db.execute("CREATE INDEX IF NOT EXISTS idx_attempts_date ON attempts(user_id, solved_at)")


init_db()


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return view(**kwargs)
    return wrapped_view


def current_user_id():
    return session.get("user_id")


def fetch_attempts(user_id):
    with get_db() as db:
        return db.execute(
            "SELECT * FROM attempts WHERE user_id = ? ORDER BY solved_at DESC, id DESC",
            (user_id,)
        ).fetchall()


def build_analytics(rows):
    total = len(rows)
    solved = sum(1 for row in rows if row["result"] == "Solved")
    attempted = total - solved
    wrong = sum(row["wrong_attempts"] for row in rows)
    success_rate = round((solved / total) * 100) if total else 0

    topic_stats = {}
    difficulty_stats = {}
    for row in rows:
        topic = row["topic"]
        topic_stats.setdefault(topic, {"total": 0, "solved": 0, "wrong": 0})
        topic_stats[topic]["total"] += 1
        topic_stats[topic]["solved"] += row["result"] == "Solved"
        topic_stats[topic]["wrong"] += row["wrong_attempts"]

        level = row["difficulty"]
        difficulty_stats.setdefault(level, {"total": 0, "solved": 0})
        difficulty_stats[level]["total"] += 1
        difficulty_stats[level]["solved"] += row["result"] == "Solved"

    topics = []
    for name, data in topic_stats.items():
        rate = round(data["solved"] / data["total"] * 100)
        # Higher score means more attention is likely needed.
        struggle = min(100, round((100 - rate) * 0.7 + min(data["wrong"] * 5, 30)))
        topics.append({
            "name": name, "total": data["total"], "solved": data["solved"],
            "rate": rate, "wrong": data["wrong"], "struggle": struggle
        })
    topics.sort(key=lambda item: (item["struggle"], item["total"]), reverse=True)

    difficulty = []
    order = ["Beginner", "Easy", "Medium", "Hard"]
    for level in order:
        data = difficulty_stats.get(level, {"total": 0, "solved": 0})
        rate = round(data["solved"] / data["total"] * 100) if data["total"] else 0
        difficulty.append({"name": level, "total": data["total"], "rate": rate})

    dates = {row["solved_at"] for row in rows}
    today = date.today()
    active_days = 0
    for offset in range(365):
        day = (today - timedelta(days=offset)).isoformat()
        if day in dates:
            active_days += 1
        elif offset > 0:
            break

    return {
        "total": total, "solved": solved, "attempted": attempted,
        "wrong": wrong, "success_rate": success_rate,
        "topics": topics, "difficulty": difficulty,
        "active_days": active_days
    }


@app.route("/")
@login_required
def index():
    rows = fetch_attempts(current_user_id())
    analytics = build_analytics(rows)
    recent = rows[:6]
    priority_topics = analytics["topics"][:3]
    return render_template(
        "dashboard.html", analytics=analytics, recent=recent,
        priority_topics=priority_topics
    )


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        if not username or not password or not confirmation:
            flash("Please complete every field.", "danger")
            return render_template("register.html")
        if len(username) < 3:
            flash("Username must contain at least 3 characters.", "danger")
            return render_template("register.html")
        if password != confirmation:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")
        if len(password) < 6:
            flash("Use a password with at least 6 characters.", "danger")
            return render_template("register.html")

        try:
            with get_db() as db:
                cursor = db.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                session.clear()
                session["user_id"] = cursor.lastrowid
                session["username"] = username
            flash("Your ALGO DNA profile has been created.", "success")
            return redirect(url_for("index"))
        except sqlite3.IntegrityError:
            flash("That username is already taken.", "danger")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not username or not password:
            flash("Enter your username and password.", "danger")
            return render_template("login.html")

        with get_db() as db:
            user = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        flash("Welcome back. Let's inspect your problem-solving patterns.", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/log", methods=["GET", "POST"])
@login_required
def log_attempt():
    topics = [
        "Arrays", "Strings", "Implementation", "Sorting", "Searching", "Two Pointers",
        "Binary Search", "Recursion", "Backtracking", "Greedy", "Brute Force", 
        "Dynamic Programming", "Graphs", "Trees", "Number Theory",
        "Bit Manipulation", "Data Structures", "Other"
    ]
    if request.method == "POST":
        problem = request.form.get("problem_name", "").strip()
        platform = request.form.get("platform", "").strip()
        topic = request.form.get("topic", "").strip()
        difficulty = request.form.get("difficulty", "")
        result = request.form.get("result", "")
        notes = request.form.get("notes", "").strip()
        solved_at = datetime.strptime(
            request.form.get("solved_at", "").strip(),
            "%d-%m-%Y"
        ).date().isoformat()

        try:
            attempts_count = int(request.form.get("attempts_count", ""))
            wrong_attempts = int(request.form.get("wrong_attempts", ""))
        except ValueError:
            flash("Attempts and wrong attempts must be whole numbers.", "danger")
            return render_template("log.html", topics=topics, today=date.today().isoformat())

        if not all([problem, platform, topic, difficulty, result, solved_at]):
            flash("Please complete all required fields.", "danger")
        elif difficulty not in ["Beginner", "Easy", "Medium", "Hard"]:
            flash("Choose a valid difficulty.", "danger")
        elif result not in ["Solved", "Attempted"]:
            flash("Choose a valid result.", "danger")
        elif attempts_count < 1 or wrong_attempts < 0 or wrong_attempts > attempts_count:
            flash("Attempts must be at least 1; wrong attempts must be zero or more and less than total attempts.", "danger")
        else:
            try:
                datetime.strptime(solved_at, "%Y-%m-%d")
                with get_db() as db:
                    db.execute("""
                        INSERT INTO attempts
                        (user_id, problem_name, platform, topic, difficulty, result,
                         attempts_count, wrong_attempts, notes, solved_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        current_user_id(), problem, platform, topic, difficulty,
                        result, attempts_count, wrong_attempts, notes, solved_at
                    ))
                flash("Problem added to your learning DNA.", "success")
                return redirect(url_for("index"))
            except ValueError:
                flash("Please enter a valid date.", "danger")

    return render_template("log.html", topics=topics, today=date.today().isoformat())


@app.route("/insights")
@login_required
def insights():
    analytics = build_analytics(fetch_attempts(current_user_id()))
    return render_template("insights.html", analytics=analytics)


@app.route("/roadmap")
@login_required
def roadmap():
    analytics = build_analytics(fetch_attempts(current_user_id()))
    if not analytics["topics"]:
        plan = []
        intro = "Log a few practice sessions first. ALGO DNA needs your activity to identify your strongest and weakest topics."
    else:
        plan = []
        for topic in analytics["topics"][:5]:
            if topic["total"] < 2:
                action = "Build a foundation: solve 3 beginner or easy problems and write down the key idea."
            elif topic["rate"] < 50:
                action = "Revisit the core concept, then solve 2 guided examples and 2 independent problems."
            elif topic["wrong"] >= 3:
                action = "Focus on debugging: review wrong attempts and explain the corrected approach in your own words."
            else:
                action = "Maintain momentum: solve one medium problem and one timed challenge."
            plan.append({"topic": topic["name"], "rate": topic["rate"], "action": action})
        intro = "Your practice priorities are ranked using your recorded solve rate, activity volume, and wrong-attempt patterns."
    return render_template("roadmap.html", plan=plan, intro=intro)


@app.route("/delete/<int:attempt_id>", methods=["POST"])
@login_required
def delete_attempt(attempt_id):
    with get_db() as db:
        db.execute(
            "DELETE FROM attempts WHERE id = ? AND user_id = ?",
            (attempt_id, current_user_id())
        )
    flash("Practice record deleted.", "info")
    return redirect(request.referrer or url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
