from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, ValidationError, Email, Length, EqualTo
from app.models import User

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