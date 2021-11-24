from app import app, db
from flask import request, render_template, url_for, redirect, flash
from datetime import datetime
from app.models import Post, User
from flask_login import login_user, logout_user, current_user

@app.route('/')
def home():

    print(current_user.is_authenticated)

    context = {
        'first_name' : 'Joel',
        'last_name' : 'Borofsky',
        'email' : 'jb@jb.com',
        'posts' : Post.query.order_by(Post.date_created.desc()).all()
        # 'posts' : [
        #     {
        #         'id' : 1,
        #         'body' : 'This is the first blog post',
        #         'date_created' : datetime.utcnow()
        #     },
        #     {
        #         'id' : 2,
        #         'body' : 'This is the second blog post',
        #         'date_created' : datetime.utcnow()
        #     },
        #     {
        #         'id' : 3,
        #         'body' : 'This is the third blog post',
        #         'date_created' : datetime.utcnow()
        #     },
        # ]
    }
    return render_template('index.html', **context)

@app.route('/about')
def about():
    # data = {
    #     'first_name' : 'Joel',
    #     'last_name' : 'Borofsky'
    # }
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

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
        return redirect(url_for('login'))
    return render_template('register.html')

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
    return redirect(url_for('home'))

@app.route('/Login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = User.query.filter_by(email=request.form.get('email')).first()
        if u is not None and u.check_password(request.form.get('password')):
            login_user(u)
            flash('You are now logged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Your username or password is incorrect.', 'danger')
            return redirect (request.referrer)
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    flash('User logged out successfully', 'info')
    return redirect(url_for('login'))

