import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db

# Create a Blueprint for authentication-related routes
bp = Blueprint("auth", __name__, url_prefix="/auth")

def login_required(view):
    # Decorator to ensure the user is logged in before accessing certain views.
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # Check if the user is logged in
        if g.user is None:
            # Redirect to the login page if the user is not logged in
            return redirect(url_for("auth.login"))
        # Proceed with the original view if the user is logged in
        return view(**kwargs)
    return wrapped_view

@bp.before_app_request
def load_logged_in_user():
    # Load the user from the session if the user_id is present.
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        # Fetch the user from the database and store it in `g.user`
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()

@bp.route("/register", methods=("GET", "POST"))
def register():
    # Handle user registration, including form validation and password hashing.
    if request.method == "POST":
        # Retrieve form data
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        # Validate form data
        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                # Insert new user into the database with hashed password
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password, method='pbkdf2', salt_length=16)),
                )
                db.commit()
                # Redirect to login page on successful registration
                return redirect(url_for("auth.login"))
            except db.IntegrityError:
                # Handle case where username is already taken
                error = f"User {username} is already registered."

        # Display error message if any
        flash(error)

    # Render registration template
    return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    # Handle user login, including checking credentials and managing session.
    if request.method == "POST":
        # Retrieve form data
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None

        # Retrieve user from the database
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        # Validate user credentials
        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."

        if error is None:
            # Store user id in the session and redirect to the main page
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("main.index"))

        # Display error message if credentials are incorrect
        flash(error)

    # Render login template
    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    # Log out the current user by clearing the session.
    session.clear()
    # Redirect to the main page after logging out
    return redirect(url_for("main.index"))
