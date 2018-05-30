import scipy.io as sio
from sklearn.decomposition import NMF
import time
import itertools
import multiprocessing
import numpy as np
from math import floor
#from vaf import vaf
#from multiprocessing import Pool, freeze_support

def calculate_tVAF(V,W,H,vaf):

    err_sub = V - np.dot(np.transpose(W),H)
    vaf = 1-sum(sum(np.square(err_sub)))/sum(sum(np.square(V)))

    return vaf

def calculate_vaf(VV,WW,HH):
    HH = np.reshape(HH,(1,-1))
    WW = np.reshape(WW,(1,-1))

    err_sub = VV - np.dot(np.transpose(WW),HH)
    vaf = 1-sum(sum(np.square(err_sub)))/sum(sum(np.square(VV)))

    # return round(vaf,2)
    return floor(vaf*100)/100

def calculate_Synergies(emg, numSyn):

    WW = []
    WWsim = []
    HH = []
    tVAF = []
    W_keep = []
    H_keep = []
    VAF = []

    start = time.time()

    #emg = np.transpose(emg)
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

        tVAF.append(calculate_tVAF(emg, W_keep, H_keep, tVAF))
        for k in range(i+1):
            vafone.append(calculate_vaf(emg, W_keep[k], H_keep[k]))

        for k in range(len(W_keep)):
            W_keep[k]=W_keep[k]/np.max(W_keep[k])

        sp = np.shape(W_keep)
        Wlist = []
        for j in range(sp[0]):
            Wlist.append(list(W_keep[j]))

        WW.append(Wlist)
        HH.append(H_keep)
        VAF.append(vafone)

    end = time.time()
    # for i in range(4):
    #     for j in range(WW[i+1].len):


    return (WW, tVAF, HH, VAF)
