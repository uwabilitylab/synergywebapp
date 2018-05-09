import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #UPLOAD_FOLDER = '/Users/claire_mit/Documents/Steele_Lab/SynergyWebApp/app/csvfiles'
    BASE_FOLDER = '/mnt/data/www/synergywebapp/'
    UPLOAD_FOLDER = BASE_FOLDER + '/app/csvfiles'
    PLOT_FOLDER = BASE_FOLDER + '/app/static/plots'
