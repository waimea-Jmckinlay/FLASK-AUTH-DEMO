# ===========================================================
# APP NAME HERE
# By YOUR NAME HERE
# ===========================================================

import html
from io import BytesIO
from os import getenv

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    session,
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.helpers import *

# Create the app
app = Flask(__name__)


# ===========================================================
# App Routes Handlers
# ===========================================================


# -----------------------------------------------------------
# Welcome page
# -----------------------------------------------------------
@app.get("/")
def show_welcome():
    return render_template("pages/welcome.jinja")


# -----------------------------------------------------------
# Signup page
# -----------------------------------------------------------
@app.get("/user/new")
def show_signup_form():
    return render_template("pages/user_form.jinja")


# -----------------------------------------------------------
# Handle user signup
# -----------------------------------------------------------
@app.post("/user")
def process_new_user():
    forename = request.form.get("forename", "").strip()
    surname = request.form.get("surname", "").strip()
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "").strip()

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


# -----------------------------------------------------------
# Login page
# -----------------------------------------------------------
@app.get("/login")
def show_login_form():
    return render_template("pages/login_form.jinja")


# -----------------------------------------------------------
# Handle user login
# -----------------------------------------------------------
@app.post("/login")
def process_user_login():
    username = request.form.get("username", "").strip().lower()
    password = request.form.get("password", "").strip()

    with connect_db() as db:
        sql = """
            SELECT id, username, forename, surname, password_hash
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
            "username": user["username"],
            "forename": user["forename"],
            "surname":  user["surname"],
        }

        flash("Login successful", "success")
        return redirect("/")


# -----------------------------------------------------------
# Handle user logout
# -----------------------------------------------------------
@app.get("/logout")
def handle_logout():
    session.clear()
    flash(f"You have been logged out", "success")
    return redirect("/")


# -----------------------------------------------------------
# Message list page - Show all the messages
# -----------------------------------------------------------
@app.get("/messages")
@login_required
def show_all_messages():
    with connect_db() as db:
        sql = """
            SELECT
                messages.id AS mid,
                messages.title,
                messages.body,
                users.id AS uid,
                users.username,
                users.forename,
                users.surname
            FROM messages
            JOIN users on messages.user_id = users.id
            ORDER BY mid DESC
        """
        params = ()
        messages = db.execute(sql, params).fetchall()

        return render_template("pages/message_list.jinja", messages=messages)


# -----------------------------------------------------------
# New message page
# -----------------------------------------------------------
@app.get("/message/new")
@login_required
def show_message_form():
    return render_template("pages/message_form.jinja")


# -----------------------------------------------------------
# Handle new message
# -----------------------------------------------------------
@app.post("/message")
@login_required
def process_new_message():
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()

    user_id = session["user"]["id"]

    with connect_db() as db:
        sql = """
            INSERT INTO messages (title, body, user_id)
            VALUES (?, ?, ?)
        """
        params = (title, body, user_id)
        db.execute(sql, params)

        flash("Message posted", "success")
        return redirect("/messages")


# -----------------------------------------------------------
# Message edit page
# -----------------------------------------------------------
@app.get(f"/messages/<int:id>/edit")
@login_required
def show_edit_message_form(id):
    with connect_db() as db:
        sql = """
            SELECT id, title, body, user_id FROM messages WHERE id=?
        """
        params = (id,)
        message = db.execute(sql, params).fetchone()

        if message and message["user_id"] == session["user"]["id"]:
            return render_template("pages/edit_message_form.jinja", message=message)

        flash("Invalid message", "error")
        return redirect("messages")


# -----------------------------------------------------------
# Handle new message
# -----------------------------------------------------------
@app.post("/messages/<int:id>/update")
@login_required
def process_edited_message(id):
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()

    user_id = session["user"]["id"]

    with connect_db() as db:
        sql = """
            UPDATE messages SET
                title = ?,
                body = ?
            WHERE id = ? AND user_id = ?
        """
        params = (title, body, id, user_id)
        db.execute(sql, params)

        flash("Message updated", "success")
        return redirect("/message")


# -----------------------------------------------------------
# Message delete handling
# -----------------------------------------------------------
@app.get(f"/message/<int:id>/delete")
@login_required
def process_delete_message(id):
    with connect_db() as db:
        sql = """
            SELECT user_id FROM messages WHERE id=?
        """
        params = (id,)
        message = db.execute(sql, params).fetchone()

        if message and message["user_id"] == session["user"]["id"]:

            sql = """
                DELETE FROM messages WHERE id=?
            """
            params = (id,)
            db.execute(sql, params)

            flash("Message deleted", "success")
            return redirect("/messages")

        flash("Invalid message", "error")
        return redirect("/messages")


# -----------------------------------------------------------
# Help page - Show some help
# -----------------------------------------------------------
@app.get("/help")
def show_help():

    flash("Flash test message")
    flash("Flash test message with a longer bit of text")
    flash("Success test message", "success")
    flash("Error test message", "error")

    return render_template("pages/help.jinja")


# ===========================================================
# Configure the app
# ===========================================================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)