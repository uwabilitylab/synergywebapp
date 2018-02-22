from scipy.stats.stats import pearsonr
import numpy as np


def similarity2(Wmatrix):
    newW = []
    newW.append(Wmatrix[0])
    for i in range(len(Wmatrix)-1):
        corr = -1*np.ones((len(Wmatrix[i]),len(Wmatrix[i+1])))
        for j in range(len(Wmatrix[i])):
            for k in range(len(Wmatrix[i+1])):
                corr[j,k] = pearsonr(newW[i][j],Wmatrix[i+1][k])

        oneW = np.zeros(len(Wmatrix[i+1]),len(Wmatrix[i+1][0]))
        for j in range(len(Wmatrix[i])):
            maxAll = np.argmax(corr)
            corr[maxAll(0),:] = -1
            corr[:,maxAll(1)] = -1
            oneW[maxAll(0),:] = Wmatrix[i+1][maxAll(1)]

        maxLast = np.argmax(corr)
        oneW[Wmatrix[i+1].len(),:] = Wmatrix[i+1][maxLast(1)]

        newW.append(list(oneW))

    return newW
