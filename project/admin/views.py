import sys
sys.path.append('../../')

import datetime
from datetime import timedelta
from project.admin.models import Admin
from project.users.models import Users
from flask_login import login_required, login_user, logout_user
from flask import Blueprint, redirect, request, render_template, url_for


admins_blueprint = Blueprint('admin', __name__, template_folder='templates')


@admins_blueprint.route('/admin_login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        admin_email = request.form['admin_email']
        admin_password = request.form['admin_password']

        # new_admin = Admin(email='admin',
        #                   password='admin')
        # from project import db
        #
        # db.session.add(new_admin)
        # db.session.commit()
        # return "True"
        admin = Admin.query.filter_by(email=admin_email).first_or_404()
        if admin.check_hashed_password(admin_password) and admin is not None:
            login_user(admin)

            next = request.args.get('next')

            if next == None or not next[0] == '/':
                next = url_for('admin.account')

            return redirect(next)

    return render_template('admin/login.html')


@login_required
@admins_blueprint.route('/admin_account', methods=['GET','POST'])
def account():

    if request.method == 'POST':
        subscription = request.form["subscriptions"]
        username = request.form["username"]
        is_subs = request.form["is_subscribed"]
        print(subscription, username, is_subs)

        from project import db

        user = Users.query.filter_by(insta_username=username).first_or_404()
        user.subscription_plan = subscription
        user.from_date = datetime.datetime.utcnow()
        user.till_date = datetime.datetime.now() + timedelta(days=int(subscription))
        user.is_subscribed = True
        db.session.commit()

    obj = Users.query.all()
    return render_template('admin/account.html', users=obj)


@login_required
@admins_blueprint.route('/admin_logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))