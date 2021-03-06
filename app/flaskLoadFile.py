from app.process_EMG import step02_processEMG
import pandas as pd
import numpy as np

def readFlaskExcel(excelfile, included_mus, lowpass, highpass):

    if excelfile.endswith(".csv"):
        loadedfile = pd.read_csv(excelfile)
    elif excelfile.endswith(".tsv"):
        loadedfile = pd.read_csv(excelfile, delimiter='\t')
    else:
        print("Not an acceptable file format")

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
        if i in included_mus:
            xdata['Time %s' %(j)] = np.array(loadedfile[column[i-1]], dtype=np.float64)
            ydata['EMG %s' %(j)] = np.array(loadedfile[column[i]], dtype=np.float64)
            aRATE['aRATE %s' %(j)] = int(round(1/((loadedfile[column[i-1]][len(loadedfile[column[i-1]])-1]-loadedfile[column[i-1]][0])/len(loadedfile[column[i-1]]))))
            rawEMG, pEMG = step02_processEMG(ydata['EMG %s' %(j)], aRATE['aRATE %s' %(j)], int(highpass), 4, int(lowpass)  , 4, 'EMG %s' %(j))
            yfilt['EMGFilt %s' %(j)] = pEMG
            ydata['EMG %s' %(j)] = np.array(rawEMG.tolist(), dtype=np.float64)
            yfiltarray.append(pEMG)
            columnNames.append(column[i])

            j = j + 1;

    return xdata, ydata, aRATE, yfilt, yfiltarray, results, columnNames
