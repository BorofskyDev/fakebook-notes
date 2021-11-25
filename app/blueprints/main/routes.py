from os import stat
from . import bp as app
from app import db
from flask import request, render_template, url_for, redirect, flash
from datetime import datetime
from app.blueprints.auth.models import User
from app.blueprints.main.models import Post
from flask_login import login_user, logout_user, current_user

@app.route('/')
def home():

    print(current_user.is_authenticated)

    context = {
        'first_name' : 'Joel',
        'last_name' : 'Borofsky',
        'email' : 'jb@jb.com',
        'posts' : Post.query.order_by(Post.date_created.desc()).all()
        
    }
    return render_template('index.html', **context)

@app.route('/about')
def about():
   
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    u = User.query.get(current_user.get_id())
    context = {
        'posts': Post.query.filter_by(user_id=u.get_id()).order_by(Post.date_created.desc()).all()      
    }
        #thank you Miguel for your flask turtorial being online
    if request.method == "POST":
        f_name = request.form.get('f_name')
        l_name = request.form.get('l_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
                #Bug fix for W5D2 Homework      
        if not password and not confirm_password:
            u.first_name = f_name
            u.last_name = l_name
            u.email = email
            db.session.commit()
            flash('Your profile has been successfully updated.', 'info')
            return redirect(request.referrer)
        else:
            if password == confirm_password:
                u.first_name = f_name
                u.last_name = l_name
                u.email = email
                u.password = password
                u.generate_password(u.password)
                db.session.commit()
                flash('Your profile has been successfully updated.', 'info')
                return redirect(request.referrer) 
            else: 
                flash("Your passwords did not match. ", 'warning')
                return redirect(request.referrer)
    return render_template('profile.html', **context)

@app.route('/new_post', methods=['POST'])
def create_new_post():
    status = request.form.get('user_status')

    if status:
        p = Post(body=status, user_id=current_user.get_id())
        db.session.add(p)
        db.session.commit()
        flash('You have successfully created a new post.', 'success')
    else:
        flash('Empty messages not allowed. Please post something', 'warning')
    return redirect(url_for('main.home'))


