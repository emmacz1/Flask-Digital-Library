from app.forms import UserLoginForm
from app.models import User, db, check_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user

auth = Blueprint('auth', __name__, template_folder='auth_templates')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('site.home'))
    return render_template('sign_up.html', form=form)

@auth.route('/signin', methods=['GET', 'POST'])
def signin():
    form = UserLoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('site.profile'))
        flash('Invalid credentials', 'danger')
    return render_template('sign_in.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('site.home'))
