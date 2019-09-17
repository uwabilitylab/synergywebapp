import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = ''
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'run', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BASE_FOLDER = ''
    UPLOAD_FOLDER = BASE_FOLDER + '/app/csvfiles'
    PLOT_FOLDER = BASE_FOLDER + '/app/static/plots'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    MAIL_SERVER = ''
    MAIL_PORT =
    MAIL_USE_TLS =
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    ADMINS = ['']
