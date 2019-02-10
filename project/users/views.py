import os
from project import serial
from project.users.models import Users
from project.users.emails import password_reset_link
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user


users_blueprint = Blueprint('users', __name__, template_folder='templates')


@login_required
@users_blueprint.route('/accept_pending_requests')
def accept_pending_requests():
    return render_template('AcceptRequests.html')


@login_required
@users_blueprint.route('/live_counter')
def live_counter():
    return render_template('LiveCounter.html')


@users_blueprint.route('/forgot_password', methods=['GET','POST'])
def forgot_password():

    # throw an exception that registered user does nt exis if not at the front end

    if request.method == 'POST':
        registered_email = request.form['resetPassword']
        print(registered_email)

        user = Users.query.filter_by(email=registered_email).first_or_404()
        if user is not None:

            token = serial.dumps(user.email, salt='password_reset')
            link = url_for('users.reset_password', token=token, _external=True)
            password_reset_link(os.environ.get('GMAIL_EMAIL'), user.email, link)

            return redirect(url_for('users.login'))

    return render_template("index.html")


@users_blueprint.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    try:
        email = serial.loads(token, salt='password_reset', max_age=36000)
        user = Users.query.filter_by(email=email).first_or_404()

        if user:
            # Do something  Either make a form of password reset or create a new pass and send the user
            return redirect(url_for('users.login'))
    except:

        return render_template('testing.html')



@users_blueprint.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':
        email = request.form['userEmailID']
        password = request.form['userLoginPassword']

        user = Users.query.filter_by(email=email).first()

        if user.check_hashed_password(password) and user is not None:
            login_user(user)
            print("User Logged In!!!")

            return render_template('index.html')

    return render_template('index.html')


@login_required
@users_blueprint.route('/logout')
def logout():
    logout_user()
    print("user logged out")
    return redirect(url_for('core.index'))