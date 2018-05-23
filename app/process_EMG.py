# -*- coding: utf-8 -*-
"""
Created on Sun Oct 22 15:57:31 2017

@author: claire_mit
"""

import numpy as np
from scipy import signal
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from scipy.fftpack import fft
import scipy


# Filtering
def step02_processEMG(raw_EMG, aRATE, HP_CO, HP_order, LP_CO, LP_order, filename):

#   High-pass filtering
    cutoff = int(HP_CO)
    # if cutoff == 1000:
    #     EMG1 = raw_EMG
    # else :
    b, a = signal.butter(HP_order, cutoff/(aRATE/2),btype='highpass')
    # raw_EMG = np.reshape(raw_EMG,[len(raw_EMG),1])
    EMG1 = signal.filtfilt(b, a, raw_EMG, padlen=0)

#   Demeaning
    EMG2 = (EMG1 - np.mean(EMG1))

#   Rectify
    EMG3 = np.abs(EMG2)

#   Smooth with zero lag third-order low-pass (40 Hz) Butterworth
    cutoff = int(LP_CO)
    b1, a1 = signal.butter(LP_order, cutoff/(aRATE/2), btype='lowpass')
    pEMG = signal.filtfilt(b1, a1, EMG3, padlen=0)

#   Normalize
    pEMG = pEMG/pEMG.max()
    raw_EMG = raw_EMG/raw_EMG.max()

#   Zero out negative values
    pEMG = pEMG.clip(min=0)

    return raw_EMG, pEMG
