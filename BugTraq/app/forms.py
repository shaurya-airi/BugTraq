from flask_wtf import FlaskForm
from wtforms import (
    IntegerField, BooleanField, PasswordField, SelectField, StringField,
    SubmitField, SelectMultipleField, widgets, DateField)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, ValidationError)
from app.models import (
    User, Project, Assignee, Reporter, Component, Status, IssueType, Priority)
from flask import request


class LoginForm(FlaskForm):
    # TODO: Login using username or email
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(6, 50)])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField(
        "Username", validators=[DataRequired(), Length(2, 55)])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(6, 50)])
    password_confirm = PasswordField(
        "Confirm Password", validators=[DataRequired(), Length(6, 50),
                                        EqualTo('password')])
    first_name = StringField(
        "First Name", validators=[DataRequired(), Length(2, 80)])
    last_name = StringField("Last Name", validators=[Length(0, 80)])
    submit = SubmitField("Register Now")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Email is already in use.")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Username is already in use.")
# TODO: Handle: Getting two errors:  Field must be between 6 and 50 characters
# long. Field must be equal to and  Username is already in use.


class CreateBugForm(FlaskForm):
    # Choices for the select fields
    status_choices = [(item.status_id, item.status) for item in
                      Status.query.order_by('status_id')]
    issue_type_choices = [(item.issue_type_id, item.issue_type) for item in
                          IssueType.query.order_by('issue_type_id')]
    priority_choices = [(item.pid, item.priority) for item in
                        Priority.query.order_by('pid')]
    # TODO: Use backrefs
    reporter_choices = [(item.user_id,
                        User.query.filter_by(user_id=item.user_id).
                        first().username) for item in
                        Reporter.query.order_by('user_id')]
    assignee_choices = [(item.user_id,
                        User.query.filter_by(user_id=item.user_id).
                        first().username) for item in
                        Assignee.query.order_by('user_id')]
    project_choices = [(item.project_id, item.title) for item in
                       Project.query.order_by('project_id')]
    summary = StringField(
        "Summary", validators=[DataRequired(), Length(1, 72)])
    description = StringField("Description", validators=[Length(0, 256)])
    status = SelectField(
        "Status", choices=status_choices, validate_choice=False)
    issue_type = SelectField(
        "Issue Type", choices=issue_type_choices, validate_choice=False)
    priority = SelectField(
        "Priority", choices=priority_choices, validate_choice=False)
    version = StringField(
        "Version", validators=[DataRequired(), Length(1, 30)])
    reporter = SelectField(
        "Reporter", choices=reporter_choices, validate_choice=False)
    assignee = SelectField(
        "Assignee", choices=assignee_choices, validate_choice=False)
    project = SelectField(
        "Project", id='select_project', choices=project_choices,
        validate_choice=False)
    component = SelectMultipleField(
        "Component", option_widget=widgets.CheckboxInput(),
        id='select_component', coerce=int)
    # CC = SelectMultipleField("CC",validators=[DataRequired(), Length(2, 50)])
    submit = SubmitField("Submit")


class SearchBugForm(FlaskForm):
    search_input = StringField(
        "Search Bugs", validators=[DataRequired(), Length(1, 72)],
        render_kw={"placeholder": "Search Bugs"})
    search = SubmitField("Go")

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchBugForm, self).__init__(*args, **kwargs)


class CreateProjectForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(2, 50)])
    description = StringField(
        "Description", validators=[DataRequired(), Length(2, 80)])
    start = DateField("Project Start Date", validators=[DataRequired()])
    end = DateField("Project End Date", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CreateComponentForm(FlaskForm):
    name = StringField("Component", validators=[DataRequired(), Length(2, 50)])
    project_id = IntegerField("Project Id")
    submit = SubmitField("Submit")

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        component = Component.query.filter_by(
            name=self.name.data, project_id=self.project_id.data).first()
        if component:
            self.name.errors.append(
                "Component is already present for the project.")
            return False
        return True


class DeleteBugForm(FlaskForm):
    delete = SubmitField("Yes")


class CommentForm(FlaskForm):
    body = StringField('', validators=[DataRequired()])
    submit = SubmitField("Submit")


class EditCommentForm(FlaskForm):
    save = SubmitField("Save Changes")


class DeleteCommentForm(FlaskForm):
    confirm_delete = SubmitField("Yes")
