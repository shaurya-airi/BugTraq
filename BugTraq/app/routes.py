from app import app, db, add_data
from flask import (render_template, request, flash, redirect, url_for, session,
                   jsonify)
from app.models import (Comment, User, Project, Component, Bug, Status)
from app.forms import (LoginForm, RegisterForm, CreateBugForm, SearchBugForm,
                       CreateProjectForm, CreateComponentForm, CommentForm,
                       DeleteBugForm)
from datetime import datetime
from app.filters import (FILTER_FIELDS, FILTER_DICT)

bug_list = []


@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html", index_flag=True)


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
            session['first_name'] = user.first_name
            flash(f"Welcome, {session['first_name']}!", "success")
            return redirect("/index")
        else:
            flash("Username or password is wrong. Please check and try again.",
                  "danger")
    return render_template("login.html", title="Login", form=form,
                           login_flag=True)


@app.route("/logout")
def logout():
    session['user_id'] = False
    session['username'] = False
    flash('You have been logged out.', 'warning')
    return redirect(url_for('index'))


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get('username'):
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User(username=username, email=email, first_name=first_name,
                    last_name=last_name)
        user.set_password(password)
        user.save()
        flash("You are successfully registered!", "success")
        return redirect(url_for('index'))
    return render_template("register.html", form=form, title="Register",
                           register_flag=True)


@app.route("/users")
@app.route("/user/<username>")
def user(username=None):
    if not session.get('username'):
        return redirect(url_for('index'))
    user = User.query.filter_by(username=username).first()
    users = None
    bugs = None
    if not username:
        users = User.query.all()
    if user:
        bugs = user.assignees.bugs
    return render_template('user.html', bugs=bugs, Status=Status,
                           title="All Bugs", user=user, users=users,
                           user_flag=True)


@app.route("/projects")
def projects():
    if not session.get('username'):
        return redirect(url_for('index'))
    all_projects = Project.query.all()
    return render_template("projects.html", title="Projects",
                           all_projects=all_projects, projects_flag=True)


@app.route("/create_project", methods=['GET', 'POST'])
def create_project():
    if not session.get('username'):
        return redirect(url_for('index'))
    form = CreateProjectForm()
    if form.validate_on_submit():
        Project(title=form.title.data, description=form.description.data,
                start=form.start.data, end=form.end.data).save()
        flash("Project is successfully created!", "success")
        return redirect(url_for('projects'))
    return render_template("create_project.html", form=form,
                           title="Create Project", create_project_flag=True)


@app.route("/components/<project_id>", methods=['GET', 'POST'])
def components(project_id=None):
    if not session.get('username'):
        return redirect(url_for('index'))
    if not project_id:
        redirect(url_for('/projects'))
    project = Project.query.get_or_404(project_id)
    all_components = project.components
    return render_template("components.html", title="Components",
                           all_components=all_components, project=project,
                           components_flag=True)


@app.route("/create_component/<project_id>", methods=['GET', 'POST'])
def create_component(project_id=None):
    if not session.get('username'):
        return redirect(url_for('index'))
    form = CreateComponentForm()
    form.project_id.data = project_id
    if form.validate_on_submit():
        Component(name=form.name.data, project_id=form.project_id.data).save()
        flash("Component is successfully created!", "success")
        return redirect(url_for('components', project_id=project_id))
    return render_template("create_component.html", form=form,
                           title="Create Component",
                           create_component_flag=True)


@app.route('/get_component/<project_id>')
def get_component(project_id):
    if not session.get('username'):
        return redirect(url_for('index'))
    components = [{'component_id': row.component_id, 'name': row.name} for row
                  in Component.query.filter_by(project_id=project_id).all()]
    return jsonify(components)


@app.route("/bugs")
@app.route("/bugs/<field>", methods=["POST", "GET"])
def bugs(field=None):
    if not session.get('username'):
        return redirect(url_for('index'))
    if field:
        bugs_query = FILTER_DICT[field]
        bugs = bugs_query()
    elif request.args.get('project_id'):
        bugs = Bug.query.filter_by(
            project_id=request.args.get('project_id')).all()
    elif request.args.get('bug_list'):
        bugs = bug_list
    else:
        bugs = Bug.query.all()
    return render_template("bugs.html", bugs=bugs, Status=Status,
                           title="All Bugs", bugs_flag=True)


@app.route("/show_bug/<bug_id>", methods=["POST", "GET"])
def show_bug(bug_id):
    if not session.get('username'):
        return redirect(url_for('index'))
    if not bug_id:
        redirect(url_for('index'))
    bug = Bug.query.get_or_404(bug_id)
    issue_type = bug.issue_type.issue_type
    status = bug.status.status
    priority = bug.priority.priority
    today = datetime.utcnow()
    project = bug.project
    components = bug.component
    assignee = bug.assignee.user
    reporter = bug.reporter.user
    creator = bug.creator
    form = CommentForm()
    delete_form = DeleteBugForm()
    comments = bug.comments
    if form.validate_on_submit():
        Comment(body=form.body.data,
                bug_id=bug_id,
                user=User.query.
                filter_by(username=session.get('username')).first()).save()
        flash('Your comment has been published.', 'success')
        return redirect(url_for('show_bug', bug_id=bug_id))
    if request.method == 'POST' and request.form.get('delete_comment'):
        comment_id = int(request.form.get('delete_comment'))
        app.logger.info(f"Deleting Comment {comment_id}")
        comment = Comment.query.get(comment_id)
        if comment:
            db.session.delete(comment)
            app.logger.info(f"Comment {comment_id} Deleted.")
            flash(f"Comment {comment_id} has been deleted.", "success")
            db.session.commit()
    if delete_form.is_submitted() and request.form.get('delete'):
        delete_bug(delete_form, bug)
        return redirect(url_for("bugs"))
    return render_template("show_bug.html", form=form, comments=comments,
                           project=project, assignee=assignee, creator=creator,
                           reporter=reporter, bug=bug, issue_type=issue_type,
                           status=status, priority=priority, title="Bugs",
                           User=User, bugs=True, today=today,
                           components=components, show_bugs_flag=True,
                           delete_form=delete_form)


@app.route("/create_bug", methods=["GET", "POST"])
def create_bug():
    if not session.get('username'):
        return redirect(url_for('index'))
    form = CreateBugForm()
    first_project = Project.query.order_by('project_id').first()
    form.component.choices = [(item.component_id, item.name) for item in
                              first_project.components]
    if request.method == 'POST':
        form.component.choices = [(item.component_id, item.name) for item in
                                  Component.query.filter_by(
                                      project_id=form.project.data)]
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
        project_id = form.project.data

        bug = Bug(summary=summary, description=description,
                  status_id=status_id, issue_type_id=issue_type_id, pid=pid,
                  version=version, reporter_id=reporter_id,
                  assignee_id=assignee_id, creator_id=session['user_id'],
                  project_id=project_id)
        for component_id in components:
            component = Component.query.get(component_id)
            bug.component.append(component)
        bug.save()
        flash("Bug is successfully created!", "success")
        return redirect(url_for('show_bug', bug_id=bug.bug_id))
    return render_template("create_bug.html", form=form, title="Create Bug",
                           create_bug_flag=True)


@app.route("/edit_bug/<bug_id>", methods=["GET", "POST"])
def edit_bug(bug_id):
    if not session.get('username'):
        return redirect(url_for('index'))
    bug = Bug.query.get_or_404(bug_id)
    form = CreateBugForm(obj=bug)
    # Got components selected
    form.component.choices = [(item.component_id, item.name) for item in
                              bug.project.components]
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

    if request.method == 'POST':
        form.component.choices = [(item.component_id, item.name) for item in
                                  Component.query.filter_by(
                                      project_id=form.project.data)]
    if form.validate_on_submit():
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
        bug.component.clear()
        for component_id in components:
            component = Component.query.get(component_id)
            bug.component.append(component)
        db.session.add(bug)
        db.session.commit()
        flash('The Bug has been Updated Successfully!', 'success')
        return redirect(url_for('bugs'))
    return render_template("edit_bug.html", form=form, title="Edit Bug",
                           edit_bug_flag=True)


@app.route("/search_bugs", methods=["GET", "POST"])
def search_bugs():
    if not session.get('username'):
        return redirect(url_for('index'))
    form = SearchBugForm()
    if request.method == 'POST':
        # TODO: Check logic for form.validateon search_input
        if request.form.get('search_input'):
            bugs, total_matches = Bug.search(request.form.get('search_input'))
            global bug_list
            bug_list = bugs
            return redirect(url_for('bugs', bug_list=bugs))
        # FILTER PART
        # TODO: I may need to rethink filter and search separation
        # TODO: Either add search and filtering to bugs page or add bugs pages
        # extension to search_bugs
        for field in FILTER_FIELDS:
            if request.form.get(field):
                return redirect(url_for('bugs', field=field))

    return render_template("search_bugs.html", form=form, title="Search Bugs",
                           Status=Status, fields=FILTER_FIELDS,
                           search_bugs_flag=True)


def delete_bug(delete_form: DeleteBugForm, bug):
    app.logger.info(f"Delete the comments of the bug {bug.bug_id}")
    bug_id = bug.bug_id
    for comment in bug.comments:
        app.logger.info(f"Deleting Comment {comment.id}")
        db.session.delete(comment)
    app.logger.info(f"Deleting Bug {bug.bug_id}")
    db.session.delete(bug)
    db.session.commit()
    flash(f'Bug {bug_id} is deleted.', 'success')


@app.route("/test/",  methods=["POST", "GET"])
@app.route("/tests")
@app.route("/test/<bug_id>", methods=["POST", "GET"])
def test(bug_id=None):
    bug = Bug.query.get(bug_id)
    comment_id = 12
    delete_form = DeleteBugForm()
    return render_template("test_ui.html", comment_id=comment_id, bug=bug,
                           delete_form=delete_form)


@app.route("/data")
def add():
    if not session.get('username'):
        return redirect(url_for('index'))

    # return add_data.priority()
    # return add_data.status()
    # return add_data.issue_type()
    # return add_data.assignee()
    # return add_data.bug()
    # return add_data.component()
    # return add_data.components_to_bug(3)
    return add_data.comment()
