from app import app, db, add_data
from flask import render_template, request, Response, json, flash, redirect, get_flashed_messages, url_for, session, jsonify
from app.models import User, Project, Component, ComponentRelation, Assignee, Reporter, FixVersion, CC, Bug, Status, IssueType, Priority
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
    # TODO: Clickable projects to open components pages
    if not session.get('username'):
        return redirect(url_for('index'))
    # project1 = Project(project_id=1, title="BugTraq", description="Feature Tracking Application", start=datetime(2020,7,1), end=datetime(2020,10,1))
    # project1.save()
    # project2 = Project(project_id=2, title="Content Aggregator", description="Feature Tracking Application", start=datetime(2020,7,1), end=datetime(2020,10,1))
    # project2.save()
    all_projects = Project.query.all()
    return render_template("projects.html", title="Projects", all_projects=all_projects, projects=True)

@app.route("/components/<project_id>")
def components(project_id=None):
    if not session.get('username'):
        return redirect(url_for('index'))
    if not project_id:
        redirect(url_for('/projects'))
    all_components = Component.query.filter_by(project_id=project_id)
    project = Project.query.filter_by(project_id=project_id).first()
    return render_template("components.html", title="Components",all_components=all_components, project=project, components=True)


# @app.route("/bug")
# def bugs():
#     if not session.get('username'):
#         return redirect(url_for('index'))
#     all_projects = Project.query.all()
#     return render_template("bugs.html", title="Bugs", bugs=True)

@app.route("/show_bug/id=<bug_id>")
def show_bugs(bug_id):
    if not bug_id:
        redirect(url_for('index'))
    bug = Bug.query.filter_by(bug_id=bug_id).first()
    issue_type = IssueType.query.filter_by(issue_type_id=bug.issue_type_id).first().issue_type
    status = Status.query.filter_by(status_id=bug.status_id).first().status
    priority = Priority.query.filter_by(pid=bug.pid).first().priority
    today = datetime.utcnow()
    project = Project.query.filter_by(project_id=bug.project_id).first()
    assignee = User.query.filter_by(user_id=bug.assignee_id).first()
    reporter = User.query.filter_by(user_id=bug.reporter_id).first()
    creator = User.query.filter_by(user_id=bug.creator_id).first()
    return render_template("show_bugs.html", project=project, assignee=assignee, creator=creator, reporter=reporter, bug=bug, issue_type=issue_type, status=status, priority=priority,
        title="Bugs", User=User, bugs=True, today=today)

@app.route("/data")
def add():

    # return add_data.priority()
    # return add_data.status()
    # return add_data.issue_type()
    # return add_data.assignee()
    # return add_data.bug()
    # return add_data.component()
    return 1