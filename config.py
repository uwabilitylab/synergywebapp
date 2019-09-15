import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'run', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #UPLOAD_FOLDER = '/Users/claire_mit/Documents/Steele_Lab/SynergyWebApp/app/csvfiles'
    # BASE_FOLDER = '/mnt/data/www/synergywebapp/'
    # BASE_FOLDER = '/Users/claire_mit/Documents/Steele_Lab/SynergyWebApp'
    BASE_FOLDER = os.environ.get('BASE_FOLDER')
    UPLOAD_FOLDER = BASE_FOLDER + '/app/csvfiles'
    PLOT_FOLDER = BASE_FOLDER + '/app/static/plots'
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['synergy.me.uw@gmail.com']
