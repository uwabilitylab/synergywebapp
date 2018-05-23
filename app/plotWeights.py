import os
from matplotlib import pyplot as plt
from matplotlib import lines as mlines
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import colors



# This file is used to generate the EMG raw and processed figures.
# This is done because loading all the individual data points at a time takes too long.
def plotWeights(WW, jobfile, muscleNamesShort, pp):

    os.mkdir('app/static/plots/Wei_Plots_%s' %(jobfile))

    filenames = open('app/static/plots/Wei_Plots_%s/filenames.txt' %(jobfile), 'w+')
    # pp = PdfPages('app/static/plots/matplots_%s.pdf' %(jobfile))

    # colors = ['#85754d', '#4b2e83', '#67832e', '#842E3D', '#3c6362', '#000000']
    faceColors = [[colors.to_rgba('#85754d', alpha=0.5)],[colors.to_rgba('#4b2e83', alpha=0.5)],[colors.to_rgba('#67832e', alpha=0.5)],[colors.to_rgba('#842E3D', alpha=0.5)],[colors.to_rgba('#3c6362', alpha=0.5)],[colors.to_rgba('#000000', alpha=0.5)]]
    EdgeColors = [[colors.to_rgba('#85754d', alpha=1)],[colors.to_rgba('#4b2e83', alpha=1)],[colors.to_rgba('#67832e', alpha=1)],[colors.to_rgba('#842E3D', alpha=1)],[colors.to_rgba('#3c6362', alpha=1)],[colors.to_rgba('#000000', alpha=1)]]

    k=1
    for i in range(len(WW)):
        for j in range(len(WW[i])):
            fig = plt.figure(figsize=(16,6))

            filename = 'app/static/plots/Wei_Plots_%s/' %(jobfile) + jobfile + 'Wei_%s' %(k) + '.png'
            filenames.write('/static/plots/Wei_Plots_%s/' %(jobfile) + jobfile + 'Wei_%s' %(k) + '.png' + '\n')
            index = np.arange(len(WW[i][j]))

            plt.bar(index, WW[i][j], color = faceColors[j], edgecolor = EdgeColors[j])
            plt.xticks(index, muscleNamesShort)
            plt.ylabel('Weight')
            plt.xlabel('Muscle')
            plt.title('%s Synergy Solution, Synergy %s Weights' %(i+1,j+1))
            plt.savefig(filename, bbox_inches='tight')
            pp.savefig(fig)
            plt.close()
            k = k + 1
