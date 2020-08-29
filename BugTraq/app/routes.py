from app import app, db, add_data
from flask import render_template, request, Response, json, flash, redirect, get_flashed_messages, url_for, session, jsonify
from app.models import User, Project, Component, Assignee, Reporter, FixVersion, CC, Bug, Status, IssueType, Priority
from app.forms import LoginForm, RegisterForm, CreateBugForm, SearchBugForm
from datetime import datetime
from app.filters import *
# from sqlalchemy import in_
bug_list = []

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
        # user_id = len(User.query.all()) +1 : Not required as next user_id is created as it is PK in SQL
        username = form.username.data
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User(username=username, email=email, first_name=first_name, last_name=last_name)
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

@app.route("/projects")
def projects():
    # TODO: Clickable projects to open components pages
    if not session.get('username'):
        return redirect(url_for('index'))
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

@app.route('/get_component/<project_id>')
def get_component(project_id):
    components = [{'component_id':row.component_id, 'name':row.name} for row in Component.query.filter_by(project_id=project_id).all()]
    return jsonify(components)

@app.route("/bug")
@app.route("/bug/<field>", methods=["POST", "GET"])
def bugs(field=None):
    if not session.get('username'):
        return redirect(url_for('index'))
    if field:
        bugs_query = FILTER_DICT[field]
        bugs = bugs_query()
    elif request.args.get('bug_list'):
        bugs = bug_list
    else:
        bugs = Bug.query.all()
    return render_template("bugs.html", bugs=bugs, Status=Status, title="All Bugs", all_bugs=True)

@app.route("/show_bug/<bug_id>")
def show_bugs(bug_id):
    if not bug_id:
        redirect(url_for('index'))
    bug = Bug.query.filter_by(bug_id=bug_id).first()
    issue_type = IssueType.query.filter_by(issue_type_id=bug.issue_type_id).first().issue_type
    status = Status.query.filter_by(status_id=bug.status_id).first().status
    priority = Priority.query.filter_by(pid=bug.pid).first().priority
    today = datetime.utcnow()
    project = Project.query.filter_by(project_id=bug.project_id).first()
    components = bug.component
    assignee = User.query.filter_by(user_id=bug.assignee_id).first()
    reporter = User.query.filter_by(user_id=bug.reporter_id).first()
    creator = User.query.filter_by(user_id=bug.creator_id).first()
    return render_template("show_bugs.html", project=project, assignee=assignee, creator=creator, reporter=reporter, bug=bug, issue_type=issue_type, status=status, priority=priority,
        title="Bugs", User=User, bugs=True, today=today, components=components)

@app.route("/create_bug", methods=["GET", "POST"])
def create_bugs():
    form = CreateBugForm()
    if form.validate_on_submit():
        summary = form.summary.data
        description = form.description.data
        status_id = form.status.data
        issue_type_id = form.issue_type.data
        pid = form.priority.data
        version = form.version.data
        components = form.component.data
        reporter_id = form.reporter.data
        assignee_id = form.assignee.data
        creator_id = session.get('user_id')
        project_id = form.project.data

        bug = Bug( summary=summary, description= description, status_id=status_id, issue_type_id=issue_type_id,
            pid=pid, version=version, reporter_id=reporter_id, assignee_id=assignee_id, creator_id=session['user_id'], project_id=project_id)
        for component_id in components:
            component = Component.query.get(component_id)
            bug.component.append(component)
        bug.save()
        flash("Bug is successfully created!","success")
        return redirect(url_for('bugs'))
    return render_template("create_bug.html", form=form, title="Create Bug", create_bug=True)

@app.route("/edit_bug/<bug_id>", methods=["GET", "POST"])
def edit_bugs(bug_id):
    bug = Bug.query.get_or_404(bug_id)
    form = CreateBugForm(obj=bug)
    # Got components selected

    if request.method == 'GET':
        form.status.default = bug.status_id
        form.issue_type.default = bug.issue_type_id
        form.priority.default = bug.pid
        form.reporter.default = bug.reporter_id
        form.assignee.default = bug.assignee_id
        form.project.default = bug.project_id
        form.process()

        form.summary.data = bug.summary
        form.description.data = bug.description
        form.version.data = bug.version
        form.component.data = [c.component_id for c in bug.component]

    if request.method == 'POST' and form.validate():
        components = form.component.data
        bug.summary = form.summary.data
        bug.description = form.description.data
        bug.status_id = form.status.data
        bug.issue_type_id = form.issue_type.data
        bug.pid = form.priority.data
        bug.version = form.version.data
        bug.reporter_id = form.reporter.data
        bug.assignee_id = form.assignee.data
        bug.creator_id = session.get('user_id')
        bug.project_id = form.project.data
        for component_id in components:
            component = Component.query.get(component_id)
            bug.component.append(component)
        db.session.add(bug)
        db.session.commit()
        flash('The Bug has been Updated Successfully!','success')
        return redirect(url_for('bugs'))
    return render_template("edit_bug.html", form=form, title="Edit Bug", edit_bug=True)

@app.route("/search_bug", methods=["GET", "POST"])
def search_bugs():
    form = SearchBugForm()
    if request.method == 'POST':
        # TODO: Check logic for form.validateon search_input
        if request.form.get('search_input'):
            bugs, total_matches = Bug.search(request.form.get('search_input'))
            global bug_list
            bug_list = bugs
            return redirect(url_for('bugs',bug_list=bugs))
        # FILTER PART
        # TODO: I may need to rethink filter and search separation
        # TODO: Either add search and filtering to bugs page or add bugs pages extension to search_bugs
        for field in FILTER_FIELDS:
            if request.form.get(field):
                return redirect(url_for('bugs',field=field))

    return render_template("search_bug.html", form=form, title="Search Bugs",  Status=Status, fields=FILTER_FIELDS, search_bug=True)

@app.route("/data")
def add():

    # return add_data.priority()
    # return add_data.status()
    # return add_data.issue_type()
    # return add_data.assignee()
    # return add_data.bug()
    # return add_data.component()
    # return add_data.components_to_bug(3)
    return 1