from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    institution = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    # files = db.relationship('File', backref='users', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    # return c.execute('SELECT (user_id) FROM users WHERE user_id = {idid}'.\
                # format(idid=id))
    return User.query.get(int(id))

class File(db.Model):
    __tablename__ = 'files'
    id = db.Column(db.Integer, primary_key=True)
    file_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    raw_file_path = db.Column(db.String(64), index=True)
    file_user_hash = db.Column(db.String(64), unique = True)
    file_hash = db.Column(db.String(64))
    file_size = db.Column(db.String(64))
    __table_args__ = (
        db.UniqueConstraint('file_user_id', 'file_hash'),
    )

    def __repr__(self):
        return '<FileId {}>'.format(self.raw_file_path)

    def set_file_hash(self, filepath):
        with open(filepath, 'rb') as f:
            self.file_hash = hashlib.md5(f.read()).hexdigest()
        return self.file_hash

    def set_file_path(self, path):
        self.raw_file_path = path

    def set_file_user_hash(self, filepath):
        line = str(self.file_user_id) + filepath
        self.file_user_hash = hashlib.md5(line.encode('utf-8')).hexdigest()
        return self.file_user_hash

class Job(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True)
    job_hash = db.Column(db.String(64))
    job_file_id = db.Column(db.String(64), db.ForeignKey('files.file_user_hash'))
    # included_muscles = db.Column
    lowpass_cutoff = db.Column(db.Integer)
    highpass_cutoff = db.Column(db.Integer)
    synergy_number = db.Column(db.Integer)
    status = db.Column(db.String(64))
    processed_file_path = db.Column(db.String(64))
    ip_address = db.Column(db.String(64))
    time_submitted = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return '<JobId {}>'.format(self.processed_file_path)

    def set_job_hash(self, job):
        self.job_hash = hashlib.md5(job.encode('utf-8')).hexdigest()
        return self.job_hash
