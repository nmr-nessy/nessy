#################################################################################
#                                                                               #
#   (C) 2010 Michael Bieri                                                      #
#   (C) 2016 Edward d'Auvergne                                                  #
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


# script to manage projects

# Python modules
from os import sep
import sys

# NESSY modules
from conf.data import sync_data
from elements.variables import Build_Variables
from elements.collect_data import build_collect_data
from elements.start_analysis import build_start_analysis
from elements.results import build_results
from elements.notebook import build_notebook, pack_notebook
from elements.settings import build_settings
from elements.summary import build_summary
import elements



def stringtolist(string):
    #create list from string
    entrynum = 1
    string = string[1:(len(string)-1)]
    string = string.replace("'", "")
    string = string.replace("[", "")
    string = string.replace("]", "")
    returnlist = string.replace(' ', '').split(',')
    return(returnlist)


def refresh_project(self):
    # Delete Notebook
    self.MainTab.DeleteAllPages()

    # Shared variables.
    self.build_variables()

    # Settings tab
    build_settings(self)

    # Collect data tab
    build_collect_data(self, self.NUMOFDATASETS, self.isoffresonance)

    # Start analysis tab
    build_start_analysis(self)

    # Results tab
    build_results(self)

    # Summary tab
    build_summary(self)

    # settings tab
    self.proj_folder.SetValue('')
    self.pdb_file.SetValue('')


class open_project():
    """Open a NESSY porject file."""

    def __init__(self, main, filename):
        # link parameters
        self.main = main

        # create empty project
        refresh_project(self.main)

        #open file
        file = open(filename, 'r')

        # Leaded entries
        self.entries = []

        # Number of experiments
        self.num_exp = 1

        # read lines in save file
        for line in file:
            entry = str(line.strip().split('\n'))
            entry = str(entry[2: (len(entry)-2)])

            # Split entries
            entries_tmp = entry.split('<>')

            # Number of experiments is set
            if entries_tmp[0] == 'Number of experiments:':
                self.num_exp = int(entries_tmp[1])

            # save entry
            self.entries.append(entries_tmp)

        # close file
        file.close()

        # build experiments
        self.build_experiments()

        # fill in values
        self.fill_in_values()

        # add new file to opened recently
        #self.append_filename(filename)

        # Refresh menu
        #elements.menu.build_menubar(self.main)


    def append_filename(self, filename):
        filename = str(filename)
        filename = filename.replace('\n', '')

        # read filenames
        file = open(self.main.homefolder+sep+'projects.nessy', 'r')
        files = []
        for line in file:
            entry = line.replace('\n', '')
            files.append(entry)
        file.close()

        # remove new filename is it is in the list
        rem = 0

        # remove file if already in list
        if filename in files:
                rem = 1

        # store files
        counter = 10
        if len(files) < counter:
            counter = len(files)
        file = open(self.main.homefolder+sep+'projects.nessy', 'w')
        file.write(filename+'\n')
        for i in range(0, counter-rem):
            if files[i] == filename:
                file.write('')
            else:
                file.write(files[i]+'\n')
        file.close()


    def build_experiments(self):
        """Builds experiments tabs."""
        if self.num_exp > 1:
            for tab in range(1, self.num_exp):
                self.main.NUMOFDATASETS = tab + 1
                build_collect_data(self.main, self.main.NUMOFDATASETS)


    def fill_in_values(self):
        # loop over entries
        for entry in range(0, len(self.entries)):

            # experiment index
            try:
                exp_index = int(self.entries[entry][1])
            except:
                exp_index = 2

            # Settings
            if self.entries[entry][0] == 'Settings:':
                self.main.SETTINGS = stringtolist(self.entries[entry][1])

            # Models
            if self.entries[entry][0] == 'Models:':
                self.main.MODELS = stringtolist(self.entries[entry][1])
                # convert boolean to integer
                for i in range(0, len(self.main.MODELS)):
                    if self.main.MODELS[i]=='1':
                        self.main.MODELS[i]=True
                    else:
                        self.main.MODELS[i]=False

            # Global fit
            self.main.ISGLOBAL = True

            # shift difference
            if self.entries[entry][0] == 'Shift difference:':
                tmp = stringtolist(self.entries[entry][1])
                self.main.SHIFT_DIFFERENCE = []
                for i in range(len(tmp)):
                    if not tmp[i] == 'None':    self.main.SHIFT_DIFFERENCE.append(tmp[i])
                    else:                       self.main.SHIFT_DIFFERENCE.append(None)

            # Gridsearch
            if self.entries[entry][0] == 'Gridsearch:':
                self.main.GRIDSEARCH = True

            # Convergence
            if self.entries[entry][0] == 'Convergence:':
                self.main.CONVERGENCE = True

            # Calculate entire dataset
            if self.entries[entry][0] == 'Entire data:':
                self.main.FITALLMODELS = True

            # Fitting accuracy
            if self.entries[entry][0] == 'Fitting accuracy:':
                self.main.tolerance = float(self.entries[entry][1])

            # Project Folder
            if self.entries[entry][0] == 'Project folder:':
                self.main.proj_folder.SetValue(self.entries[entry][1])
                self.main.PROJFOLDER = self.entries[entry][1]

            # CPMG freq
            if self.entries[entry][0] == 'CPMG frequencies:':
                self.main.CPMGFREQ[exp_index] = stringtolist(self.entries[entry][2])

            # Write offet / spin lock power
            if self.entries[entry][0] == 'Spin Lock / Offset:':
                self.main.data_grid_r1rho[exp_index][2] = stringtolist(self.entries[entry][2])

            # HD exchange
            if self.entries[entry][0] == 'HD Exchange:':
                self.main.HD_TIME[exp_index] = stringtolist(self.entries[entry][2])

            # CPMG delay
            if self.entries[entry][0] == 'CPMG delay:':
                self.main.CPMG_DELAY = stringtolist(self.entries[entry][1])

            # HD noise
            if self.entries[entry][0] == 'HD noise:':
                self.main.HD_NOISE = stringtolist(self.entries[entry][1])

            # PDB File
            if self.entries[entry][0] == 'PDB file:':
                self.main.pdb_file.SetValue(self.entries[entry][1])
                self.main.PDB = self.entries[entry][1]

            # Sequence
            if self.entries[entry][0] == 'Sequence:':
                seq = stringtolist(self.entries[entry][2])
                for j in range(0, len(seq)):
                    # loop over experiments
                    self.main.data_grid[exp_index].SetCellValue(j, 0, seq[j])

            # Datasets
            if self.entries[entry][0] == 'Datasets:':
                dataset = int(self.entries[entry][2])
                data_entry = stringtolist(self.entries[entry][3])
                for i in range(0, len(data_entry)):
                    self.main.data_grid[exp_index].SetCellValue(i, dataset, data_entry[i])

            # Spin lock data sets
            if self.entries[entry][0] == 'Datasets Spinlock:':
                dataset = int(self.entries[entry][2])
                spinlock = int(self.entries[entry][3])
                data_entry = stringtolist(self.entries[entry][4])
                for i in range(0, len(data_entry)):
                    self.main.data_grid_r1rho[exp_index][1][dataset-1].SetCellValue(i, spinlock, data_entry[i])

            # self.entries[entry] in results tree
            if self.entries[entry][0] == 'Results:':
                plots = stringtolist(self.entries[entry][2])
                if self.entries[entry][1] == 'Plot':
                    for i in range(0, len(plots)):
                        self.main.tree_results.AppendItem (self.main.plots_plots, plots[i], 0)
                if self.entries[entry][1] == 'Model1':
                    self.main.results_model1 = plots
                    for i in range(0, len(plots)):
                        self.main.tree_results.AppendItem (self.main.plots_model1, plots[i], 0)
                if self.entries[entry][1] == 'Model2':
                    self.main.results_model2 = plots
                    for i in range(0, len(plots)):
                        self.main.tree_results.AppendItem (self.main.plots_model2, plots[i], 0)
                if self.entries[entry][1] == 'Model3':
                    self.main.results_model3 = plots
                    for i in range(0, len(plots)):
                        self.main.tree_results.AppendItem (self.main.plots_model3, plots[i], 0)
                if self.entries[entry][1] == 'Model4':
                    self.main.results_model4 = plots
                    for i in range(0, len(plots)):
                        self.main.tree_results.AppendItem (self.main.plots_model4, plots[i], 0)
                if self.entries[entry][1] == 'Model5':
                    self.main.results_model5 = plots
                    for i in range(0, len(plots)):
                        self.main.tree_results.AppendItem (self.main.plots_model5, plots[i], 0)
                if self.entries[entry][1] == 'Model6':
                    self.main.results_model6 = plots
                    for i in range(0, len(plots)):
                        self.main.tree_results.AppendItem (self.main.plots_model6, plots[i], 0)

                # Final Results
                if self.entries[entry][1] == 'Final':
                    self.main.FINAL_RESULTS = stringtolist(self.entries[entry][2])
                    for i in range(0, len(self.main.FINAL_RESULTS)):
                        self.main.tree_results.AppendItem (self.main.plots_modelselection, self.main.FINAL_RESULTS[i], 0)

                # Color coded pymol macros.
                if self.entries[entry][1] == 'ColorCode':
                    self.main.COLOR_PDB = stringtolist(self.entries[entry][2])
                    for i in range(0, len(self.main.COLOR_PDB)):
                        self.main.tree_results.AppendItem (self.main.structures, self.main.COLOR_PDB[i], 0)

                # Text Files.
                if self.entries[entry][1] == 'Textfiles:':
                    self.main.results_txt = stringtolist(self.entries[entry][2])
                    for i in range(0, len(self.main.results_txt)):
                        self.main.tree_results.AppendItem (self.main.txt, self.main.results_txt[i], 0)

                # 2d plots.
                if self.entries[entry][1] == '2D Plots:':
                    self.main.plot2d = stringtolist(self.entries[entry][2])
                    for i in range(0, len(self.main.plot2d)):
                        self.main.tree_results.AppendItem (self.main.plots2d, self.main.plot2d[i], 0)

                # 3d plots.
                if self.entries[entry][1] == '3D Plots:':
                    self.main.plot3d = stringtolist(self.entries[entry][2])
                    for i in range(0, len(self.main.plot3d)):
                        self.main.tree_results.AppendItem (self.main.plots3d, self.main.plot3d[i], 0)

                # Intensities.
                if self.entries[entry][1] == 'Intensities:':
                    self.main.INTENSITIES_PLOTS = stringtolist(self.entries[entry][2])
                    for i in range(0, len(self.main.INTENSITIES_PLOTS)):
                        self.main.tree_results.AppendItem (self.main.plots_intensities, self.main.INTENSITIES_PLOTS[i], 0)

            # Spectrometer frequencies
            if self.entries[entry][0] == 'Spec freq:':
                tmp = stringtolist(self.entries[entry][1])

                for e in range(0, len(tmp)):
                    self.main.spec_freq[e].SetValue(tmp[e])

            # B0
            if self.entries[entry][0] == 'B0:':
                tmp = stringtolist(self.entries[entry][1])
                for e in range(0, len(tmp)):
                    self.main.B0[e].SetValue(tmp[e])

            # Hetero nucleus
            #if self.entries[entry][0] == 'Hetnuc:':
            #    tmp = stringtolist(self.entries[entry][1])
            #    for e in range(0, len(tmp)):
            #        self.main.HETNUC[e].SetSelection(int(tmp[e]))



def save_project(self, filename):


    file = open(filename, 'w')
    file.write('NESSY save file<><>')

    # Settings
    file.write('\nSettings:<>'+ str(self.SETTINGS))

    # Gridsearch
    if self.GRIDSEARCH:
        file.write('\nGridsearch:<>')

    # convergence
    if self.CONVERGENCE:
        file.write('\nConvergence:<>')

    # analyse entire dataset
    if self.FITALLMODELS:
        file.write('\nEntire data:<>')

    # Models
    # convert boolean to integer
    for i in range(0, len(self.MODELS)):
        if self.MODELS[i]:
            self.MODELS[i]=1
        else:
            self.MODELS[i]=0
    file.write('\nModels:<>'+ str(self.MODELS))

    # fitting accuracy
    file.write('\nFitting accuracy:<>' + str(self.tolerance))

    # write project folder
    file.write('\nProject folder:<>' + str(self.proj_folder.GetValue()))

    # write CPMG Time
    file.write('\nCPMG delay:<>' + str(self.CPMG_DELAY))

    # write HD noise
    file.write('\nHD noise:<>' + str(self.HD_NOISE))

    # Shift difference
    file.write('\nShift difference:<>' + str(self.SHIFT_DIFFERENCE))

    # write spectrometer ferquencies
    tmp = []
    for fr in range(0, len(self.spec_freq)):
        tmp.append(str(self.spec_freq[fr].GetValue()))
    file.write('\nSpec freq:<>' + str(tmp))

    # B0
    tmp = []
    for fr in range(0, len(self.B0)):
        tmp.append(str(self.B0[fr].GetValue()))
    file.write('\nB0:<>' + str(tmp))

    # Hetero nucleus
    #tmp = []
    #for fr in range(0, len(self.HETNUC)):
    #    tmp.append(str(self.HETNUC[fr].GetSelection()))
    #file.write('\nHetnuc:<>' + str(tmp))

    # write pdb file
    file.write('\nPDB file:<>' + str(self.pdb_file.GetValue()))

    # write number of experiments
    file.write('\nNumber of experiments:<>' + str(self.NUMOFDATASETS))

    # entries in results tree
    file.write('\nResults:<>Plot<>' + str(self.results_plot))
    file.write('\nResults:<>Model1<>' + str(self.results_model1))
    file.write('\nResults:<>Model2<>' + str(self.results_model2))
    file.write('\nResults:<>Model3<>' + str(self.results_model3))
    file.write('\nResults:<>Model4<>' + str(self.results_model4))
    file.write('\nResults:<>Model5<>' + str(self.results_model5))
    file.write('\nResults:<>Model6<>' + str(self.results_model6))
    file.write('\nResults:<>Final<>' + str(self.FINAL_RESULTS))
    file.write('\nResults:<>ColorCode<>' + str(self.COLOR_PDB))
    file.write('\nResults:<>Textfiles:<>' + str(self.results_txt))
    file.write('\nResults:<>2D Plots:<>' + str(self.plot2d))
    file.write('\nResults:<>3D Plots:<>' + str(self.plot3d))
    file.write('\nResults:<>Intensities:<>' + str(self.INTENSITIES_PLOTS))

    # Results
    file.write('\nFinal Results:<>'+str(self.FINAL_RESULTS))

    # loop over experiments
    for exp in range(0, self.NUMOFDATASETS):
        # experiment index
        num_exp = str(exp) + '<>'

        # write sequence
        seq = []
        file.write('\nSequence:<>'+num_exp)
        for i in range(0, self.RESNO):
            seq.append(str(self.data_grid[exp].GetCellValue(i, 0)))
        file.write(str(seq))

        # write data sets of CPMG relaxation dispersion or H/D exchange
        for i in range(0, int(self.SETTINGS[2])):   # loop over dataset
            # collect data
            data = []
            for residue in range(0, self.RESNO):
                data.append(str(self.data_grid[exp].GetCellValue(residue, i+1)))

            file.write('\nDatasets:<>'+num_exp+str(i+1)+'<>'+str(data))

        # Write data sets for Spin Lock experiments
        for spintab in range(0, int(self.SETTINGS[2])):   # loop over offsets / spin lock power
            for grid in range(0, int(self.SETTINGS[2])):   # loop over data sets
                data = []
                for residue in range(0, self.RESNO):
                    data.append(str(self.data_grid_r1rho[exp][1][spintab].GetCellValue(residue, grid+1)))

                file.write('\nDatasets Spinlock:<>'+num_exp+str(spintab+1)+'<>'+str(grid+1)+'<>'+str(data))

        # CPMG relaxation delay
        file.write('\nCPMG relaxation delay:<>'+num_exp + self.CPMG_DELAY[exp])

        # HD Exchange
        file.write('\nHD Exchange:<>'+num_exp + str(self.HD_TIME[exp]))

        # type of experiment
        if self.sel_experiment[exp].GetSelection() == 0:
            exper = 'cpmg'
        if self.sel_experiment[exp].GetSelection() == 1:
            exper = 'on'
        if self.sel_experiment[exp].GetSelection() == 2:
            exper = 'off'
        if self.sel_experiment[exp].GetSelection() == 3:
            exper = 'HD'
        file.write('\nExperiment:<>'+num_exp + exper)

        # write CPMG Frequencies
        file.write('\nCPMG frequencies:<>'+num_exp  + str(self.CPMGFREQ[exp]))

        # Write offet / spin lock power
        file.write('\nSpin Lock / Offset:<>'+num_exp + str(self.data_grid_r1rho[exp][2]))

    #close file
    file.close()

    # read filenames
    #file = open(self.homefolder+sep+'projects.nessy', 'r')
    #files = []
    #for line in file:
    #   files.append(line)
    #file.close()

    # remove new filename is it is in the list
    #rem = 0
    #try:
    #    files = files.remove(filename)
    #except:
    #    # remove last entry
    #    if len(files) > 10:
     #       rem = 1

    ## store files
    #file = open(self.homefolder+sep+'projects.nessy', 'w')
    #file.write(filename+'\n')
    #for i in range(0, len(files)-rem):
    #    file.write(files[i]+'\n')
    #file.close()

    # Refresh menu
    #elements.menu.build_menubar(self)
