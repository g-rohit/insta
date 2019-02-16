import sys
sys.path.append('../../')
import datetime
from flask_login import UserMixin
from project import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def user_load(user_id):
    return Users.query.get(user_id)


class Users(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    insta_username = db.Column(db.String(100), unique=True)
    hashed_password = db.Column(db.String(100))
    accept_request_count = db.Column(db.String)
    mob_number = db.Column(db.String(20))
    date_time = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __int__(self,email,insta_username,password,mob_number):
        self.email = email
        self.insta_username = insta_username
        self.hashed_password = generate_password_hash(password)
        self.mob_number = mob_number

    def check_hashed_password(self,password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"email {self.email}"