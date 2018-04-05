import os
import pandas as pd

from flask import Flask, render_template, Markup, request, jsonify, flash, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from vaf import vaf

from werkzeug import secure_filename
# from json import dumps, loads, JSONEncoder, JSONDecoder
import json
from process_EMG import step02_processEMG
from scipy import signal
from flaskLoadFile import readFlaskExcel
from flaskSynergies import calculate_Synergies, calculate_tVAF
import numpy as np
import scipy.io as sio
from sklearn.decomposition import NMF
import time
import itertools
import multiprocessing
from xydatamaker import xycoordinates
from sim2 import similarity2
import csv
from hashlib import sha1
import datetime
import random
import string

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Job(db.Model):
    __tablename__ = 'jobs'
    # id = db.Column(db.Float, primary_key=True)
    id = db.Column(db.String(64), primary_key=True)
    file_path = db.Column(db.String(64), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    status = db.Column(db.String(64))
    ip_address = db.Column(db.String(64))

    def __repr__(self):
        return '<JobId {}>'.format(self.file_path)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Job=Job)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

xdata = []
ydata = []
size = 0;

@app.route("/import", methods=['GET', 'POST'])
def doimport():
    # print(request.method)
    # low = request.form['lowCuttoff']
    # high = request.form['highCuttoff']
    if request.method == 'POST':

        low = request.form['low']
        high = request.form['high']
        address = request.remote_addr
        timeDigest= datetime.datetime.now(tz=None)
        timeFormat = timeDigest.strftime("%Y-%m-%d %H:%M:%S.%f")
        excel = request.files['file']

        xdata, ydata, aRATE, yfilt, yfiltarray, results, columnNames = readFlaskExcel(excel, low, high)
        numSyn = request.form['syn']
        list1 = [4,6,8,9,10,11,12,13]
        WW, tVAF, HH = calculate_Synergies([yfiltarray[i] for i in list1],[1,2,3,4,5,6,7,8],int(numSyn))

        # WW = vaf(WW)
        # WW = similarity2(WW)
        randString = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        line = randString + timeFormat
        m = sha1(line.encode('utf-8')).hexdigest()
        filepath = "./csvfiles/" + m
        with open(filepath + ".csv", "w") as f:
            writer = csv.writer(f)
            writer.writerow(["Highpass"])
            writer.writerow(high)
            writer.writerow(["Lowpass"])
            writer.writerow(low)
            writer.writerow(["Muscles included"])
            writer.writerow(list1)
            writer.writerow(['Unfiltered Emg'])
            for i in range(16):
                writer.writerow(ydata['EMG %s' %(i+1)])
            writer.writerow(['Filtered Emg'])
            for i in range(16):
                writer.writerow(yfilt['EMGFilt %s' %(i+1)])
            writer.writerow(["tVAF"])
            writer.writerow(tVAF)
            writer.writerow(["Weights"])
            for item in WW:
                writer.writerows(item)
            writer.writerow(["Activations"])
            for item in HH:
                writer.writerows(item)


        # db.create_all()
        u = Job(id = m, file_path = filepath, timestamp = timeDigest, status = 'Processed', ip_address = address)
        db.session.add(u)
        db.session.commit()

        muscleNames = [columnNames[i] for i in range(16)]
        muscleNamesShort = [columnNames[i] for i in range(8)]
        tVAFlabels = ["1 Synergy","2 Synergies","3 Synergies","4 Synergies","5 Synergies"]
        labels = ["5","7","9","10","11","12","13","14"]

        resultsJson = json.dumps(results)
        WWJson = json.dumps(WW)
        tVAFJson = json.dumps(tVAF)
        MNJson = json.dumps(muscleNames)
        MNSJson = json.dumps(muscleNamesShort)
        # print(muscleNamesShort)

        return render_template('basic9.html', resultsJson = resultsJson,
            WWJson = WWJson, labels = labels, tVAFJson = tVAFJson,
            tVAFlabels = tVAFlabels, MNJson = MNJson, muscleNamesShort = muscleNamesShort)

    return render_template('userpoints.html')

# @app.route("/uploading", methods=['GET', 'POST'])
# def douploading():
#     # ajax request
