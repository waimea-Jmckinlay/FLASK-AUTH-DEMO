#===========================================================
# APP NAME HERE
# By YOUR NAME HERE
#===========================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *


# Create the app
app = Flask(__name__)


#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Welcome page
#-----------------------------------------------------------
@app.get("/")
def show_welcome():
    return render_template("pages/welcome.jinja")

#-----------------------------------------------------------
# singnup page
#-----------------------------------------------------------
@app.get("/user/new")
def show_singnup_form():
    return render_template("pages/user_form.jinja")

#-----------------------------------------------------------
# handle user singup
#-----------------------------------------------------------
@app.post("/user")
def prosess_new_user():
  forename = request.form.get('forename', '').strip()
  surname  = request.form.get('surname',  '').strip()
  username = request.form.get('username', '').strip().lower()
  password = request.form.get('password', '').strip()

  with connect_db() as db:
        sql = "SELECT id FROM users WHERE username=?"
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if user:
            flash(f"Username '{username}' already exists", "error")
            return redirect("/user/new")

        pass_hash = generate_password_hash(password)

        sql = """
            INSERT INTO users (forename, surname, username, password_hash)
            VALUES (?, ?, ?, ?)
        """
        params = (forename, surname, username, pass_hash)
        db.execute(sql, params)

        flash("Account created. Please login", "success")
        return redirect("/login")

#-----------------------------------------------------------
# get login route
#-----------------------------------------------------------
@app.get("/login")
def show_login_user():
    return render_template("pages/login.jinja")
#-----------------------------------------------------------
# login post route  
#-----------------------------------------------------------  
@app.post("/login")
def login_user():
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    with connect_db() as db:
        sql = """
            SELECT id, forename, surname, password_hash
            FROM users
            WHERE username=?
        """
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if not user:
            flash(f"Unknown user", "error")
            return redirect("/login")

        if not check_password_hash(user["password_hash"], password):
            flash(f"Incorrect password", "error")
            return redirect("/login")

        session["logged_in"] = True
        session["user"] = {
            "id":       user["id"],
            "username": username,
            "forename": user["forename"],
            "surname":  user["surname"],
        }

        flash("Login successful", "success")
        return redirect("/")  
#------------------------------------------------------------------
# admin login 
#------------------------------------------------------------------
@app.post("/login")
def login_admin():
    password = request.form.get('password', '').strip()

    load_dotenv()
    ADMIN_PASSWORD = getenv("ADMIN_PASSWORD", "")
    if not ADMIN_PASSWORD:
        flash(f"No admin password set!", "error")
        return redirect("/")

    if password == ADMIN_PASSWORD:
        session["logged_in"] = True
        flash(f"Login successful", "success")
        return redirect("/")
    else:
        session.clear()
        flash(f"Incorrect password", "error")
        return redirect("/")                
#-----------------------------------------------------------
# logout route
#-----------------------------------------------------------
@app.get("/logout")
def logout_admin():
    session.clear()
    flash(f"You have been logged out", "success")
    return redirect("/")        
#-----------------------------------------------------------
# Creature list page - Show all the 
#-----------------------------------------------------------
@app.get("/creatures")
def show_all_creatures():
    with connect_db() as db:
        sql = """
            SELECT id, species, name
            FROM creatures
        """
        params = ()
        creatures = db.execute(sql, params).fetchall()

        return render_template("pages/creature_list.jinja", creatures=creatures)
#----------------------------------------------------------
#Add the @login_required decorator to required routes
#----------------------------------------------------------
@app.get("/admin")
@login_required
def admin_page():
    # Can only access this route if logged in
    ...
#----------------------------------------------------------
# message getting
#-----------------------------------------------------------
@app.get("/message/new")
@login_required
def message_page():
    return render_template("pages/message_form.jinja")

#----------------------------------------------------------
# message posting
#-----------------------------------------------------------
@app.post("/message")
def add_note():
    # Get form data
    title    = request.form.get('title', '').strip()
    body     = request.form.get('body', '').strip()

    # Validate data
    if not title:
        flash("Title is required", "error")
        return redirect("/message/new")

    if len(title) > 40:
        flash("Title is too long (max 40 chars)", "error")
        return redirect("/message/new")


    # Escape text inputs
    title = html.escape(title)
    body = html.escape(body)

    # User ID is in the session
    user_id = session["user"]["id"]

    # Add to the database
    with connect_db() as db:
        sql = """
            INSERT INTO messages (title, body, user_id)
            VALUES (?, ?, ?)
        """
        params = (title, body, user_id)
        db.execute(sql, params)

        flash(f"Message added")
        return redirect("/messages")

#-----------------------------------------------------------
# message obtaining
#-----------------------------------------------------------
@app.get("/message")

#-----------------------------------------------------------
# Help page - Show some help
#-----------------------------------------------------------
@app.get("/help")
def show_help():

    flash("Flash test message")
    flash("Flash test message with a longer bit of text")
    flash("Success test message", "success")
    flash("Error test message", "error")

    return render_template("pages/help.jinja")


#===========================================================
# Configure the app
#===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)

