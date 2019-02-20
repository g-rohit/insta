import sys
sys.path.append('../../')

import datetime
from flask_login import UserMixin
from project import db, login_manager
from werkzeug.security import check_password_hash, generate_password_hash


@login_manager.user_loader
def admin_load(admin_id):
    return Admin.query.get(admin_id)


class Admin(db.Model, UserMixin):
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(256))
    hashed_password = db.Column(db.String(100))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,email,password):
        self.email = email
        self.hashed_password = generate_password_hash(password)

    def check_hashed_password(self,password):
        return check_password_hash(self.hashed_password, password)

    def __str__(self):
        return self.email