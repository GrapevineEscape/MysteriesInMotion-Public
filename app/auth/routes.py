from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from app.extensions import db

auth_bp = Blueprint('auth', __name__)

# Hardcoded registration code for MVP (will move to Admin settings later)
PERFORMER_REG_CODE = "MIM2025"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('performer.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Debugging print
        print(f"Form Data: first_name={form.first_name.data}, last_name={form.last_name.data}")

        if form.registration_code.data != PERFORMER_REG_CODE:
            flash('Invalid registration code.', 'danger')
            return render_template('register.html', form=form)
        
        # Check if the email is already taken
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html', form=form)
        
        # Create the new performer
        new_user = User(
            first_name=form.first_name.data or "Unknown",
            last_name=form.last_name.data or "Unknown",
            email=form.email.data,
            is_admin=False
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    # Missing return statement for GET requests or failed form validation
    return render_template('register.html', form=form)
