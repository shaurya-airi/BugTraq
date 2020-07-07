from app import app, db
from flask import render_template, request, Response, json, flash, redirect, get_flashed_messages, url_for, session, jsonify
from app.models import User, Project
from app.forms import LoginForm, RegisterForm
from datetime import datetime

@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index=True)

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get('username'):
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.get_password(password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            flash("You are successfully logged in!","success")
            return redirect("/index")
        else:
            flash("Sorry, something went wrong!","danger")
    return render_template("login.html", title="Login", form=form, login=True)

@app.route("/logout")
def logout():
    session['user_id']=False
    session['username']=False
    return redirect(url_for('index'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user_id = len(User.query.all()) +1
        username = form.username.data
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User(user_id=user_id, username=username, email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        flash("You are successfully registered!","success")
        return redirect(url_for('index'))
    return render_template("register.html", form=form, title="Register", register=True)

@app.route("/user")
@app.route("/users")
def user():
    # guest_user = User(user_id=1, username='airis', email='shauryaairi@bugtraq.com', first_name='Shaurya', last_name='Airi')
    # guest_user.set_password('123456')
    # guest_user.save()
    # admin = User(user_id=2, username='admin', email='admin@buqtraq.com', first_name='admin', last_name="admin")
    # admin.set_password('123456')
    # admin.save()
    users = User.query.all()
    return render_template('user.html', users=users)

# @app.route("/navigate")
# def navigate_bugs():
#     return render_template("navigate_bugs.html", title="Navigation", navigaiton=True)

@app.route("/projects")
def projects():
    # project1 = Project(project_id=1, title="BugTraq", description="Feature Tracking Application", start=datetime(2020,7,1), end=datetime(2020,10,1))
    # project1.save()
    # project2 = Project(project_id=2, title="Content Aggregator", description="Feature Tracking Application", start=datetime(2020,7,1), end=datetime(2020,10,1))
    # project2.save()
    all_projects = Project.query.all()
    return render_template("projects.html", title="Projects", all_projects=all_projects, projects=True)