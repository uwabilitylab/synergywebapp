import pandas as pd
from app.process_EMG import step02_processEMG
import time
from app.xydatamaker import xycoordinates
import numpy as np
# exelfile must be in the following formula
# excelfile = request.files['file']
# in order to get the filename to know the correct extension and load w/ pd
def readFlaskExcel(excelfile, lowpass, highpass):

    # print(excelfile)
    # filenameEF = excelfile.filename

    if excelfile.endswith(".csv"):
    # if filenameEF.endswith(".csv"):
        loadedfile = pd.read_csv(excelfile)
        # try numpy.load text
    elif excelfile.endswith(".tsv"):
        loadedfile = pd.read_csv(excelfile, delimiter='\t')

    elif excelfile.endswith(".xlsx") or excelfile.endswith(".xls"):
    # elif filenameEF.endswith(".xlsx") or filenameEF.endswith(".xls"):
        loadedfile = pd.read_excel(excelfile, sheet_name = 0)
        #try python converter to loadtext format openpy....
    else:
        print("Not an acceptable file format")
    # xlsx = pd.ExcelFile(excelfile)
    # excelfile = "." + excelfile
    # loadedfile = pd.read_excel(excelfile, sheet_name = 0)
    column = loadedfile.columns

    xdata = dict()
    ydata = dict()
    aRATE = dict()
    yfilt = dict()

    j = 1;
    yfiltarray = []
    results = []
    columnNames = []
    for i in range(len(column)):
        if 'EMG' in column[i]:
            xdata['Time %s' %(j)] = np.array(loadedfile[column[i-1]], dtype=np.float64)
            ydata['EMG %s' %(j)] = np.array(loadedfile[column[i]], dtype=np.float64)
            aRATE['aRATE %s' %(j)] = int(round(1/((loadedfile[column[i-1]][len(loadedfile[column[i-1]])-1]-loadedfile[column[i-1]][0])/len(loadedfile[column[i-1]]))))
            rawEMG, pEMG = step02_processEMG(ydata['EMG %s' %(j)], aRATE['aRATE %s' %(j)], int(highpass), 4, int(lowpass)  , 4, 'EMG %s' %(j))
            yfilt['EMGFilt %s' %(j)] = pEMG
            ydata['EMG %s' %(j)] = np.array(rawEMG[:,0].tolist(), dtype=np.float64)
            yfiltarray.append(pEMG)
            columnNames.append(column[i])

            j = j + 1;

    return xdata, ydata, aRATE, yfilt, yfiltarray, results, columnNames
