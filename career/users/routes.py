import os
from flask import render_template, send_from_directory, session, url_for, flash, redirect, request, Blueprint, current_app
from career import db, bcrypt
from career.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from career.users.utils import save_picture, send_reset_email
from career.models import User
from flask_login import login_user, current_user, logout_user, login_required
from .jwt_utils import generate_access_token, verify_access_token
import secrets
from PIL import Image

users = Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        # Generate JWT token
        access_token = generate_access_token(user.id)
        # If API request, return JSON with token
        if request.is_json or request.headers.get('Accept') == 'application/json':
            return {"access_token": access_token, "user_id": user.id}, 201
        return redirect(url_for('main.onboarding'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # Generate JWT token
            access_token = generate_access_token(user.id)
            # If API request, return JSON with token
            if request.is_json or request.headers.get('Accept') == 'application/json':
                return {"access_token": access_token, "user_id": user.id}, 200
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('users.login'))
    return render_template('login.html', title='Login', form=form)

# Example: Token-protected API route
from flask import jsonify
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        user_id = verify_access_token(token)
        if not user_id:
            return jsonify({'message': 'Token is invalid or expired!'}), 401
        # Optionally, set user context here
        return f(user_id=user_id, *args, **kwargs)
    return decorated

# Example API endpoint using token authentication
@users.route('/api/profile', methods=['GET'])
@token_required
def api_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'image_file': user.image_file
    })


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext

    # ✅ Use current_app.root_path (points to project root)
    picture_path = os.path.join(current_app.root_path, 'uploads/profile_pic', picture_fn)

    # Make sure folder exists
    os.makedirs(os.path.dirname(picture_path), exist_ok=True)

    # Resize only for non-SVG images
    if f_ext.lower() != ".svg":
        output_size = (125, 125)
        i = Image.open(form_picture)
        i.thumbnail(output_size)
        i.save(picture_path)
    else:
        # Save SVG as is
        form_picture.save(picture_path)

    return picture_fn


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        
        # Update fields from form
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.age = form.age.data
        current_user.qualification = form.qualification.data
        current_user.goal = form.goal.data
        current_user.field_of_interest = form.field_of_interest.data
        current_user.preferred_location = form.preferred_location.data

        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.age.data = current_user.age
        form.qualification.data = current_user.qualification
        form.goal.data = current_user.goal
        form.field_of_interest.data = current_user.field_of_interest
        form.preferred_location.data = current_user.preferred_location

    image_file = url_for('users.uploaded_file', filename='profile_pic/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@users.before_request
def make_session_permanent():
    session.permanent = True

@users.route("/profile")
@login_required
def profile():
    image_file = url_for('users.uploaded_file', filename='profile_pic/' + current_user.image_file)
    return render_template('profile.html', title='Profile', image_file=image_file)

@users.route("/courses")
@login_required
def courses():
    image_file = url_for('users.uploaded_file', filename='profile_pic/' + current_user.image_file)
    return render_template('quiz.html', title='Courses')

@users.route('/uploads/<path:filename>')
def uploaded_file(filename):
    image_file = url_for('users.uploaded_file', filename='profile_pic/' + current_user.image_file)
    return send_from_directory('uploads', filename)