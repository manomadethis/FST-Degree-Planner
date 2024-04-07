from flask_login import UserMixin, LoginManager
from app import db, text
from . import login_manager
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.username

@login_manager.user_loader
def load_user(user_id):
    with db.connect() as connection:
        result = connection.execute(text("SELECT * FROM users WHERE username = :username"), {"username": user_id})
        user_data = result.fetchone()._asdict()
    if user_data is not None:
        return User(username=user_data['username'], email=user_data['email'], password=user_data['password'])
    return None