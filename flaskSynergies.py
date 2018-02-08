import scipy.io as sio
from sklearn.decomposition import NMF
import time
import itertools
import multiprocessing
import numpy as np
#from multiprocessing import Pool, freeze_support

def calculate_tVAF(V,W,H,vaf):

    err_sub = V - np.dot(np.transpose(W),H)
    vaf = 1-sum(sum(np.square(err_sub)))/sum(sum(np.square(V)))

    return vaf

def calculate_Synergies(emg, channels):

    WW = []
    HH = []
    tVAF = []
    W_keep = []
    H_keep = []

    start = time.time()

    #emg = np.transpose(emg)
    for i in range(5): # second dimension of the matrix

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
        for k in range(len(W_keep)):
            W_keep[k]=W_keep[k]/W_keep[k].max()

        WW.append(W_keep)
        HH.append(H_keep)

    end = time.time()

    return (WW, tVAF, HH)
