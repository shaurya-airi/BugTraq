from app import app, db
from flask import render_template, request, Response, json, flash, redirect, get_flashed_messages, url_for, session, jsonify
from app.models import User
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
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.get_password(password):
            flash("You are successfully logged in!","success")
            return redirect("/index")
        else:
            flash("Sorry, something went wrong!","danger")
    return render_template("login.html", title="Login", form=form, login=True)

@app.route("/logout")
def logout():
    return redirect(url_for('index'))

@app.route("/register", methods=["GET", "POST"])
def register():
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
    # admin = User(user_id=2, username='admin', email='admin@buqtraq.com', first_name='admin', last_name="admin")
    # admin.set_password('123456')
    # admin.save()
    # guest_user.save()
    users = User.query.all()
    return render_template('user.html', users=users)