#################################################################################
#                                                                               #
#   (C) 2010 Michael Bieri                                                      #
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


# scipt generate variables

import sys

Pi = 3.14159265


class Build_Variables():

    def __init__(self, main):

        self = main

        # Folders
        self.TEXT_FOLDER = 'Text_files'
        self.PLOT_FOLDER = 'Plots'
        self.PYMOL_FOLDER = 'Pymol_macros'

        # Function tolerance for fit
        self.tolerance = 1.49012e-20

        # Initial guess: [                                              Model 1, Model 2, Model 3, Model 4, Model 5, Model 6]
        self.INI_R2 = [15.1, 15.1, 15.1, 15.1, 15.1, 15.1]              # rad/s
        self.INI_kex = [0, 5012.3, 300.3, 2012.3, 110.3, 1000.2]        # rad/s
        self.INI_kex2 = [0, 0, 0, 3012.3, 110.3, 0]                     # rad/s
        self.INI_phi = [0, 0.07, 0, 0.07, 0, 0]                         # ppm**2
        self.INI_phi2 = [0, 0, 0, 0.05, 0, 0]                           # ppm**2
        self.INI_dw = [0, 0, 0.9, 0, 0.9, 0.9]                          # ppm
        self.INI_dw2 = [0, 0, 0, 0, 0.1, 0]                             # ppm
        self.INI_pb = [0, 0, 0.05, 0, 0.05, 0.05]
        self.INI_pc = [0, 0, 0, 0, 0.01, 0]

        # Constraints                                                   Models x [lower, upper] constraint
        self.CONS_R2 = [[5, 50], [5, 50], [5, 50], [5, 50], [5, 50], [5, 50]]
        self.CONS_kex = [[0, 0], [500, 10000], [10, 3000], [100, 20000], [100, 2000], [10, 15000]]
        self.CONS_kex2 = [[0, 0], [0, 0], [0, 0], [10, 20000], [10, 2000], [0, 0]]
        self.CONS_phi = [[0, 0], [0.00001, 10], [0, 0], [0.00001, 10], [0, 0], [0, 0]]
        self.CONS_phi2 = [[0, 0], [0, 0], [0, 0], [0.00001, 0.005], [0, 0], [0, 0]]
        self.CONS_dw = [[0, 0], [0, 0], [0.001, 10], [0, 0], [0.001, 10], [0.001, 10]]
        self.CONS_dw2 = [[0, 0], [0, 0], [0, 0], [0, 0], [0.001, 10], [0, 0]]
        self.CONS_pb = [[0, 0], [0, 0], [0.001, 0.3], [0, 0], [0.001, 0.3], [0.001, 0.2]]
        self.CONS_pc = [[0, 0], [0, 0], [0, 0], [0, 0], [0.001, 0.3], [0, 0]]

        # Save constraints to singleton
        Constraints_container.r2 = self.CONS_R2
        Constraints_container.kex = self.CONS_kex
        Constraints_container.kex2 = self.CONS_kex2
        Constraints_container.phi = self.CONS_phi
        Constraints_container.phi2 = self.CONS_phi2
        Constraints_container.dw = self.CONS_dw
        Constraints_container.dw2 = self.CONS_dw2
        Constraints_container.pb = self.CONS_pb
        Constraints_container.pc = self.CONS_pc

        # Gridsearch
        self.GRIDSEARCH = False
        self.GRID_INCREMENT = [0.5, 100, 0.05, 0.05, 0.00005]            # [r2, kex, dw, pb, phi]

        # Convergence
        self.CONVERGENCE = False

        # Gyromagnetic ration
        self.Y = {'0':-27.116, '1':67.262, '2':108.291}    # in MHz/T, order: 15N, 13C, 31P

        # data grid container
        self.data_grid = []
        self.data_grid_r1rho = []

        # Data grid sizer
        self.datagrid_sizer = []

        # summary label container
        self.label_summary = []

        # container for selected experiment (cpmg, R1p...)
        self.sel_experiment = []

        # container for reference data
        self.referencedata = []

        # container for number of datasets
        self.NUM_OF_DATASETS = []
        self.NUM_OF_DATASET = []

        # Container for bitmap under set up button
        self.bitmap_setup = []

        # Data grid
        self.RESNO = 700
        self.data = []

        # Framewidth
        self.FRAMEWIDTH = 2

        # Output format for plots
        self.PLOTFORMAT = '.svg'
        # dictionaries
        self.PLOT2SELECTION = {'.svg':0, '.ps':1, '.eps':2, '.pdf':3}
        self.SELECTION2PLOT = {'0':'.svg', '1':'.ps', '2':'.eps', '3':'.pdf'}

        # include residues
        self.INCLUDE_RES = []
        for i in range(0, int(self.RESNO)):
            self.INCLUDE_RES.append(True)

        # spectrometer frequencies
        self.spec_freq = []

        # Static magnetic field
        self.B0 = []

        # Hetero nucleus
        self.HETNUC = []

        # Spin lock label and values
        self.spinlock_offset_label = []
        self.spinlock_offset_label1 = []
        self.spinlock_offset_value = []

        # Variables for results tree file names
        self.results_txt = []
        self.results_plot = []
        self.results_model1 = []
        self.results_model2 = []
        self.results_model3 = []
        self.results_model4 = []
        self.results_model5 = []
        self.results_model6 = []
        self.results_model7 = []
        self.COLOR_PDB = []
        self.plot2d = []
        self.plot3d = []
        self.INTENSITIES_PLOTS = []

        # Results.
        self.MODEL1 = []            # [Residue, Fit_parameters, chi2]
        self.MODEL2 = []            # [Residue, Fit_parameters, chi2]
        self.MODEL3 = []            # [Residue, Fit_parameters, chi2]
        self.MODEL4 = []            # [Residue, Fit_parameters, chi2]
        self.MODEL5 = []            # [Residue, Fit_parameters, chi2]
        self.MODEL6 = []            # [Residue, Fit_parameters, chi2]
        self.MODEL = []             # [Model, datacontainer]
        self.MODEL_SELECTION = []   # [Residue, Model, R2, kex, Rex, pb, dw]
        self.MODEL_SELECTION_ERROR = [] # [Residue, R2, kex, Rex, pb, dw]
        self.COLLECTED_RESULTS = [] # sum of [MODEL_SELECTION, MODEL_SELECTION_ERROR, experiment index] over all datasets
        self.FINAL_RESULTS = []

        # Running evaluation flag
        self.RUNNING = False

        # Project folder
        self.PROJFOLDER = ''

        # Settings for peakfiles
        self.DATAFILEPROPERTY = ['0', '3', 'Space / Tab']

        # Sequence
        self.SEQUENCE = []

        # PDB file
        self.PDB = ''

        # Saved file
        self.SAVE_FILE = None

        # Project folder
        self.FOLDER = ''

        # Type of experiment
        self.EXPERIMENT = 'cpmg'

        # NESSY settings
        self.SETTINGS = ['AICc', '500', '30', '2.0', '50.0', '0', '40'] # [Model selection, Monte Carlo, Data sets, Difference to exclude, R2 limit, min Y axis in R2eff plots, max Y axis in R2eff plots]

        # Flag for models 1 - 5
        self.MODELS = [True, True, True, False, False, False, False]

        # create intensity plots
        self.CREATE_INTENSITYPLOT = 1

        # Create intensity plots
        self.CREATE_R2EFFPLOT = 1

        # Number of experiments
        self.NUMOFDATASETS = 1
        self.ISGLOBAL = True

        # Flag to decide if entire data set is fit to each model
        self.FITALLMODELS = False

        # Manual model selection
        self.MANUAL_SELECTION = False

        # CPMG dispersion
        self.CPMGFREQ = []
        self.CPMG_DELAY = []
        self.R2eff = []
        self.R2eff_variance = []
        self.R2eff_mean = []
        # create data containers
        for i in range(0, self.RESNO):
            self.data.append([])
            self.R2eff.append([])

        # shift difference
        self.SHIFT_DIFFERENCE = []
        for i in range(0, self.RESNO):
            self.SHIFT_DIFFERENCE.append(None)

        # HD exchange
        self.HD_TIME = []
        self.HD_NOISE = []
        # container for element
        self.hd_noise = []
        self.INITIAL_HD = ['error', '25992751.3', '0.05']

        # van't Hoff analysis
        self.vanthoff = {'dG':[], 'kab':[], 'K':[], 'T':[]}

        # Transition state
        self.transition = {'kab':[], 'T':[]}



class Constraints_container:
    """Container for constraints."""

    # Containers
    r2 = None
    kex = None
    kex2 = None
    phi = None
    phi2 = None
    dw = None
    dw2 = None
    pb = None
    pc = None
