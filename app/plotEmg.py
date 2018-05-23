import os
from matplotlib import pyplot as plt
from matplotlib import lines as mlines
from matplotlib.backends.backend_pdf import PdfPages


# This file is used to generate the EMG raw and processed figures.
# This is done because loading all the individual data points at a time takes too long.
def plotEMG(xdata, ydata, yfilt, jobfile, muscleNames, pp):

    os.mkdir('app/static/plots/EMG_Plots_%s' %(jobfile))

    filenames = open('app/static/plots/EMG_Plots_%s/filenames.txt' %(jobfile), 'w+')
    # pp = PdfPages('app/static/plots/matplots_%s.pdf' %(jobfile))

    length = len(xdata)

    for i in range(length):
        j = i + 1

        fig = plt.figure(figsize=(16,6))

        filename = 'app/static/plots/EMG_Plots_%s/' %(jobfile) + jobfile + 'EMG_%s' %(j) + '.png'
        filenames.write('/static/plots/EMG_Plots_%s/' %(jobfile) + jobfile + 'EMG_%s' %(j) + '.png' + '\n')

        raw = plt.plot(xdata['Time %s' %(j)], ydata['EMG %s' %(j)], color = '#d9d9d9', label = 'Raw EMG')
        filt = plt.plot(xdata['Time %s' %(j)], yfilt['EMGFilt %s' %(j)], color = '#85754d', label = 'Processed EMG')
        raw_line = mlines.Line2D([], [], color='#d9d9d9',label='Raw EMG')
        filt_line = mlines.Line2D([], [], color='#85754d',label='Processed EMG')

        plt.legend(handles=[raw_line, filt_line])
        plt.xlabel('Time')
        plt.ylabel('Amplitude')
        plt.title(muscleNames[i])
        plt.savefig(filename, bbox_inches='tight')
        pp.savefig(fig)
        plt.close()
