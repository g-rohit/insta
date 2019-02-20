import os
from flask import Flask
from flask_mail import Mail
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import URLSafeTimedSerializer
# from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy_utils import create_database, database_exists


app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Farees143k@localhost/instamax'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.environ.get('GMAIL_EMAIL')
app.config['MAIL_PASSWORD'] = os.environ.get('GMAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
db = SQLAlchemy(app)
mail = Mail(app)
serial = URLSafeTimedSerializer('MYSUPERSECRETKEY')

if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
    create_database(app.config['SQLALCHEMY_DATABASE_URI'])

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'users.login'

#########   ###########################################################################################

from project.core.views import core_blueprint
from project.users.views import users_blueprint
from project.admin.views import admins_blueprint
from project.error_pages.handler import error_pages


app.register_blueprint(error_pages)
app.register_blueprint(core_blueprint)
app.register_blueprint(users_blueprint)
app.register_blueprint(admins_blueprint)