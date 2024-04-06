from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import check_password_hash
from app import db, text

class LoginForm(FlaskForm):
    identifier = StringField('Email or Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

    def validate_email(self, email):
        with db.connect() as connection:
            result = connection.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email.data})
            user = result.fetchone()
        if user is None:
            raise ValidationError('Invalid email address. Please try again.')

    def validate_password(self, password):
        with db.connect() as connection:
            result = connection.execute(text("SELECT * FROM users WHERE email = :identifier OR username = :identifier"), {"identifier": self.identifier.data})
            row = result.fetchone()
            user = row._asdict() if row else None
        if user is None or not check_password_hash(user['password'], password.data):
            raise ValidationError('Invalid password. Please try again.')

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        with db.connect() as connection:
            result = connection.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email.data})
            user = result.fetchone()
        if user is not None:
            raise ValidationError('Email already in use. Please use a different email address.')

    def validate_username(self, username):
        with db.connect() as connection:
            result = connection.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username.data})
            user = result.fetchone()
        if user is not None:
            raise ValidationError('Please use a different username.')