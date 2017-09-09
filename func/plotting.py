#################################################################################
#                                                                               #
#   (C) 2010 Michael Bieri                                                      #
#   (C) 2013 Edward d'Auvergne                                                  #
#                                                                               #
#   This file is part of NESSY.                                                 #
#                                                                               #
#   NESSY is free software: you can redistribute it and/or modify               #
#   it under the terms of the GNU General Public License as published by        #
#   the Free Software Foundation, either version 3 of the License, or           #
#   (at your option) any later version.                                         #
#                                                                               #
#   NESSY is distributed in the hope that it will be useful,                    #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of              #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
#   GNU General Public License for more details.                                #
#                                                                               #
#   You should have received a copy of the GNU General Public License           #
#   along with NESSY; if not, write to the Free Software                        #
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                               #
#################################################################################


# Python modules
from os import sep, mkdir, makedirs
import pylab
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from scipy import sqrt
import time
import wx

# NESSY modules
from curvefit.chi2 import Chi2_container



def create_pylab_graphs(self, r2eff, include, residue, exp_index, exp_mode=0):
    """Function that creates pylab plots (png and svg) and csv text files"""

    # prefix of files
    prefix = 'Exp_'+str(exp_index+1)+'_'

    # detect maximum frequency
    max = 0
    for i in range(0, len(self.CPMGFREQ[exp_index])):
        try:
            if int(self.CPMGFREQ[exp_index][i]) > max:
                max = int(self.CPMGFREQ[exp_index][i])

        # empty data sets
        except:
            break

    # add extra border in graph
    max = max + (0.1*max)

    # Create folders
    pylabfolder = str(self.proj_folder.GetValue()) + sep + 'R2eff_plots'

    try:
        mkdir(pylabfolder)
    except:
        wx.CallAfter(self.report_panel.AppendText, '\nPylab folder already exists.\n')

    # png folder for pylab plots
    try:
        mkdir(pylabfolder+sep+'png')
    except:
        wx.CallAfter(self.report_panel.AppendText, '\nPNG folder already exists.\n')

    # svg folder for pylab plots
    try:
        mkdir(pylabfolder+sep+self.PLOTFORMAT.replace('.', ''))
    except:
        wx.CallAfter(self.report_panel.AppendText, '\nsvg folder already exists.\n')


    # create text file folder
    textfolder = str(self.proj_folder.GetValue()) + sep + 'R2eff_txt'

    try:
        mkdir(textfolder)
    except:
        wx.CallAfter(self.report_panel.AppendText, '\nText file folder already exists.\n\n')


    # current residue no
    status = 1

    for i in range(0, self.RESNO):  # loop over residues
        x = []
        y = []

        # calculate only marked residues
        if i in include:
            for j in range(0, self.NUM_OF_DATASET[exp_index]):      # loop over dataset
                if not r2eff[i][j] == None:
                    x.append(float(self.CPMGFREQ[exp_index][j]))
                    y.append(float(r2eff[i][j]))

            # Update progress bar
            progress = int(status * 100 / residue)
            wx.CallAfter(self.gauge_1.SetValue, min(100, progress))
            status = status + 1
            time.sleep(0.001)

            # save pylab plot
            if exp_mode == 0:
                pylab.xlabel('v(CPMG) [Hz]', fontsize=19, weight='bold')
                pylab.ylabel('R2eff [1/s]', fontsize=19, weight='bold')
            elif exp_mode == 1:
                pylab.xlabel('v1 [Hz]', fontsize=19, weight='bold')
                pylab.ylabel('R1rho [1/s]', fontsize=19, weight='bold')
            pylab.xticks(fontsize=19)
            pylab.yticks(fontsize=19)
            pylab.errorbar(x, y, yerr = sqrt(self.R2eff_variance[exp_index][i]), fmt ='ko')
            pylab.xlim((0, max))
            # y axis limits
            y_min = float(self.SETTINGS[5])
            y_max = float(self.SETTINGS[6])

            pylab.ylim(y_min, y_max)

            # Frame width
            params={'axes.linewidth' : self.FRAMEWIDTH}
            pylab.rcParams.update(params)

            # create svg plot
            pylab.savefig(pylabfolder + sep +self.PLOTFORMAT.replace('.', '') + sep +prefix+ str(i+1) + '_' + str(self.data_grid[exp_index].GetCellValue(i, 0)) +self.PLOTFORMAT)

            #create png plot
            pylab.figtext(0.13, 0.85, str(i+1)+' '+str(self.data_grid[exp_index].GetCellValue(i, 0)), fontsize=19)
            pylab.savefig(pylabfolder + sep +'png' + sep +prefix+ str(i+1) + '_' + str(self.data_grid[exp_index].GetCellValue(i, 0)) +'_plot.png', dpi = 72, transparent = True)
            pylab.cla() # clear the axes
            pylab.close() #clear figure
            wx.CallAfter(self.report_panel.AppendText, 'R2eff NESSY Plot for Residue ' + str(i+1) + ' created\n' )

            # Add Results to results tree
            # plots
            entry = pylabfolder + sep +'png' + sep +prefix+ str(i+1) + '_' + str(self.data_grid[exp_index].GetCellValue(i, 0)) +'_plot.png'
            self.results_plot.append(entry)

            # save text file
            file = open(textfolder+sep+prefix+str(i+1) + '_' + str(self.data_grid[exp_index].GetCellValue(i, 0)) + '_R2eff.csv', 'w')
            file.write('CPMG [Hz];R2eff [1/s];error\n\n')
            for k in range(len(y)):
                file.write(str(x[k]) + ';' + str(y[k]) + ';' + str(sqrt(self.R2eff_variance[exp_index][i]))+'\n')
            file.close()
            wx.CallAfter(self.report_panel.AppendText, 'CSV file for Residue ' + str(i+1) + ' created\n' )

            # Add Results to results tree
            # .txt files
            entry = textfolder+sep+prefix+str(i+1) + '_' + str(self.data_grid[exp_index].GetCellValue(i, 0)) + '_R2eff.csv'
            self.results_txt.append(entry)

            # clear graph
            pylab.cla()
            pylab.close()

    # add plot files to results tree
    for n in range(len(self.results_plot)):
        self.tree_results.AppendItem (self.plots_plots, self.results_plot[n], 0)

    # add txt files to results tree
    for i in range(len(self.results_txt)):
        self.tree_results.AppendItem (self.txt, self.results_txt[i], 0)


class Plot_intensities():
    """Create intensities plots."""
    def __init__(self, main, index):
        # prefix
        prefix = 'Exp_'+str(index+1)+'_'

        # link parameters
        self.main = main

        # Feedback
        wx.CallAfter(self.main.checkrun_label.SetLabel, 'Creating Intensity plots...')
        wx.CallAfter(self.main.report_panel.AppendText, '\nCreating Intensity plots:\n\n' )
        wx.CallAfter(self.main.gauge_1.SetValue, 0)

        # Detect number of residues
        max_calc = 0
        current_calc = 1
        for i in range(0, self.main.RESNO):
            if not self.main.data_grid[index].GetCellValue(i, self.main.referencedata[index]) == '':
                max_calc = max_calc + 1

        # create directory
        folder = self.main.PROJFOLDER + sep + 'Intensities_plots'
        try:
            os.mkdir(folder)
        except:
            wx.CallAfter(self.main.report_panel.AppendText, '')

        # Detect reference data set
        for i in range(0, int(self.main.SETTINGS[2])):
            if float(self.main.CPMGFREQ[index][i]) == 0.0:
                reference = i+1

        # loop over residues
        for residue in range(0, self.main.RESNO):
            # abort if residue was disabled
            if not self.main.INCLUDE_RES[residue]:
                continue

            # skip if there is no value
            if self.main.data_grid[index].GetCellValue(residue, reference) == '':
                continue

            # Data containers
            x_values = []
            y_values = []

            # loop over datasets
            for dataset in range (0, int(self.main.SETTINGS[2])):
                if not '' in [self.main.data_grid[index].GetCellValue(residue, dataset+1), self.main.CPMGFREQ[index][dataset]]:
                    x_values.append(float(self.main.CPMGFREQ[index][dataset]))
                    y_values.append(float(self.main.data_grid[index].GetCellValue(residue, dataset+1)))

            # Normalize y values
            y_values = [i/float(str(self.main.data_grid[index].GetCellValue(residue, reference))) for i in y_values]

            # Create plot
            pylab.plot(x_values, y_values, 'ko')
            pylab.figtext(0.13, 0.85, str(residue+1)+' '+str(self.main.data_grid[index].GetCellValue(residue, 0)), fontsize=19)
            pylab.xlabel('v(CPMG) [Hz]', fontsize=19, weight='bold')
            pylab.ylabel('Relative Intensity', fontsize=19, weight='bold')
            pylab.xticks(fontsize=19)
            pylab.yticks(fontsize=19)
            pylab.ylim(0, 1.1)

            # Frame width
            params={'axes.linewidth' : self.main.FRAMEWIDTH}
            pylab.rcParams.update(params)

            # save files
            pylab.savefig(folder+sep+prefix+str(residue+1)+'_'+str(self.main.data_grid[index].GetCellValue(residue, 0))+'.png', dpi = 72, transparent = True)
            pylab.savefig(folder+sep+prefix+str(residue+1)+'_'+str(self.main.data_grid[index].GetCellValue(residue, 0))+self.main.PLOTFORMAT)

            # store item
            self.main.INTENSITIES_PLOTS.append(folder+sep+prefix+str(residue+1)+'_'+str(self.main.data_grid[index].GetCellValue(residue, 0))+'.png')
            self.main.tree_results.AppendItem (self.main.plots_intensities, folder+sep+prefix+str(residue+1)+'_'+str(self.main.data_grid[index].GetCellValue(residue, 0))+'.png', 0)

            # clear graph
            pylab.cla()
            pylab.close()

            # report
            wx.CallAfter(self.main.report_panel.AppendText, 'Intensity plot for residue '+str(self.main.data_grid[index].GetCellValue(residue, 0))+' '+str(residue+1)+' created\n')
            progress = int(100 * current_calc / max_calc)
            wx.CallAfter(self.main.gauge_1.SetValue, min(100, progress))
            current_calc = current_calc + 1
            time.sleep(0.001)


def surface_plot(base_dir='', fileroot='', model=2, output='', output1='', savecont='',  vec='.svg'):
        """Function to create a chi2 trace as 3D plot."""

        # Create folders
        # png
        pngdir = base_dir+sep+'chi2_surface'+sep+'png'
        try:
            makedirs(pngdir)
        except:
            a = 0

        # vector
        vecdir = base_dir+sep+'chi2_surface'+sep+vec
        try:
            makedirs(vecdir)
        except:
            a = 0

        # Create 3d axes
        fig = plt.figure()
        ax = Axes3D(fig)

        # plot
        ax.plot(Chi2_container.chi2_surface[0], Chi2_container.chi2_surface[1], Chi2_container.chi2_surface[2])
        ax.set_xlabel('kex [1/s]', fontsize=19, weight='bold')
        if model in [2, 4]:  ax.set_ylabel('Phi', fontsize=19, weight='bold')
        else:               ax.set_ylabel('pb', fontsize=19, weight='bold')
        ax.set_zlabel('Chi2', fontsize=19, weight='bold')

        # Create png
        pylab.savefig(pngdir+sep+fileroot+'.png', dpi = 72, transparent = True)

        # Create vector plot
        pylab.savefig(vecdir+sep+fileroot+'.'+vec)

        # Crear plot
        pylab.cla()     # clear the axes
        pylab.close()   #clear figure

        # clear chi2_surface container
        Chi2_container.chi2_surface = [[], [], []]

        # Store 3D plots
        output.AppendItem (output1, pngdir+sep+fileroot+'.png', 0)

        # Store 3d plots
        savecont.append(pngdir+sep+fileroot+'.png')
