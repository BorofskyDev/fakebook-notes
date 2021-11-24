from os import stat
from . import bp as app
from app import db
from flask import request, render_template, url_for, redirect, flash
from datetime import datetime
from app.blueprints.auth.models import User
from app.blueprints.main.models import Post
from flask_login import login_user, logout_user, current_user


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(email=request.form.get('email')).first() is not None:
            flash('That email is already in use. Please use a different email.', 'warning')
            return redirect(request.referrer)
        if request.form.get('password') != request.form.get('confirm_password'):
            flash('These passwords do not match. Please try again.', 'warning')
        u = User(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'),
            password=request.form.get('password'),
        )
        u.generate_password(u.password)
        db.session.add(u)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')
@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(email=request.form.get('email')).first()
        if u is not None and u.check_password(request.form.get('password')):
            login_user(u)
            flash('You are now logged in', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Your username or password is incorrect.', 'danger')
            return redirect (request.referrer)

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('User logged out successfully', 'info')
    return redirect(url_for('auth.login'))