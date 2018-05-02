import os
import pandas as pd

from flask import Flask, render_template, Markup, request, jsonify, flash, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from config import Config

from werkzeug import secure_filename
from flask_login import UserMixin
from decorators import check_confirmed
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
# from json import dumps, loads, JSONEncoder, JSONDecoder
import json
# from process_EMG import step02_processEMG
from scipy import signal
# from flaskLoadFile import readFlaskExcel
# from flaskSynergies import calculate_Synergies, calculate_tVAF
import numpy as np
import scipy.io as sio
from sklearn.decomposition import NMF
import time
import itertools
import multiprocessing
# from xydatamaker import xycoordinates
# from sim2 import similarity2
import csv
from hashlib import sha1
import datetime
import random
import string
import sqlite3

from app import app, db
from app.models import User, File, Job
#
#
# basedir = os.path.abspath(os.path.dirname(__file__))
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'hard to guess string'
# app.config['SQLALCHEMY_DATABASE_URI'] =\
#     'sqlite3:///' + os.path.join(basedir, 'data.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# #
# bootstrap = Bootstrap(app)
# moment = Moment(app)
# # engine = create_engine(app)
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)
# # con = sqlite3.connect('data.db')
# # c = con.cursor()
# login = LoginManager(app)
# login.login_view = 'login'

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Job=Job)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# import routes, models, forms
