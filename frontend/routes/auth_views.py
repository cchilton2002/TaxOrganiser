from flask import Blueprint, render_template

auth_views = Blueprint('auth', __name__)

@auth_views.route("/")
def login():
    return render_template("login.html")

@auth_views.route("/register")
def register():
    return render_template("register.html")