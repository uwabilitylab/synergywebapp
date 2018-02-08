import pandas as pd
from process_EMG import step02_processEMG

# exelfile must be in the following formula
# excelfile = request.files['file']
# in order to get the filename to know the correct extension and load w/ pd
def readFlaskExcel(excelfile):
    filenameEF = excelfile.filename

    if filenameEF.endswith(".csv"):
        loadedfile = pd.read_csv(excelfile)
    elif filenameEF.endswith(".xlsx") or filenameEF.endswith(".xls"):
        loadedfile = pd.read_excel(excelfile)
    else:
        print("Not an acceptable file format")

    column = loadedfile.columns

    xdata = dict()
    ydata = dict()
    aRATE = dict()
    yfilt = dict()

    j = 1;
    yfiltarray = []
    for i in range(len(column)):
        if 'EMG' in column[i]:
            xdata['Time %s' %(j)] = loadedfile[column[i-1]]
            ydata['EMG %s' %(j)] = loadedfile[column[i]]
            aRATE['aRATE %s' %(j)] = int(round(1/((loadedfile[column[i-1]][len(loadedfile[column[i-1]])-1]-loadedfile[column[i-1]][0])/len(loadedfile[column[i-1]]))))
        #    xinterp['TimeInterp %s' %(j)], yfilt['EMGFilt %s' %(j)], ydata['EMG %s' %(j)] = step02_processEMG(ydata['EMG %s' %(j)], aRATE['aRATE %s' %(j)], 20, 4, 10, 4, 'EMG %s' %(j))
        #    yfilt['EMGFilt %s' %(j)], ydata['EMG %s' %(j)] = step02_processEMG(ydata['EMG %s' %(j)], aRATE['aRATE %s' %(j)], 20, 4, 10, 4, 'EMG %s' %(j))
            rawEMG, pEMG = step02_processEMG(ydata['EMG %s' %(j)], aRATE['aRATE %s' %(j)], 20, 4, 10, 4, 'EMG %s' %(j))
            yfilt['EMGFilt %s' %(j)] = pEMG
            ydata['EMG %s' %(j)] = rawEMG
            #print(pEMG.shape())
            #pEMG.flatten()
            yfiltarray.append(pEMG)


            j = j + 1;
    # EMGfile = loadedfile[EMG_cols]
    #
    #         xdata = dict();
    #         ydata = dict();
    #         len(EMGCOLS)
    #         for i in range(len(EMGCOLS)/2):
    #             xdata['Time%s' (i)] = EMGfile[EMGCOLS[2*i]]
    #             ydata['EMG%s' (i)] = EMGfile[EMGCOLS[2*i+1]]
    #             aRATE['aRATE%s' (i)] = int(round(1/(EMGfile[len(EMGCOLS[2*i])-1])))
    return xdata, ydata, aRATE, yfilt, yfiltarray
    #return ydata, aRATE, yfilt
