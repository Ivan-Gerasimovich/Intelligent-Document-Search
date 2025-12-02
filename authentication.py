from flask import session, redirect, url_for, request, render_template

from dotenv import dotenv_values


ENV = dotenv_values(".env") 

def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username:
            if username in ENV.keys():
                if ENV[username] == password:
                    session["username"] = username
                    return redirect(url_for("index"))
                else:
                    error = "Invalid username or password"
    return render_template("auth.html", error=error)

def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper
