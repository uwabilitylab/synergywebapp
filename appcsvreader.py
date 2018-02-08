from flask_bootstrap import Bootstrap
from flask import Flask, render_template, Markup, request, jsonify, redirect, url_for
from importCSV import CSVreader
import pandas as pd
from werkzeug import secure_filename
from json import dumps, loads, JSONEncoder, JSONDecoder
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




app = Flask(__name__)

xdata = []
ydata = []
size = 0;

@app.route("/import", methods=['GET', 'POST', 'PUT'])
def doimport():
    if request.method == 'POST':
        excel = request.files['file']
        xdata, ydata, aRATE, yfilt, yfiltarray = readFlaskExcel(excel)

        set1a = zip(xdata['Time 1'], ydata['EMG 1'])
        set1b = zip(xdata['Time 1'], yfilt['EMGFilt 1'])

        set2a = zip(xdata['Time 2'], ydata['EMG 2'])
        set2b = zip(xdata['Time 2'], yfilt['EMGFilt 2'])

        set3a = zip(xdata['Time 3'], ydata['EMG 3'])
        set3b = zip(xdata['Time 3'], yfilt['EMGFilt 3'])

        set4a = zip(xdata['Time 4'], ydata['EMG 4'])
        set4b = zip(xdata['Time 4'], yfilt['EMGFilt 4'])

        set5a = zip(xdata['Time 5'], ydata['EMG 5'])
        set5b = zip(xdata['Time 5'], yfilt['EMGFilt 5'])

        set6a = zip(xdata['Time 6'], ydata['EMG 6'])
        set6b = zip(xdata['Time 6'], yfilt['EMGFilt 6'])

        set7a = zip(xdata['Time 7'], ydata['EMG 7'])
        set7b = zip(xdata['Time 7'], yfilt['EMGFilt 7'])

        set8a = zip(xdata['Time 8'], ydata['EMG 8'])
        set8b = zip(xdata['Time 8'], yfilt['EMGFilt 8'])

        set9a = zip(xdata['Time 9'], ydata['EMG 9'])
        set9b = zip(xdata['Time 9'], yfilt['EMGFilt 9'])

        set10a = zip(xdata['Time 10'], ydata['EMG 10'])
        set10b = zip(xdata['Time 10'], yfilt['EMGFilt 10'])

        set11a = zip(xdata['Time 11'], ydata['EMG 11'])
        set11b = zip(xdata['Time 11'], yfilt['EMGFilt 11'])

        set12a = zip(xdata['Time 12'], ydata['EMG 12'])
        set12b = zip(xdata['Time 12'], yfilt['EMGFilt 12'])

        set13a = zip(xdata['Time 13'], ydata['EMG 13'])
        set13b = zip(xdata['Time 13'], yfilt['EMGFilt 13'])

        set14a = zip(xdata['Time 14'], ydata['EMG 14'])
        set14b = zip(xdata['Time 14'], yfilt['EMGFilt 14'])

        set15a = zip(xdata['Time 15'], ydata['EMG 15'])
        set15b = zip(xdata['Time 15'], yfilt['EMGFilt 15'])

        set16a = zip(xdata['Time 16'], ydata['EMG 16'])
        set16b = zip(xdata['Time 16'], yfilt['EMGFilt 16'])
    #    if request.method == 'PUT':
           #if request.form['submit'] == 'Do Something':
              # calculate_Synergies(yfilt, [1,2,3,4,5,6,7,8])
    #          return render_template('synergyDisplay.html', form=form)
    #    new = yfilt.values()
    #    newfilt = new['dict_values']
    #    print(newfilt)
    #    print(yfiltarray.shape())
        legend = 'Monthly Data'
        list1 = [4,6,8,9,10,11,12,13]
        WW, tVAF, HH = calculate_Synergies([yfiltarray[i] for i in list1],[1,2,3,4,5,6,7,8])
        labels = ["5","7","9","10","11","12","13","14"]
        labeltvaf = ["1 Synergy","2 Synergies","3 Synergies","4 Synergies","5 Synergies",]
        return render_template('basic6.html', Wmatrix11 = WW[0][0],
            Wmatrix21 = WW[1][0], Wmatrix22 = WW[1][0],
            Wmatrix31 = WW[2][0], Wmatrix32 = WW[2][1], Wmatrix33 = WW[2][2],
            Wmatrix41 = WW[3][0], Wmatrix42 = WW[3][1], Wmatrix43 = WW[3][2], Wmatrix44 = WW[3][3],
            Wmatrix51 = WW[4][0], Wmatrix52 = WW[4][1], Wmatrix53 = WW[4][2], Wmatrix54 = WW[4][3], Wmatrix55 = WW[4][4],
            labeltvaf = labeltvaf, tVAF = tVAF,
            labels = labels, legend = legend, set1a = set1a, set1b = set1b,
            set2a = set2a, set2b = set2b, set3a = set3a, set3b = set3b,
            set4a = set4a, set4b = set4b, set5a = set5a, set5b = set5b,
            set6a = set6a, set6b = set6b, set7a = set7a, set7b = set7b,
            set8a = set8a, set8b = set8b, set9a = set9a, set9b = set9b,
            set10a = set10a, set10b = set10b, set11a = set11a, set11b = set11b,
            set12a = set12a, set12b = set12b, set13a = set13a, set13b = set13b,
            set14a = set14a, set14b = set14b, set15a = set15a, set15b = set15b,
            set16a = set16a, set16b = set16b)
    return render_template('userpoints.html')

@app.route("/chart_view", methods=['GET'])
def chartupload():
    #xdata = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    #ydata = [1, 2, 3, 4, 5, 6, 7, 8]
    return render_template('basic3.html', xdata=xdata, ydata=ydata)

bootstrap = Bootstrap(app)

if __name__ == '__main__':
  app.run()
