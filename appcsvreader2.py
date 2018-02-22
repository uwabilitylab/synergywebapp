from flask_bootstrap import Bootstrap
from flask import Flask, render_template, Markup, request, jsonify, redirect, url_for
from importCSV import CSVreader
import pandas as pd
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

app = Flask(__name__)

xdata = []
ydata = []
size = 0;

@app.route("/import", methods=['GET', 'POST', 'PUT'])
def doimport():
    if request.method == 'POST':
        excel = request.files['file']
        xdata, ydata, aRATE, yfilt, yfiltarray, results, columnNames = readFlaskExcel(excel)

        list1 = [4,6,8,9,10,11,12,13]
        WW, tVAF, HH = calculate_Synergies([yfiltarray[i] for i in list1],[1,2,3,4,5,6,7,8])

        # for i in range(WW.len()-1):
        #     for j in range(WW[i]):
        #         s = similarity2(WW[i][j],WW[i+1][j])


        muscleNames = [columnNames[i] for i in range(16)]
        muscleNamesShort = [columnNames[i] for i in range(8)]
        tVAFlabels = ["1 Synergy","2 Synergies","3 Synergies","4 Synergies","5 Synergies"]
        labels = ["5","7","9","10","11","12","13","14"]

        resultsJson = json.dumps(results)
        WWJson = json.dumps(WW)
        tVAFJson = json.dumps(tVAF)
        MNJson = json.dumps(muscleNames)
        MNSJson = json.dumps(muscleNamesShort)
        print(muscleNamesShort)

        return render_template('basic9.html', resultsJson = resultsJson,
            WWJson = WWJson, labels = labels, tVAFJson = tVAFJson,
            tVAFlabels = tVAFlabels, MNJson = MNJson, muscleNamesShort = muscleNamesShort)

    return render_template('userpoints.html')

bootstrap = Bootstrap(app)

if __name__ == '__main__':
  app.run()
