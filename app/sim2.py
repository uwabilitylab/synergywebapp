from scipy.stats.stats import pearsonr
import numpy as np


def similarity2(Wmatrix):

    newW = []
    newW.append(Wmatrix[0])
    for i in range(len(Wmatrix)-1):
        x = np.array(Wmatrix[i])
        if (np.shape(x)==(8,)):
            x = np.reshape(x,[1,8])

        y = np.array(Wmatrix[i+1])
        sx = np.shape(x)
        sy = np.shape(y)
        corr = -1*np.ones([sx[0],sy[0]])
        for j in range(sx[0]):
            for k in range(sy[0]):
                [corr[j,k], a] = pearsonr(x[j,:],y[k,:])

        oneW = -1*np.ones([sy[0],sy[1]])
        flatCorr = np.reshape(corr, [1,np.size(corr)])
        for j in range(sx[0]-1):
            maxAll = np.argmax(flatCorr)
            corr[maxAll//(sy[0]),:] = -2
            corr[:,maxAll%(sy[0])] = -2
            oneW[maxAll//(sy[0]),:] = list(y[maxAll%(sy[0]),:])
            flatCorr = np.reshape(corr, [1,np.size(corr)])

        maxAll = np.argmax(flatCorr)
        corr[:,maxAll%(sy[0])] = -2
        oneW[maxAll//(sy[0]),:] = list(y[maxAll%(sy[0]),:])
        flatCorr = np.reshape(corr, [1,np.size(corr)])
        maxLast = np.argmax(flatCorr)
        oneW[sy[0]-1,:] = list(y[maxLast%(sy[0]),:])
        q = np.shape(oneW)
        twoW = []
        for j in range(q[0]):
            twoW.append(list(oneW[j,:]))

        newW.append(twoW)

    return newW
