import sys
sys.path.append('../../')
from project import db

import os
import requests
from project import serial
from project.users.models import Users
from project.users.forms import PasswordResetForm
from project.users.emails import password_reset_link
from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, login_user, logout_user, current_user



users_blueprint = Blueprint('users', __name__, template_folder='templates')


@login_required
@users_blueprint.route('/accept_pending_requests')
def accept_pending_requests():
    return render_template('AcceptRequests.html')


@login_required
@users_blueprint.route('/live_counter', methods=['GET','POST'])
def live_counter():

    if request.method == 'POST':
        instagram_username = request.form['instagram_username']
        # authentication_api = 'https://api.instagram.com/oauth/authorize/?client_id=f3d4674e8e48455bb17f9bf964431dfc&redirect_uri=http://localhost:5000/follow_count&response_type=code&scope=basic+public_content+follower_list+comments+relationships+likes'
        # return redirect(authentication_api)
        response = requests.get('https://www.instagram.com/web/search/topsearch/?query={un}'.format(un=instagram_username))
        resp = response.json()
        for i in resp['users']:
            if i['user']['username'] == instagram_username.lower():
                user_id = i['user']['pk']
                count = i['user']['follower_count']

        return render_template('count_display.html', user_count=count)

    return render_template('LiveCounter.html')


# @users_blueprint.route('/follow_count')
# def follow_count():
#
#     code = request.args.get('code')
#
#     payload = {
#         'client_id': 'f3d4674e8e48455bb17f9bf964431dfc',
#         'client_secret': 'a7f6991455944e23a17268eeeb378393',
#         'grant_type': 'authorization_code',
#         'redirect_uri': 'http://localhost:5000/follow_count',
#         'code': code
#     }
#     response = requests.post('https://api.instagram.com/oauth/access_token', data=payload).json()
#     access_token = response['access_token']
#     response_get = requests.get("https://api.instagram.com/v1/users/self/?access_token={at}".format(
#         at=access_token)).json()
#     user_count = response_get["data"]["counts"]["followed_by"]
#
#     return render_template('count_display.html', user_count=user_count)


@users_blueprint.route('/forgot_password', methods=['GET','POST'])
def forgot_password():

    # throw an exception that registered user does nt exis if not at the front end

    if request.method == 'POST':
        registered_email = request.form['resetPassword']

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
        # import ipdb; ipdb.set_trace()
        email = serial.loads(token, salt='password_reset', max_age=36000)
        user = Users.query.filter_by(email=email).first_or_404()

        if user is not None:

            form = PasswordResetForm()
            if form.validate_on_submit():
                user.hashed_password = generate_password_hash(form.password.data)
                db.session.commit()

                return redirect(url_for('users.login'))
            return render_template("password_reset.html", form=form)

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