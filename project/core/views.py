from project import db
from project.users.models import Users
from werkzeug.security import generate_password_hash
from flask import render_template, Blueprint, request, redirect, url_for


core_blueprint = Blueprint('core', __name__, template_folder='templates', static_folder='static')


@core_blueprint.route('/', methods=['GET','POST'])
def index():

    errors = []
    if request.method == 'POST':

        email = request.form['emailID']
        insta_username = request.form['InstaID']
        password = request.form['Password']
        confirm_password = request.form['Con_Password']
        phone_number = request.form['telNumber']

        errors = list()
        try:
            phone_number = int(phone_number)
        except:
            errors.append("Invalid Phone Number")


        if password != confirm_password:
            errors.append("Password does not match")

        if type(phone_number) == int and (password == confirm_password):

            new_user = Users(email=email,
                             insta_username=insta_username,
                             hashed_password=generate_password_hash(password),
                             mob_number=phone_number)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('users.login'))
    return render_template('index.html', errors=errors)



@core_blueprint.route('/pricing')
def pricing():
    return render_template('Pricing.html')


@core_blueprint.route('/faq')
def faq():
    return render_template('FAQ.html')

@core_blueprint.route('/contact')
def contact():
    return render_template('Contact.html')
