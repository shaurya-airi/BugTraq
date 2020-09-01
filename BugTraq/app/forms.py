from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, SubmitField, SelectMultipleField, widgets, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, InputRequired
from app.models import User, Project, Component, Assignee, Reporter, FixVersion, CC, Bug, Status, IssueType, Priority
from flask import request
from sqlalchemy import desc

class LoginForm(FlaskForm):
    #TODO: Login using username or email
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(6,50)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(2, 55)])
    password = PasswordField("Password", validators=[DataRequired(), Length(6,50)])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired(), Length(6,50), EqualTo('password')])
    first_name = StringField("First Name", validators=[DataRequired(), Length(2,80)])
    last_name = StringField("Last Name", validators=[DataRequired(), Length(2, 80)])
    submit = SubmitField("Register Now")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email is already in use.")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username is already in use.")
# TODO: Handle: Getting two errors:  Field must be between 6 and 50 characters long. Field must be equal to and  Username is already in use.

class CreateBugForm(FlaskForm):
    # Choices for the select fields
    status_choices = [(item.status_id, item.status) for item in Status.query.order_by('status_id')]
    issue_type_choices = [(item.issue_type_id, item.issue_type) for item in IssueType.query.order_by('issue_type_id')]
    priority_choices = [(item.pid, item.priority) for item in Priority.query.order_by('pid')]
    reporter_choices = [(item.user_id, User.query.filter_by(user_id=item.user_id).first().username) for item in Reporter.query.order_by('user_id')]
    assignee_choices = [(item.user_id, User.query.filter_by(user_id=item.user_id).first().username) for item in Assignee.query.order_by('user_id')]
    project_choices = [(item.project_id, item.title) for item in Project.query.order_by('project_id')]
    component_choices = [(item.component_id, item.name ) for item in Component.query.order_by('name')]

    summary = StringField("Summary", validators=[DataRequired(), Length(1, 72)])
    description = StringField("Description", validators=[DataRequired(), Length(1,256)])
    status = SelectField("Status", choices=status_choices, validate_choice=False)
    issue_type = SelectField("Issue Type", choices=issue_type_choices, validate_choice=False)
    priority = SelectField("Priority", choices=priority_choices, validate_choice=False)
    version = StringField("Version", validators=[DataRequired(), Length(1, 30)])
    reporter = SelectField("Reporter", choices=reporter_choices, validate_choice=False)
    assignee = SelectField("Assignee", choices=assignee_choices, validate_choice=False)
    project = SelectField("Project", id='select_project', choices=project_choices, validate_choice=False)
    component = SelectMultipleField("Component", option_widget=widgets.CheckboxInput(), id='select_component', coerce=int, choices=component_choices)
    # CC = SelectMultipleField("CC", validators=[DataRequired(), Length(2, 50)])
    submit = SubmitField("Submit")


class SearchBugForm(FlaskForm):
    search_input = StringField("Search Bugs", validators=[DataRequired(), Length(1, 72)], render_kw={"placeholder": "Search Bugs"})
    search = SubmitField("Go")

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchBugForm, self).__init__(*args, **kwargs)


class CreateProjectForm(FlaskForm):
    # Project(project_id=1, title="BugTraq", description="Feature Tracking Application", start=datetime(2020,7,1), end=datetime(2020,10,1)).save()
    title = StringField("Title", validators=[DataRequired(), Length(2, 50)])
    description = StringField("Description", validators=[DataRequired(), Length(2, 80)])
    start = DateField("Project Start Date", validators=[DataRequired()])
    end = DateField("Project End Date", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CreateComponentForm(FlaskForm):
    name = StringField("Component", validators=[DataRequired(), Length(2, 50)])
    submit = SubmitField("Submit")


class CommentForm(FlaskForm):
    # bug_choices = [(item.bug_id, item.summary) for item in Bug.query.order_by(desc(Bug.updated_at)).all()]
    body = StringField('', validators=[DataRequired()])
    # bug = SelectField("Bug", choices=bug_choices, validate_choice=False)
    submit = SubmitField('Submit')
