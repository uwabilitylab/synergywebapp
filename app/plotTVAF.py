import os
from matplotlib import pyplot as plt
from matplotlib import lines as mlines
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import colors


# This file is used to generate the EMG raw and processed figures.
# This is done because loading all the individual data points at a time takes too long.
def plotTVAF(tVAF, jobfile, pp):

    os.mkdir('app/static/plots/tVAF_Plots_%s' %(jobfile))

    filenames = open('app/static/plots/tVAF_Plots_%s/filenames.txt' %(jobfile), 'w+')
    # pp = PdfPages('app/static/plots/matplots_%s.pdf' %(jobfile))

    # colors = ['#4b2e83']
    faceColors = [[colors.to_rgba('#4b2e83', alpha=0.5)]]
    EdgeColors = [[colors.to_rgba('#4b2e83', alpha=1)]]


    fig = plt.figure(figsize=(16,6))

    filename = 'app/static/plots/tVAF_Plots_%s/' %(jobfile) + jobfile + 'tVAF' + '.png'
    filenames.write('/static/plots/tVAF_Plots_%s/' %(jobfile) + jobfile + 'tVAF' + '.png' + '\n')
    index = np.arange(len(tVAF))

    plt.bar(index, tVAF, color = faceColors[0], edgecolor = EdgeColors[0])
    plt.xticks(index, index)
    plt.ylabel('tVAF')
    plt.title('tVAF of Each Synergy Solution')
    plt.savefig(filename, bbox_inches='tight')
    pp.savefig(fig)
    plt.close()
