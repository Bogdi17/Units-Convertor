import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    """Start page"""
    return render_template("index.html")


@app.route("/improve", methods=["GET", "POST"])
@login_required
def improve():
    """Improve"""
    user_id = session["user_id"]
    if request.method =="POST":
        if not request.form.get("topic"):
            return apology("you must enter a topic")
        elif not request.form.get("content"):
            return apology("you must enter your ideas")
        
        topic = request.form.get("topic")
        content = request.form.get("content")
        db.execute("INSERT INTO improvements (user_id, topic, content) VALUES(?, ?, ?)",
                   user_id, topic, content)

        flash("Thanks for your suggestion!")
        return render_template("improve.html")
    else:
        return render_template("improve.html")


@app.route("/help")
def help():
    """Help page"""
    return render_template("help.html")


@app.route("/units")
def units():
    """Help page"""
    return render_template("units.html")


@app.route("/history")
@login_required
def history():
    """Show history of converts"""
    user_id = session["user_id"]
    converts = db.execute(
        "SELECT * FROM converts WHERE user_id = ? ORDER BY timestamp DESC", user_id)
    return render_template("history.html", converts=converts)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Give me a username", 400)
        elif not request.form.get("password"):
            return apology("Give me a password", 400)
        elif not request.form.get("confirmation"):
            return apology("Give me password confirmation", 400)
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Give me passwords that match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 0:
            return apology("Give me a usename that doesn't already exists", 400)
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/weight", methods=["GET", "POST"])
def weight():
    """Convert weight."""
    user_id = session["user_id"]
    if request.method == "POST":
        input_unit = request.form.get("input_unit")
        output_unit = request.form.get("output_unit")
        input = request.form.get("input")

        if not input_unit or not output_unit:
            return apology("must give input unit and output unit")
        elif not input:
            return apology("must give input")
        else:
            input = int(input)

        #gigagram
        if input_unit == "gigagram":
            if output_unit == "gigagram":
                output = input
            elif output_unit == "tone":
                output = input * 1000
            elif output_unit == "quintal":
                output = input * 10000
            elif output_unit == "kg":
                output = input * 1000000
            elif output_unit == "lbs":
                output = input * 2205000
            elif output_unit == "hectogram":
                output = input * 10000000
            elif output_unit == "decagram":
                output = input * 100000000
            elif output_unit == "gram":
                output = input * 1000000000
            elif output_unit == "decigram":
                output = input * 10000000000
            elif output_unit == "centigram":
                output = input * 100000000000
            else:
                output = input * 1000000000000

        #tone
        if input_unit == "tone":
            if output_unit == "gigagram":
                output = input / 1000
            elif output_unit == "tone":
                output = input
            elif output_unit == "quintal":
                output = input * 10
            elif output_unit == "kg":
                output = input * 1000
            elif output_unit == "lbs":
                output = input * 2205
            elif output_unit == "hectogram":
                output = input * 10000
            elif output_unit == "decagram":
                output = input * 100000
            elif output_unit == "gram":
                output = input * 1000000
            elif output_unit == "decigram":
                output = input * 10000000
            elif output_unit == "centigram":
                output = input * 100000000
            else:
                output = input * 1000000000


        #quintal
        if input_unit == "quintal":
            if output_unit == "gigagram":
                output = input / 10000
            elif output_unit == "tone":
                output = input / 10
            elif output_unit == "quintal":
                output = input
            elif output_unit == "kg":
                output = input * 100
            elif output_unit == "lbs":
                output = input * 220.5
            elif output_unit == "hectogram":
                output = input * 1000
            elif output_unit == "decagram":
                output = input * 10000
            elif output_unit == "gram":
                output = input * 100000
            elif output_unit == "decigram":
                output = input * 1000000
            elif output_unit == "centigram":
                output = input * 10000000
            else:
                output = input * 100000000


        #kg
        if input_unit == "kg":
            if output_unit == "gigagram":
                output = input / 1000000
            elif output_unit == "tone":
                output = input / 1000
            elif output_unit == "quintal":
                output = input / 100
            elif output_unit == "kg":
                output = input
            elif output_unit == "lbs":
                output = input * 2.205
            elif output_unit == "hectogram":
                output = input * 10
            elif output_unit == "decagram":
                output = input * 100
            elif output_unit == "gram":
                output = input * 1000
            elif output_unit == "decigram":
                output = input * 10000
            elif output_unit == "centigram":
                output = input * 100000
            else:
                output = input * 1000000


        #hectogram
        if input_unit == "hectogram":
            if output_unit == "gigagram":
                output = input / 10000000
            elif output_unit == "tone":
                output = input / 10000
            elif output_unit == "quintal":
                output = input / 1000
            elif output_unit == "kg":
                output = input / 10
            elif output_unit == "lbs":
                output = input / 4.536
            elif output_unit == "hectogram":
                output = input
            elif output_unit == "decagram":
                output = input * 10
            elif output_unit == "gram":
                output = input * 100
            elif output_unit == "decigram":
                output = input * 1000
            elif output_unit == "centigram":
                output = input * 10000
            else:
                output = input * 100000


        #decagram
        if input_unit == "decagram":
            if output_unit == "gigagram":
                output = input / 100000000
            elif output_unit == "tone":
                output = input / 100000
            elif output_unit == "quintal":
                output = input / 10000
            elif output_unit == "kg":
                output = input / 100
            elif output_unit == "lbs":
                output = input / 45.36
            elif output_unit == "hectogram":
                output = input / 10
            elif output_unit == "decagram":
                output = input
            elif output_unit == "gram":
                output = input * 10
            elif output_unit == "decigram":
                output = input * 100
            elif output_unit == "centigram":
                output = input * 1000
            else:
                output = input * 10000


        #gram
        if input_unit == "gram":
            if output_unit == "gigagram":
                output = input / 1000000000
            elif output_unit == "tone":
                output = input / 1000000
            elif output_unit == "quintal":
                output = input / 100000
            elif output_unit == "kg":
                output = input / 1000
            elif output_unit == "lbs":
                output = input / 453.6
            elif output_unit == "hectogram":
                output = input / 100
            elif output_unit == "decagram":
                output = input / 10
            elif output_unit == "gram":
                output = input
            elif output_unit == "decigram":
                output = input * 10
            elif output_unit == "centigram":
                output = input * 100
            else:
                output = input * 1000


        #decigram
        if input_unit == "decigram":
            if output_unit == "gigagram":
                output = input / 10000000000
            elif output_unit == "tone":
                output = input / 10000000
            elif output_unit == "quintal":
                output = input / 1000000
            elif output_unit == "kg":
                output = input / 10000
            elif output_unit == "lbs":
                output = input / 4536
            elif output_unit == "hectogram":
                output = input / 1000
            elif output_unit == "decagram":
                output = input / 100
            elif output_unit == "gram":
                output = input / 10
            elif output_unit == "decigram":
                output = input
            elif output_unit == "centigram":
                output = input * 10
            else:
                output = input * 100


        #centigram
        if input_unit == "centigram":
            if output_unit == "gigagram":
                output = input / 100000000000
            elif output_unit == "tone":
                output = input / 100000000
            elif output_unit == "quintal":
                output = input / 10000000
            elif output_unit == "kg":
                output = input / 100000
            elif output_unit == "lbs":
                output = input / 45360
            elif output_unit == "hectogram":
                output = input / 10000
            elif output_unit == "decagram":
                output = input / 1000
            elif output_unit == "gram":
                output = input / 100
            elif output_unit == "decigram":
                output = input / 10
            elif output_unit == "centigram":
                output = input
            else:
                output = input * 10

        #mg
        if input_unit == "mg":
            if output_unit == "gigagram":
                output = input / 1000000000000
            elif output_unit == "tone":
                output = input / 1000000000
            elif output_unit == "quintal":
                output = input / 100000000
            elif output_unit == "kg":
                output = input / 1000000
            elif output_unit == "lbs":
                output = input / 453600
            elif output_unit == "hectogram":
                output = input / 100000
            elif output_unit == "decagram":
                output = input / 10000
            elif output_unit == "gram":
                output = input / 1000
            elif output_unit == "decigram":
                output = input / 100
            elif output_unit == "centigram":
                output = input / 10
            else:
                output = input

        #lbs
        if input_unit == "lbs":
            if output_unit == "gigagram":
                output = input / 2205000
            elif output_unit == "tone":
                output = input / 2205
            elif output_unit == "quintal":
                output = input / 220.5
            elif output_unit == "kg":
                output = input / 2.205
            elif output_unit == "lbs":
                output = input
            elif output_unit == "hectogram":
                output = input * 4.536
            elif output_unit == "decagram":
                output = input * 45.36
            elif output_unit == "gram":
                output = input * 453.6
            elif output_unit == "decigram":
                output = input * 4536
            elif output_unit == "centigram":
                output = input * 45360
            else:
                output = input * 453600

        db.execute("INSERT INTO converts (user_id, input, output, input_unit, output_unit) VALUES(?, ?, ?, ?, ?)",
                   user_id, input, output, input_unit, output_unit)

        flash(f"You converted {input} {input_unit} to {output} {output_unit}.")
        return render_template("weight.html")
    else:
        return render_template("weight.html")


@app.route("/distance", methods=["GET", "POST"])
def distance():
    """Convert distance."""
    user_id = session["user_id"]
    if request.method == "POST":
        input_unit = request.form.get("input_unit")
        output_unit = request.form.get("output_unit")
        input = request.form.get("input")

        if not input_unit or not output_unit:
            return apology("must give input unit and output unit")
        elif not input:
            return apology("must give input")
        else:
            input = int(input)

        #mile
        if input_unit == "mile":
            if output_unit == "km":
                output = input * 1.609
            elif output_unit == "hm":
                output = input * 16.09
            elif output_unit == "dam":
                output = input * 160.9
            elif output_unit == "m":
                output = input * 1609
            elif output_unit == "dm":
                output = input * 16090
            elif output_unit == "cm":
                output = input * 160900
            elif output_unit == "mm":
                output = input * 1609000
            elif output_unit == "micrometre":
                output = input * 1609000000
            elif output_unit == "yard":
                output = input * 1760
            elif output_unit == "foot":
                output = input * 5280
            elif output_unit == "inch":
                output = input * 63360
            else:
                output = input


        #km
        elif input_unit == "km":
            if output_unit == "km":
                output = input
            elif output_unit == "hm":
                output = input * 10
            elif output_unit == "dam":
                output = input * 100
            elif output_unit == "m":
                output = input * 1000
            elif output_unit == "dm":
                output = input * 10000
            elif output_unit == "cm":
                output = input * 100000
            elif output_unit == "mm":
                output = input * 1000000
            elif output_unit == "micrometre":
                output = input * 1000000000
            elif output_unit == "yard":
                output = input * 1093.61
            elif output_unit == "foot":
                output = input * 3280.84
            elif output_unit == "inch":
                output = input * 39370.1
            else:
                output = input / 1.609

        #hm
        elif input_unit == "hm":
            if output_unit == "km":
                output = input / 10
            elif output_unit == "hm":
                output = input
            elif output_unit == "dam":
                output = input * 10
            elif output_unit == "m":
                output = input * 100
            elif output_unit == "dm":
                output = input * 1000
            elif output_unit == "cm":
                output = input * 10000
            elif output_unit == "mm":
                output = input * 100000
            elif output_unit == "micrometre":
                output = input * 100000000
            elif output_unit == "yard":
                output = input * 109.361
            elif output_unit == "foot":
                output = input * 328.084
            elif output_unit == "inch":
                output = input * 3937.01
            else:
                output = input / 16.093


        #dam
        elif input_unit == "dam":
            if output_unit == "km":
                output = input / 100
            elif output_unit == "hm":
                output = input / 10
            elif output_unit == "dam":
                output = input
            elif output_unit == "m":
                output = input * 10
            elif output_unit == "dm":
                output = input * 100
            elif output_unit == "cm":
                output = input * 1000
            elif output_unit == "mm":
                output = input * 10000
            elif output_unit == "micrometre":
                output = input * 10000000
            elif output_unit == "yard":
                output = input * 10.9361
            elif output_unit == "foot":
                output = input * 32.8084
            elif output_unit == "inch":
                output = input * 393.701
            else:
                output = input / 160.93


        #m
        elif input_unit == "m":
            if output_unit == "km":
                output = input / 1000
            elif output_unit == "hm":
                output = input / 100
            elif output_unit == "dam":
                output = input / 10
            elif output_unit == "m":
                output = input
            elif output_unit == "dm":
                output = input * 10
            elif output_unit == "cm":
                output = input * 100
            elif output_unit == "mm":
                output = input * 1000
            elif output_unit == "micrometre":
                output = input * 1000000
            elif output_unit == "yard":
                output = input * 1.09361
            elif output_unit == "foot":
                output = input * 3.28084
            elif output_unit == "inch":
                output = input * 39.3701
            else:
                output = input / 1609.3


        #dm
        elif input_unit == "dm":
            if output_unit == "km":
                output = input / 10000
            elif output_unit == "hm":
                output = input / 1000
            elif output_unit == "dam":
                output = input / 100
            elif output_unit == "m":
                output = input / 10
            elif output_unit == "dm":
                output = input
            elif output_unit == "cm":
                output = input * 10
            elif output_unit == "mm":
                output = input * 100
            elif output_unit == "micrometre":
                output = input * 100000
            elif output_unit == "yard":
                output = input * 0.109361
            elif output_unit == "foot":
                output = input * 0.328084
            elif output_unit == "inch":
                output = input * 3.93701
            else:
                output = input / 16093


        #cm
        elif input_unit == "cm":
            if output_unit == "km":
                output = input / 100000
            elif output_unit == "hm":
                output = input / 10000
            elif output_unit == "dam":
                output = input / 1000
            elif output_unit == "m":
                output = input / 100
            elif output_unit == "dm":
                output = input / 10
            elif output_unit == "cm":
                output = input
            elif output_unit == "mm":
                output = input * 10
            elif output_unit == "micrometre":
                output = input * 10000
            elif output_unit == "yard":
                output = input * 0.0109361
            elif output_unit == "foot":
                output = input * 0.0328084
            elif output_unit == "inch":
                output = input * 0.393701
            else:
                output = input / 160930


        #mm
        elif input_unit == "mm":
            if output_unit == "km":
                output = input / 1000000
            elif output_unit == "hm":
                output = input / 100000
            elif output_unit == "dam":
                output = input / 10000
            elif output_unit == "m":
                output = input / 1000
            elif output_unit == "dm":
                output = input / 100
            elif output_unit == "cm":
                output = input / 10
            elif output_unit == "mm":
                output = input
            elif output_unit == "micrometre":
                output = input * 1000
            elif output_unit == "yard":
                output = input * 0.00109361
            elif output_unit == "foot":
                output = input * 0.00328084
            elif output_unit == "inch":
                output = input * 0.0393701
            else:
                output = input / 1609300


        #micrometre
        elif input_unit == "micrometre":
            if output_unit == "km":
                output = input / 1000000000
            elif output_unit == "hm":
                output = input / 100000000
            elif output_unit == "dam":
                output = input / 10000000
            elif output_unit == "m":
                output = input / 1000000
            elif output_unit == "dm":
                output = input / 100000
            elif output_unit == "cm":
                output = input / 10000
            elif output_unit == "mm":
                output = input / 1000
            elif output_unit == "micrometre":
                output = input
            elif output_unit == "yard":
                output = input / 914400
            elif output_unit == "foot":
                output = input / 304800
            elif output_unit == "inch":
                output = input / 25400
            else:
                output = input / 16093000


        #yard
        elif input_unit == "yard":
            if output_unit == "km":
                output = input / 1094
            elif output_unit == "hm":
                output = input / 109.4
            elif output_unit == "dam":
                output = input / 10.94
            elif output_unit == "m":
                output = input / 1.094
            elif output_unit == "dm":
                output = input * 9.144
            elif output_unit == "cm":
                output = input * 91.44
            elif output_unit == "mm":
                output = input * 914.4
            elif output_unit == "micrometre":
                output = input * 914400
            elif output_unit == "yard":
                output = input
            elif output_unit == "foot":
                output = input * 3
            elif output_unit == "inch":
                output = input * 36
            else:
                output = input / 1760


        #foot
        elif input_unit == "foot":
            if output_unit == "km":
                output = input / 3281
            elif output_unit == "hm":
                output = input / 328.1
            elif output_unit == "dam":
                output = input / 32.81
            elif output_unit == "m":
                output = input / 3.281
            elif output_unit == "dm":
                output = input * 3.048
            elif output_unit == "cm":
                output = input * 30.48
            elif output_unit == "mm":
                output = input * 304.8
            elif output_unit == "micrometre":
                output = input * 304800
            elif output_unit == "yard":
                output = input / 3
            elif output_unit == "foot":
                output = input
            elif output_unit == "inch":
                output = input * 12
            else:
                output = input / 5280


        #inch
        elif input_unit == "inch":
            if output_unit == "km":
                output = input / 39370
            elif output_unit == "hm":
                output = input / 3937
            elif output_unit == "dam":
                output = input / 393.7
            elif output_unit == "m":
                output = input / 39.37
            elif output_unit == "dm":
                output = input / 3.937
            elif output_unit == "cm":
                output = input * 2.54
            elif output_unit == "mm":
                output = input * 25.4
            elif output_unit == "micrometre":
                output = input * 25400
            elif output_unit == "yard":
                output = input / 36
            elif output_unit == "foot":
                output = input / 12
            elif output_unit == "inch":
                output = input
            else:
                output = input / 63360

        db.execute("INSERT INTO converts (user_id, input, output, input_unit, output_unit) VALUES(?, ?, ?, ?, ?)",
                   user_id, input, output, input_unit, output_unit)

        flash(f"You converted {input} {input_unit} to {output} {output_unit}.")
        return render_template("distance.html")
    else:
        return render_template("distance.html")



@app.route("/time", methods=["GET", "POST"])
def time():
    """Convert time."""
    user_id = session["user_id"]
    if request.method == "POST":
        input_unit = request.form.get("input_unit")
        output_unit = request.form.get("output_unit")
        input = request.form.get("input")

        if not input_unit or not output_unit:
            return apology("must give input unit and output unit")
        elif not input:
            return apology("must give input")
        else:
            input = int(input)

        #millennium
            #if input_unit == "millennium":
                #if output_unit == "millenium":
                    #output = input
                #elif output_unit == "century":
                    #output = input * 10
                #elif output_unit == "decade":
                   # output = input * 100
               # elif output_unit == "year":
                 #   output = input * 1000
               # elif output_unit == "month":
                #    output = input * 12000
                #elif output_unit == "week":
                 #   output = input * 52140
                #elif output_unit == "day":
                 #   output = input * 365000
                #elif output_unit == "hour":
                #    output = input * 8760000
                #elif output_unit == "minute":
                 #   output = input * 525600000
                #elif output_unit == "second":
                 #   output = input * 31536000000
                #else:
                 #   output = input * 31536000000000


        #century
        if input_unit == "century":
            #if output_unit == "millenium":
                #output = input / 10
            if output_unit == "century":
                output = input
            elif output_unit == "decade":
                output = input * 10
            elif output_unit == "year":
                output = input * 100
            elif output_unit == "month":
                output = input * 1200
            elif output_unit == "week":
                output = input * 5214
            elif output_unit == "day":
                output = input * 36500
            elif output_unit == "hour":
                output = input * 876000
            elif output_unit == "minute":
                output = input * 52560000
            elif output_unit == "second":
                output = input * 3153600000
            else:
                output = input * 3153600000000


        #decade
        elif input_unit == "decade":
            #if output_unit == "millenium":
                #output = input / 100
            if output_unit == "century":
                output = input / 10
            elif output_unit == "decade":
                output = input
            elif output_unit == "year":
                output = input * 10
            elif output_unit == "month":
                output = input * 120
            elif output_unit == "week":
                output = input * 521.4
            elif output_unit == "day":
                output = input * 3650
            elif output_unit == "hour":
                output = input * 87600
            elif output_unit == "minute":
                output = input * 5256000
            elif output_unit == "second":
                output = input * 315360000
            else:
                output = input * 315360000000

        #year
        elif input_unit == "year":
            #if output_unit == "millenium":
                #output = input / 1000
            if output_unit == "century":
                output = input / 100
            elif output_unit == "decade":
                output = input / 10
            elif output_unit == "year":
                output = input
            elif output_unit == "month":
                output = input * 12
            elif output_unit == "week":
                output = input * 52.14
            elif output_unit == "day":
                output = input * 365
            elif output_unit == "hour":
                output = input * 8760
            elif output_unit == "minute":
                output = input * 525600
            elif output_unit == "second":
                output = input * 31536000
            else:
                output = input * 31536000000


        #month
        elif input_unit == "month":
            #if output_unit == "millenium":
               # output = input / 12000
            if output_unit == "century":
                output = input / 1200
            elif output_unit == "decade":
                output = input / 120
            elif output_unit == "year":
                output = input / 12
            elif output_unit == "month":
                output = input
            elif output_unit == "week":
                output = input * 4.345
            elif output_unit == "day":
                output = input * 30.417
            elif output_unit == "hour":
                output = input * 730
            elif output_unit == "minute":
                output = input * 43800
            elif output_unit == "second":
                output = input * 2628000
            else:
                output = input * 2628000000


        #week
        elif input_unit == "week":
            #if output_unit == "millenium":
                #output = input / 52140
            if output_unit == "century":
                output = input / 5214
            elif output_unit == "decade":
                output = input / 521.4
            elif output_unit == "year":
                output = input / 52.14
            elif output_unit == "month":
                output = input / 4.345
            elif output_unit == "week":
                output = input
            elif output_unit == "day":
                output = input * 7
            elif output_unit == "hour":
                output = input * 168
            elif output_unit == "minute":
                output = input * 10080
            elif output_unit == "second":
                output = input * 604800
            else:
                output = input * 604800000


        #day
        elif input_unit == "day":
            #if output_unit == "millenium":
                #output = input / 365000
            if output_unit == "century":
                output = input / 36500
            elif output_unit == "decade":
                output = input / 3650
            elif output_unit == "year":
                output = input / 365
            elif output_unit == "month":
                output = input / 30.417
            elif output_unit == "week":
                output = input / 7
            elif output_unit == "day":
                output = input
            elif output_unit == "hour":
                output = input * 24
            elif output_unit == "minute":
                output = input * 1440
            elif output_unit == "second":
                output = input * 86400
            else:
                output = input * 86400000


        #hour
        elif input_unit == "hour":
            #if output_unit == "millenium":
                #output = input / 8760000
            if output_unit == "century":
                output = input / 876000
            elif output_unit == "decade":
                output = input / 87600
            elif output_unit == "year":
                output = input / 8760
            elif output_unit == "month":
                output = input / 730
            elif output_unit == "week":
                output = input / 168
            elif output_unit == "day":
                output = input / 24
            elif output_unit == "hour":
                output = input
            elif output_unit == "minute":
                output = input * 60
            elif output_unit == "second":
                output = input * 3600
            else:
                output = input * 3600000


        #minute
        elif input_unit == "minute":
            #if output_unit == "millenium":
                #output = input / 525600000
            if output_unit == "century":
                output = input / 52560000
            elif output_unit == "decade":
                output = input / 5256000
            elif output_unit == "year":
                output = input / 525600
            elif output_unit == "month":
                output = input / 43800
            elif output_unit == "week":
                output = input / 10080
            elif output_unit == "day":
                output = input / 1440
            elif output_unit == "hour":
                output = input / 60
            elif output_unit == "minute":
                output = input
            elif output_unit == "second":
                output = input * 60
            else:
                output = input * 60000


        #second
        elif input_unit == "second":
            #if output_unit == "millenium":
                #output = input / 31536000000
            if output_unit == "century":
                output = input / 3153600000
            elif output_unit == "decade":
                output = input / 315360000
            elif output_unit == "year":
                output = input / 31536000
            elif output_unit == "month":
                output = input / 43800
            elif output_unit == "week":
                output = input / 10080
            elif output_unit == "day":
                output = input / 1440
            elif output_unit == "hour":
                output = input / 3600
            elif output_unit == "minute":
                output = input / 60
            elif output_unit == "second":
                output = input
            else:
                output = input * 1000


        #second
        else:
           # if output_unit == "millenium":
                #output = input / 31536000000000
            if output_unit == "century":
                output = input / 3153600000000
            elif output_unit == "decade":
                output = input / 315360000000
            elif output_unit == "year":
                output = input / 31536000000
            elif output_unit == "month":
                output = input / 43800000
            elif output_unit == "week":
                output = input / 10080000
            elif output_unit == "day":
                output = input / 1440000
            elif output_unit == "hour":
                output = input / 3600000
            elif output_unit == "minute":
                output = input / 60000
            elif output_unit == "second":
                output = input / 1000
            else:
                output = input

        db.execute("INSERT INTO converts (user_id, input, output, input_unit, output_unit) VALUES(?, ?, ?, ?, ?)",
                   user_id, input, output, input_unit, output_unit)


        flash(f"You converted {input} {input_unit} to {output} {output_unit}.")
        return render_template("time.html")
    else:
        return render_template("time.html")


@app.route("/temperature", methods=["GET", "POST"])
def temperature():
    """Convert temperature."""
    user_id = session["user_id"]
    if request.method == "POST":
        input_unit = request.form.get("input_unit")
        output_unit = request.form.get("output_unit")
        input = request.form.get("input")

        if not input_unit or not output_unit:
            return apology("must give input unit and output unit")
        elif not input:
            return apology("must give input")
        else:
            input = int(input)

        #celsius
        if input_unit == "celsius":
            if output_unit == "celsius":
                output = input
            elif output_unit == "fahrenheit":
                output = input * (9 / 5) + 32
            elif output_unit == "kelvin":
                output = input + 273.15
            else:
                output = input * (9 / 5) + 491.67


        #fahrenheit
        elif input_unit == "fahrenheit":
            if output_unit == "celsius":
                output = (input - 32) * (5 / 9)
            elif output_unit == "fahrenheit":
                output = input
            elif output_unit == "kelvin":
                output = (input - 32) * (5 / 9) + 273.15
            else:
                output = input + 459.67


        #kelvin
        elif input_unit == "kelvin":
            if output_unit == "celsius":
                output = input - 273.15
            elif output_unit == "fahrenheit":
                output = (input - 273.15) * (9 / 5) + 32
            elif output_unit == "kelvin":
                output = input
            else:
                output = input * 1.8


        #rankine
        else:
            if output_unit == "celsius":
                output = (input - 491.67) * (5 / 9)
            elif output_unit == "fahrenheit":
                output = input - 459.67
            elif output_unit == "kelvin":
                output = input * (5 / 9)
            else:
                output = input

        db.execute("INSERT INTO converts (user_id, input, output, input_unit, output_unit) VALUES(?, ?, ?, ?, ?)",
                   user_id, input, output, input_unit, output_unit)


        flash(f"You converted {input} {input_unit} to {output} {output_unit}.")
        return render_template("temperature.html")
    else:
        return render_template("temperature.html")

