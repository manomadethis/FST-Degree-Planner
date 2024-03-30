from app import create_app
from flask import flash, get_flashed_messages, redirect, render_template, request, send_from_directory, url_for
from flask_login import login_user, UserMixin, LoginManager
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
import os
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash

engine = create_engine('postgresql://postgres:p%40ssword@localhost/degreeplannerdb')

# Test database connection
try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("Database connection is active.")
except Exception as e:
    print("Failed to connect to the database. Error: {}".format(e))

def hash_password(password):
    return generate_password_hash(password)

app = create_app()
app.config['SECRET_KEY'] = os.urandom(24)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def get_id(self):
        return self.username

class LoginForm(FlaskForm):
    identifier = StringField('Email or Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

    def validate_email(self, email):
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email.data})
            user = result.fetchone()
        if user is None:
            raise ValidationError('Invalid email address. Please try again.')

    def validate_password(self, password):
        with engine.connect() as connection:
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
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email.data})
            user = result.fetchone()
        if user is not None:
            raise ValidationError('Email already in use. Please use a different email address.')

    def validate_username(self, username):
        with engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM users WHERE username = :username"), {"username": username.data})
            user = result.fetchone()
        if user is not None:
            raise ValidationError('Please use a different username.')

@login_manager.user_loader
def load_user(user_id):
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM users WHERE username = :username"), {"username": user_id})
        user_data = result.fetchone()._asdict()
    if user_data is not None:
        return User(username=user_data['username'], email=user_data['email'], password=user_data['password'])
    return None

@app.route('/')
def home():
    return send_from_directory('static/landing', 'landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        try:
            # Fetch user data from the database
            with engine.connect() as connection:
                result = connection.execute(text("SELECT * FROM users WHERE email = :identifier OR username = :identifier"), {"identifier": form.identifier.data})
                user_data = result.fetchone()._asdict()

            if user_data is None:
                flash('Login failed. Please try again.', 'danger')
                return render_template('login_form.html', form=form)

            # Create a User object
            user = User(username=user_data['username'], email=user_data['email'], password=user_data['password'])

            # Log the user in
            login_user(user)

            flash('Login successful!', 'success')
            return render_template('login_form.html', form=form)
        except Exception as e:
            flash('Login failed. Please try again.', 'danger')
    return render_template('login_form.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        # validation passed, you can register the user
        hashed_password = hash_password(form.password.data)
        try:
            with engine.connect() as connection:
                trans = connection.begin()  # Start a transaction
                result = connection.execute(text("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)"),
                                {"email": form.email.data, "username": form.username.data, "password": hashed_password})
                trans.commit()  # Commit the transaction
            flash('Registration successful!', 'success')
            return render_template('signup_form.html', form=form)
        except Exception as e:
            flash('Registration failed. Error: {}'.format(e), 'danger')
    return render_template('signup_form.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)