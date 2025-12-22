import os

from cs50 import SQL
from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date, timedelta

app = Flask(__name__)

# Configure sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to database
db = SQL("sqlite:///swims.db")

@app.context_processor
def inject_year():
    return {"year": datetime.now().year}
# updates the years of the app through datetime

# Authentification Routes: Register, Log-in, Log-out, Forgot-Password
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        age = request.form.get("age")
        club_team = request.form.get("club_team")
        hometown = request.form.get("hometown")

        if password != confirmation:
            return ("passwords do not match")

        # Check if username exists
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 0:
            return ("username already exists")

        # Hash password and insert into DB
        hashed_pass = generate_password_hash(password)
        db.execute("INSERT INTO users(name, username, hash, age, club_team, hometown) VALUES(?,?,?,?,?,?)", name, username, hashed_pass, age, club_team, hometown)

        # Log in user
        userID = db.execute("SELECT id FROM users WHERE username = ?", username)[0]["id"]
        session["user_id"] = userID

        return redirect("/")
    else:
        return render_template("register.html")

# Login route for users
@app.route("/login", methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

# Logout route for users and used from finance app.py
@app.route("/logout")
def logout():
    """Logs the user out"""
    session.clear()
    # Redirect user to login form
    return redirect("/")

# forgot password for users
@app.route("/reset_pass", methods=["GET", "POST"])
def reset_pass():
    if request.method == "POST":
        username = request.form.get("username")
        old_pass = request.form.get("old_password")
        new_pass = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Basic validation
        if not username or not old_pass or not new_pass or not confirmation:
            return "Please fill out all fields."
        if new_pass != confirmation:
            return "Passwords do not match."

        # Check if username exists
        user = db.execute("SELECT id, hash FROM users WHERE username = ?", username)
        if len(user) != 1:
            return "Username not found."

        # Verify old password
        if not check_password_hash(user[0]["hash"], old_pass):
            return "Old password is incorrect."

        # Update password
        new_hashed = generate_password_hash(new_pass)
        db.execute("UPDATE users SET hash = ? WHERE id = ?", new_hashed, user[0]["id"])

        return redirect("/login")  # Redirect back to login after reset

    else:
        return render_template("reset_pass.html")


# ROUTES for pages
# ---- HOME DASHBOARD ----
@app.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    current = session["user_id"]
    # will get the current date(today), will be used for summary/streak
    today = date.today()

    #get the variables(greet, streak, distance, total_lifts, soreness) to pass into html
    # name of the user:
    name = db.execute("SELECT name FROM users WHERE id = ?", current)
    name = name[0]["name"] if name else "User"

    # gets 4 diff dates from all tables
    total_days = db.execute("""SELECT date FROM lifts WHERE user_id = ?
                         UNION
                         SELECT date FROM swims WHERE user_id = ?
                         UNION
                         SELECT date FROM races WHERE user_id = ?
                         UNION
                         SELECT date FROM recovery WHERE user_id = ?
                         ORDER BY date ASC
                         """, current, current, current, current)
    training_days = db.execute("""SELECT date FROM lifts WHERE user_id = ?
                         UNION
                         SELECT date FROM swims WHERE user_id = ?
                         UNION
                         SELECT date FROM races WHERE user_id = ?
                         ORDER BY date ASC
                         """, current, current, current)
    # parse_dates takes a specific day(from the query) and turns it into a year,month,day for each query
    def parse_dates(query_result):
        days = []
        for entry in query_result:
            if entry["date"]:
                day = datetime.strptime(entry["date"], "%Y-%m-%d").date()
                days.append(day)
        return days
    # then will take each query(totaxl and training) and will run them through the parse_dates function
    training_days = parse_dates(training_days)
    total_days = parse_dates(total_days)

    # now we need to actually record the streaks

    # creates a function to count/reset streaks
    def streak_counter(days):
        # creates 2 streak variables
        current_streak = 0
        prev_day = None
        # starts the streak
        for day in days:
            if prev_day is None:
                current_streak = 1
            # increases the streak
            elif day == prev_day + timedelta(days=1):
                current_streak += 1
            # resets the streak
            else:
                current_streak = 1
            # updates the day from the loop
            prev_day = day
        # updates the streak for today
        streak_today = current_streak if prev_day == date.today() else 0

        # returns the streak
        return streak_today
    # checks streaks for both types
    training_streak = streak_counter(training_days)
    total_streak = streak_counter(total_days)


    # =======================now creating summary chart============================
    # creates start/end days
    start = today - timedelta(days=6) # timedelta(duration of time(imported from time) difference between 2 dates)
    end = today
    # makes them into strings to compare
    start_str = start.strftime("%Y-%m-%d")
    end_str = end.strftime("%Y-%m-%d")

    # creates variable queries for 3 items(distance,lifts,soreness)
    dist = db.execute("SELECT SUM(distance) AS total_dist FROM swims WHERE user_id = ? AND date BETWEEN ? AND ?", current, start_str, end_str)[0]["total_dist"]
    lifts = db.execute("SELECT COUNT(DISTINCT date) AS total_lifts FROM lifts WHERE user_id = ? AND date BETWEEN ? AND ?", current, start_str, end_str)[0]["total_lifts"]
    sore = db.execute("SELECT AVG(soreness) AS avg_soreness FROM recovery WHERE user_id = ? AND date BETWEEN ? AND ?", current, start_str, end_str)[0]["avg_soreness"]

    dist = dist or 0
    lifts = lifts or 0
    sore = sore or 0
    # then will render vairables to the dash.html
    return render_template("dash.html",
                            name=name,
                            training_streak=training_streak,
                            total_streak=total_streak,
                            total_dist = dist,
                            total_lifts = lifts,
                            avg_soreness = sore
                            )

# ---- PROFILE PAGE/EDIT PROFILE ----
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect("/login")
    # makes sure the user is registred and logged in

    current = session["user_id"]

    stats = db.execute(
        "SELECT name, username, age, club_team, hometown FROM users WHERE id = ?",
        current
    )
    if len(stats) != 1:
        return "Error: User not found"
       # makes sure the user actually has status
    row = stats[0]

    # gets the user's data for the profile page
    return render_template(
        "profile.html",
        name = row["name"],
        age = row["age"],
        username = row["username"],
        club_team = row["club_team"],
        hometown = row["hometown"]
        )

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if "user_id" not in session:
        return redirect("/login")
    current = session["user_id"]

    if request.method == "POST":
        # Get updated form values
        name = request.form.get("name")
        age = request.form.get("age")
        club_team = request.form.get("club_team")
        hometown = request.form.get("hometown")

        # Update the user in the database
        db.execute("UPDATE users SET name = ?, age = ?, club_team = ?, hometown = ? WHERE id = ?",
                    name, age, club_team, hometown, current)

        return redirect(url_for("profile"))

    else:
        # GET: fetch current user info to prefill the form
        user = db.execute("SELECT name, age, club_team, hometown FROM users WHERE id = ?", current)[0]

        return render_template(
            "edit_profile.html",
            name=user["name"],
            age=user["age"],
            club_team=user["club_team"],
            hometown=user["hometown"]
        )


# creates a route to send data to chart.js to create progression charts
# ---- PROGRESSION PAGES ----
@app.route("/progression")
def progression():
    # checks if the user is logged in, if not redirect to login
    if "user_id" not in session:
        return redirect("/login")
    current = session["user_id"]

    # Chart.js integration and JSON route structure adapted with help from ChatGPT (for learning purposes)

    # ---- Branch 1: JSON data request for chart.js ----
    # will AJAX a JSON file to send to chart.js to create a chart of an event requested by the user
    if request.args.get("format") == "json":
        # creates a request that sends specific data to chart.js
        event = request.args.get("event")
        # later defined through an HTML select

        # retrieves all races for this user and event, sorted by date
        rows = db.execute("""
            SELECT date, time
            FROM races
            WHERE user_id = ? AND event = ?
            ORDER BY date
        """, current, event)
        # now gets the time and date for charts

        # converts times into seconds for an accurate progression approach
        def to_seconds(t):
            # "1:03.25" -> 63.25 ; "59.87" -> 59.87
            if not t:
                return None
            parts = t.split(":")  # since time is already imported, it uses t.split
            if len(parts) == 1:
                return float(parts[0])  # SS.xx
            # makes the time a float because milliseconds matter in swimming
            mins = int(parts[0])
            secs = float(parts[1])
            return mins * 60 + secs  # returns the time in total seconds

        # create lists of dates and converted times for Chart.js
        labels = [r["date"] for r in rows]  # e.g., ["2025-10-10","2025-11-01",...]
        values = [to_seconds(r["time"]) for r in rows]  # e.g., [63.5, 62.9, 62.2]

        # jsonify the data to be sent into chart.js
        return jsonify({"labels": labels, "values": values})

    # ---- Branch 2: regular page render ----
    # allows the user to see their events through the HTML dropdown to track their progression
    events = db.execute("""
        SELECT DISTINCT event
        FROM races
        WHERE user_id = ?
        ORDER BY event
    """, current)

    return render_template("progression.html", events=events)


@app.route("/add_lift", methods=["GET", "POST"])
def add_lift():
    if "user_id" not in session:
        return redirect("/login")
    current = session["user_id"]
    # checks for user validity and then gets data

    if request.method == "POST":
        # required forms:
        date = request.form.get("date")
        exercise = request.form.get("exercise")
        sets = int(request.form.get("sets") or 0)
        reps = int(request.form.get("reps") or 0)

        # non required forms:
        weight = float(request.form.get("weight")) if request.form.get("weight") else None
        muscle_group = request.form.get("muscle_group") or None
        rpe = float(request.form.get("rpe")) if request.form.get("rpe") else None
        notes = request.form.get("notes") or None

        db.execute(
            """INSERT INTO lifts
               (user_id, date, exercise, sets, reps, weight, muscle_group, rpe, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            current, date, exercise, sets, reps, weight, muscle_group, rpe, notes
        )

        return redirect(url_for("progression"))

    return render_template("add_lift.html")

# ---- ADD SWIM ----
@app.route("/add_swim", methods=["GET", "POST"])
def add_swim():
    if "user_id" not in session:
        return redirect("/login")
    current = session["user_id"]
    # checks for user validity and then gets data

    if request.method == "POST":
        # required forms:
        date = request.form.get("date")
        stroke = request.form.get("stroke")
        distance = int(request.form.get("distance"))
        pool = request.form.get("pool")
        duration = float(request.form.get("duration"))
        difficulty = int(request.form.get("difficulty"))

        # non required forms:
        notes = request.form.get("notes") or None

        db.execute(
            """INSERT INTO swims
            (user_id, date, distance, stroke, duration, pool, difficulty, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            current, date, distance, stroke, duration, pool, difficulty, notes
        )

        return redirect(url_for("progression"))

    return render_template("add_swim.html")

# ---- ADD MEET ----
@app.route("/add_meet", methods=["GET", "POST"])
def add_meet():
    if "user_id" not in session:
        return redirect("/login")
    current = session["user_id"]
    # checks for user validity and then gets data

    if request.method == "POST":
        # required forms:
        date = request.form.get("date")
        event = request.form.get("event")
        time = request.form.get("time")
        meet = request.form.get("meet")
        race_round = request.form.get("round")

        # non required forms:
        notes = request.form.get("notes") or None

        db.execute(
            """INSERT INTO races
               (user_id, date, event, time, meet, round, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            current, date, event, time, meet, race_round, notes
        )
        # 1. Get data from form (meet name, date, result, notes)
        # 2. Insert into 'progression' table with type='meet'
        return redirect(url_for("progression"))
    return render_template("add_meet.html")

# ---- RECOVERY PAGE ----
@app.route("/recovery", methods=["GET", "POST"])
def recovery():
    if "user_id" not in session:
        return redirect("/login")
    current = session["user_id"]

    if request.method == "POST":
        # required forms
        date = request.form.get("date")
        sleep = float(request.form.get("sleep"))
        fatigue = request.form.get("fatigue")
        soreness = request.form.get("soreness")
        stress = request.form.get("stress")
        # non-required(notes)
        notes = request.form.get("notes") or None

        db.execute(
            """INSERT INTO recovery
               (user_id, date, sleep_hours, fatigue, soreness, stress, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            current, date, sleep, fatigue, soreness, stress, notes
        )
        return redirect("/recovery")
    return render_template("recovery.html")

# ----- Index: Show user's full training record --------
@app.route("/index")
def index():
    if "user_id" not in session:
        return redirect("/login")

    current = session["user_id"]

    lifts = db.execute("SELECT id, date, exercise, sets, reps, weight, muscle_group, rpe, notes FROM lifts WHERE user_id = ?", current)
    swims = db.execute("SELECT id, date, distance, pool, stroke, duration, difficulty, notes FROM swims WHERE user_id = ?", current)
    races = db.execute("SELECT id, date, event, time, meet, round, notes FROM races WHERE user_id = ?", current)

    return render_template("index.html", lifts=lifts, swims=swims, races=races)

# ---- EDIT LIFT ----
@app.route("/edit_lift/<int:lift_id>", methods=["GET", "POST"])
def edit_lift(lift_id):
    if "user_id" not in session:
        return redirect("/login")
    current = session["user_id"]

    if request.method == "POST":
        date = request.form.get("date")
        exercise = request.form.get("exercise")
        sets = request.form.get("sets")
        reps = request.form.get("reps")
        weight = request.form.get("weight")
        muscle_group = request.form.get("muscle_group")
        rpe = request.form.get("rpe")
        notes = request.form.get("notes")

        db.execute("""
            UPDATE lifts
            SET date = ?, exercise = ?, sets = ?, reps = ?, weight = ?, muscle_group = ?, rpe = ?, notes = ?
            WHERE id = ? AND user_id = ?
        """, date, exercise, sets, reps, weight, muscle_group, rpe, notes, lift_id, current)

        return redirect(url_for("index"))

    row = db.execute("""
        SELECT id, date, exercise, sets, reps, weight, muscle_group, rpe, notes
        FROM lifts
        WHERE id = ? AND user_id = ?
    """, lift_id, current)

    if len(row) != 1:
        return "Lift not found", 404

    return render_template("edit_lift.html", lift=row[0])


# ---- EDIT SWIM ----
@app.route("/edit_swim/<int:swim_id>", methods=["GET", "POST"])
def edit_swim(swim_id):
    if "user_id" not in session:
        return redirect("/login")
    current = session["user_id"]

    if request.method == "POST":
        date = request.form.get("date")
        distance = request.form.get("distance")
        pool = request.form.get("pool")
        stroke = request.form.get("stroke")
        duration = request.form.get("duration")
        difficulty = request.form.get("difficulty")
        notes = request.form.get("notes")

        db.execute("""
            UPDATE swims
            SET date = ?, distance = ?, pool = ?, stroke = ?, duration = ?, difficulty = ?, notes = ?
            WHERE id = ? AND user_id = ?
        """, date, distance, pool, stroke, duration, difficulty, notes, swim_id, current)

        return redirect(url_for("index"))

    row = db.execute("""
        SELECT id, date, distance, pool, stroke, duration, difficulty, notes
        FROM swims
        WHERE id = ? AND user_id = ?
    """, swim_id, current)

    if len(row) != 1:
        return "Swim not found", 404

    return render_template("edit_swim.html", swim=row[0])


# ---- EDIT RACE ----
@app.route("/edit_race/<int:race_id>", methods=["GET", "POST"])
def edit_race(race_id):
    if "user_id" not in session:
        return redirect("/login")
    current = session["user_id"]

    if request.method == "POST":
        date = request.form.get("date")
        event = request.form.get("event")
        time = request.form.get("time")
        meet = request.form.get("meet")
        round_ = request.form.get("round")
        notes = request.form.get("notes")

        db.execute("""
            UPDATE races
            SET date = ?, event = ?, time = ?, meet = ?, round = ?, notes = ?
            WHERE id = ? AND user_id = ?
        """, date, event, time, meet, round_, notes, race_id, current)

        return redirect(url_for("index"))

    row = db.execute("""
        SELECT id, date, event, time, meet, round, notes
        FROM races
        WHERE id = ? AND user_id = ?
    """, race_id, current)

    if len(row) != 1:
        return "Race not found", 404

    return render_template("edit_race.html", race=row[0])

@app.route("/delete", methods=["POST"])
def delete_event():
    if "user_id" not in session:
        return redirect("/login")

    current = session["user_id"]

    entry_type = request.form.get("type")
    entry_id = request.form.get("id")

    table_map = {
        "lift": "lifts",
        "swim": "swims",
        "race": "races",
    }

    if entry_type not in table_map or not entry_id:
        return "Invalid delete request", 400

    table = table_map[entry_type]

    db.execute(f"DELETE FROM {table} WHERE id = ? AND user_id = ?", entry_id, current)

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
