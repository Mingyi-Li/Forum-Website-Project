import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

# from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure Library to use SQLite database
db = SQL("sqlite:///final.db")


# homepage
@app.route("/")
@login_required
def index():
    """Show homepage"""
    # get users from db
    usernames = db.execute(
        "SELECT username FROM users WHERE online='1' ORDER BY username ASC"
    )
    # add price and total value for all stocks
    return render_template("index.html", usernames=usernames)


# login page
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

        # Ensure user exists and password is correct
        if len(rows) != 1 or rows[0]["password"] != request.form.get("password"):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # update online status
        db.execute(
            "UPDATE users SET online='1' WHERE id = :user_id",
            user_id=session["user_id"],
        )

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # clear userames
    session.clear()
    # route POST
    if request.method == "POST":
        # check username submition
        if not request.form.get("username"):
            return apology("Please Enter Username. ", 400)
        # check password submition
        elif not request.form.get("password"):
            return apology("Please Enter Password. ", 400)
        # check password confirmation submition
        elif not request.form.get("confirmation"):
            return apology("Please Confirm Password. ", 400)
        # check password match confirmation
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords Do Not Match ", 400)
        # query db for username
        row = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        # check id user already exists
        if len(row) != 0:
            return apology("Existing Useranme")

        # insert submition
        db.execute(
            "INSERT INTO users (username, password) VALUES(?, ?)",
            request.form.get("username"),
            request.form.get("password"),
        )
        # get the new user
        row = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        # record registration
        session["user_id"] = row[0]["id"]

        # update online status
        db.execute(
            "UPDATE users SET online='1' WHERE id = :user_id",
            user_id=session["user_id"],
        )

        # to homepage
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # update online status
    db.execute(
        "UPDATE users SET online='0' WHERE id = :user_id", user_id=session["user_id"]
    )

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# forum page
@app.route("/forum")
@login_required
def forum():
    """Show forum"""
    # get all posts and pass to the html page
    posts = db.execute("SELECT * FROM posts ORDER BY time DESC")
    for post in posts:
        post["author"] = db.execute(
            "SELECT username FROM users WHERE id IN (SELECT user_id FROM posts WHERE id = :id)",
            id=post.get("id"),
        )[0].get("username")
    return render_template("forum.html", posts=posts)


# create a new post page
@app.route("/newPost", methods=["GET", "POST"])
@login_required
def newPost():
    """Show page"""
    if request.method == "POST":
        # apology on empty post
        if not request.form.get("inputPostContent"):
            return apology("Please Enter your ideas. ", 400)
        if not request.form.get("inputPostTitle"):
            return apology("Please Enter your ideas. ", 400)
        # insert submition
        db.execute(
            "INSERT INTO posts (user_id, title, content) VALUES(?, ?, ?)",
            session["user_id"],
            request.form.get("inputPostTitle"),
            request.form.get("inputPostContent"),
        )
    return render_template("newPost.html")
