import numpy as np


def vaf(VV,WW,HH):

    vaf_all = []
    for i in range(WW):
        vaf_one = []
        for j in range(WW[i]):
            err = VV - np.dot(np.transpose(WW[i][j],HH[i][j]))
            vaf_one.append(1-sum(sum(np.square(err)))/sum(sum(np.square(VV))))
        vaf_all.append(vaf_one)

    return vaf_all
