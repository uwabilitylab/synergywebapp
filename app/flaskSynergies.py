from sklearn.decomposition import NMF
import numpy as np
from math import floor

def calculate_tVAF(V,W,H): #calculate total variance accounted for

    err_sub = V - np.dot(np.transpose(W),H)
    tvaf = 1-sum(sum(np.square(err_sub)))/sum(sum(np.square(V)))

    return tvaf

def calculate_VAF(VV,WW,HH): #calculate variance within each component of a synergy solution
    HH = np.reshape(HH,(1,-1))
    WW = np.reshape(WW,(1,-1))

    err_sub = VV - np.dot(np.transpose(WW),HH)
    vaf = 1-sum(sum(np.square(err_sub)))/sum(sum(np.square(VV)))

    return vaf

def calculate_Synergies(emg, numSyn):

    WW = []
    WWsim = []
    HH = []
    tVAF = []
    W_keep = []
    H_keep = []
    VAF = []

    for i in range(numSyn): # second dimension of the matrix
        vafone = []
        nsyn = i+1
        Err = float('inf')

        replicates = 50

        for j in range(replicates):

            model = NMF(n_components=nsyn, init='random', random_state=None, max_iter=1000, tol=1e-6)
            W = model.fit_transform(emg)
            H = model.components_
            E = model.reconstruction_err_

            if E < Err:
                Err = E
                W_keep = np.transpose(W)
                H_keep = H

        tVAF.append(calculate_tVAF(emg, W_keep, H_keep))
        for k in range(i+1):
            vafone.append(calculate_VAF(emg, W_keep[k], H_keep[k]))

        for k in range(len(W_keep)):
            W_keep[k]=W_keep[k]/np.max(W_keep[k])

        sp = np.shape(W_keep)
        Wlist = []
        for j in range(sp[0]):
            Wlist.append(list(W_keep[j]))

        WW.append(Wlist)
        HH.append(H_keep)
        VAF.append(vafone)

    return (WW, tVAF, HH, VAF)
