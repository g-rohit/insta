import sys
sys.path.append('../../')
from project import db

import os
import requests
from project import serial
from project.users.models import Users
from project.users.forms import PasswordResetForm
from werkzeug.security import generate_password_hash
from project.users.emails import password_reset_link
from project.users.request_acceptor import InstagramBot
from flask_login import login_required, login_user, logout_user, current_user
from flask import Blueprint, render_template, redirect, url_for, request, session


users_blueprint = Blueprint('users', __name__, template_folder='templates')


@login_required
@users_blueprint.route('/accept_pending_requests', methods=['GET', 'POST'])
def accept_pending_requests():

    if request.method == 'POST':
        no_of_request_to_accept = request.form['noOfFollowers']
        current_user.accept_request_count = no_of_request_to_accept
        db.session.commit()

        return redirect(url_for('users.pending_request_count'))
    return render_template('AcceptRequests.html')


@login_required
@users_blueprint.route('/live_counter', methods=['GET','POST'])
def live_counter():

    if request.method == 'POST':
        instagram_username = request.form['instagram_username']
        response = requests.get('https://www.instagram.com/web/search/topsearch/?query={un}'.format(un=instagram_username))
        resp = response.json()
        for i in resp['users']:
            if i['user']['username'] == instagram_username.lower():
                user_id = i['user']['pk']
                count = i['user']['follower_count']

        return render_template('count_display.html', user_count=count)
    return render_template('LiveCounter.html')


@login_required
@users_blueprint.route('/pending_request_count_api', methods=['GET','POST'])
def pending_request_count():

    if request.method == 'POST':
        instagram_username = current_user.insta_username
        instagram_password = request.form['instagram_password']

        session['insta_username'] = instagram_username
        session['insta_password'] = instagram_password

        insta_obj = InstagramBot(instagram_username, instagram_password)
        insta_obj.login()
        resp = insta_obj.pending_request_count()
        insta_obj.closeBrowser()
        return render_template('acceptor_display.html', resp=resp)

    return render_template('request_acceptor.html')


@login_required
@users_blueprint.route('/request_acceptor_api', methods=['GET','POST'])
def request_acceptor():

    instagram_accept_request_count = current_user.accept_request_count
    if instagram_accept_request_count is None:
        return redirect(url_for('users.accept_pending_requests'))
    instagram_accept_request_count = instagram_accept_request_count[:-1]
    instagram_accept_request_count = int(instagram_accept_request_count) * 1000
    instagram_username = current_user.insta_username
    instagram_password = session['insta_password']


    insta_obj = InstagramBot(instagram_username, instagram_password)
    insta_obj.login()
    counts = insta_obj.pending_request_count()
    if counts < instagram_accept_request_count:
        resp = insta_obj.accept_pending_requests(counts)
    else:
        resp = insta_obj.accept_pending_requests(instagram_accept_request_count)
    insta_obj.closeBrowser()

    return render_template('result.html', resp=resp)



@users_blueprint.route('/forgot_password', methods=['GET','POST'])
def forgot_password():

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

            return redirect(url_for('users.pending_request_count'))

    return render_template('index.html')


@login_required
@users_blueprint.route('/logout')
def logout():
    logout_user()
    print("user logged out")
    return redirect(url_for('core.index'))