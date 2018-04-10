# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 15:57:31 2017

@author: claire_mit
"""

import numpy as np
from scipy import signal

# Filtering
def step02_processEMG(raw_EMG, aRATE, HP_CO, HP_order, LP_CO, LP_order, filename):

#   High-pass filtering
    cutoff = HP_CO
    if cutoff == 1000:
        EMG1 = raw_EMG
    else :
        b, a = signal.butter(HP_order, cutoff/(aRATE/2),'highpass')
        raw_EMG = np.reshape(raw_EMG,[len(raw_EMG),1])
        # print(np.shape(raw_EMG))
        EMG1 = signal.filtfilt(b, a, raw_EMG, padlen=0)

#   Demeaning
#    EMG2 = np.empty([len(EMG1),len(EMG1[0])])
#    for i in range(len(EMG1[0])):
#        np.append(EMG2, (EMG1[:,i] - np.mean(EMG1[:,i],0)))
    EMG2 = (EMG1 - np.mean(EMG1))

#   Rectify
    EMG3 = np.abs(EMG2)

#   Smooth with zero lag third-order low-pass (40 Hz) Butterworth
    cutoff = LP_CO
    b, a = signal.butter(LP_order, cutoff/(aRATE/2), 'lowpass')
    pEMG = signal.filtfilt(b, a, EMG3, padlen=0)

#    np.save(filename, pEMG)
#   Normalize

    #norm_EMG = pEMG/pEMG.max()
    #raw_norm = raw_EMG/raw_EMG.max()

#   Interpolate
    # Xq = np.arange(round(X[0]), round(X)[len(X)-1],0.01)
    # Yq = np.interp(Xq,pEMG,X)
    pEMG = pEMG/pEMG.max()
    #print(pEMG)
    pnew = [x for xs in pEMG for x in xs]
    #print(pnew.shape())

    raw_EMG = raw_EMG/raw_EMG.max()


    return raw_EMG, pnew
