import pandas as pd
from app.process_EMG import step02_processEMG
import time
from app.xydatamaker import xycoordinates
# exelfile must be in the following formula
# excelfile = request.files['file']
# in order to get the filename to know the correct extension and load w/ pd
def readFlaskExcel(excelfile, lowpass, highpass):
    # filenameEF = excelfile.filename

    # if excelfile.endswith(".csv"):
    # # if filenameEF.endswith(".csv"):
    #     loadedfile = pd.read_csv(excelfile)
    #     # try numpy.load text
    # elif excelfile.endswith(".xlsx") or excelfile.endswith(".xls"):
    # # elif filenameEF.endswith(".xlsx") or filenameEF.endswith(".xls"):
    #     loadedfile = pd.read_excel(excelfile)
    #     #try python converter to loadtext format openpy....
    # else:
    #     print("Not an acceptable file format")

    loadedfile = pd.read_excel(excelfile)
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
            xdata['Time %s' %(j)] = loadedfile[column[i-1]]
            ydata['EMG %s' %(j)] = loadedfile[column[i]]
            print(lowpass)

            aRATE['aRATE %s' %(j)] = int(round(1/((loadedfile[column[i-1]][len(loadedfile[column[i-1]])-1]-loadedfile[column[i-1]][0])/len(loadedfile[column[i-1]]))))
            rawEMG, pEMG = step02_processEMG(ydata['EMG %s' %(j)], aRATE['aRATE %s' %(j)], int(highpass), 4, int(lowpass)  , 4, 'EMG %s' %(j))
            yfilt['EMGFilt %s' %(j)] = pEMG
            ydata['EMG %s' %(j)] = rawEMG[:,0].tolist()

            yfiltarray.append(pEMG)
            results.append(xycoordinates(xdata['Time %s' %(j)],ydata['EMG %s' %(j)],yfilt['EMGFilt %s' %(j)]))
            columnNames.append(column[i])

            j = j + 1;

    return xdata, ydata, aRATE, yfilt, yfiltarray, results, columnNames
