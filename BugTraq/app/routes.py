from app import app
from flask import render_template, request, Response, json, flash, redirect, get_flashed_messages, url_for, session, jsonify
# from app.models import User
from app.forms import LoginForm, RegisterForm

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("You are successfully logged in!","success")
        return redirect("/index")
    return render_template("login.html", title="Login", form=form, login=True)

@app.route("/logout")
def logout():
    return redirect(url_for('index'))

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        flash("You are successfully registered!","success")
        return redirect(url_for('index'))
    return render_template("register.html", form=form, title="Register", register=True)
