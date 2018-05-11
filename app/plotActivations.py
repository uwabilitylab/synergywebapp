import os
from matplotlib import pyplot as plt
from matplotlib import lines as mlines
from matplotlib.backends.backend_pdf import PdfPages

# This file is used to generate the EMG raw and processed figures.
# This is done because loading all the individual data points at a time takes too long.
def plotAct(xdata, HH, jobfile, pp):

    os.mkdir('app/static/plots/Act_Plots_%s' %(jobfile))

    filenames = open('app/static/plots/Act_Plots_%s/filenames.txt' %(jobfile), 'w+')
    # pp = PdfPages('app/static/plots/matplots_%s.pdf' %(jobfile))

    colors = ['#85754d', '#4b2e83', '#67832e', '#842E3D', '#3c6362', '#000000']

    k=1
    for i in range(len(HH)):
        for j in range(len(HH[i])):
            fig = plt.figure(100*(k), figsize=(16,6))

            filename = 'app/static/plots/Act_Plots_%s/' %(jobfile) + jobfile + 'Act_%s' %(k) + '.png'
            filenames.write('/static/plots/Act_Plots_%s/' %(jobfile) + jobfile + 'Act_%s' %(k) + '.png' + '\n')

            weight = plt.plot(xdata['Time %s' %(1)], HH[i][j], color = colors[j])
            plt.ylabel('Amplitude')
            plt.xlabel('Time')
            plt.title('%s Synergy Solution, Synergy %s Activation' %(i+1,j+1))
            plt.savefig(filename, bbox_inches='tight')
            pp.savefig(fig)
            plt.close()
            k = k + 1
