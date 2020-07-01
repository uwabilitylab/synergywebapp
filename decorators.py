from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user
from app.models import User, File, Job

def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function

def admin_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.username != "Admin":
            flash('You are not authorized to view this page!', 'warning')
            return redirect(url_for('userHomepage'))
        return func(*args, **kwargs)

    return decorated_function

def access_files(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        rule = request.path.split("/")
        j = Job.query.filter_by(job_hash = rule[-1]).first()
        f = File.query.filter_by(new_file_path = j.job_file_id).first()
        u = User.query.filter_by(id = f.file_user_id).first()

        if current_user.username != u.username:
            flash('You are not authorized to view this page!', 'warning')
            return redirect(url_for('userHomepage'))
        return func(*args, **kwargs)

    return decorated_function
