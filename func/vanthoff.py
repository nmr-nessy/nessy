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


# Python modules
from os import sep, makedirs
import pylab
from random import random, uniform
from scipy import log, array, linspace, var, sqrt, mean, exp
from scipy.optimize import leastsq
try:
    import thread as _thread
except ImportError:
    import _thread
from time import sleep
import wx
import wx.grid
import wx.lib.agw.pyprogress as PP

# NESSY modules
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC
from math_fns.vanthoff import Eyring_fit, Eyring, lin_fit, lin_model, log_fit, log_model
from math_fns.tests import AICc
from conf.message import error_popup, message
from conf.filedialog import opendir, openfile, savefile
from conf.NESSY_grid import NESSY_grid




def vanthoff_list(inputs, output=True):
    '''Function to read van't Hoff parameters of list.'''
    # find filename
    filename = str(inputs[len(inputs)-1])

    # containers
    dG = []
    K = []
    T = []
    kab = []
    T_index = 0
    K_index = 0
    dG_index = 0
    kab_index = 0

    # open file
    file = open(filename, 'r')

    # read lines
    header_flag = True
    for line in file:
        printtxt = ''

        # split entries
        line = line.replace('\n', '')
        if '\t' in line:
            entries = line.split('\t')      # tab separated
        elif ';' in line:
            entries = line.split(';')      # semicolon separated
        else:
            entries = line.split()          # space separated

        # skip if not enough entries
        if len(entries) < 2:
            continue

        # collect values
        if not header_flag:
            # T
            T.append(entries[T_index])
            printtxt = printtxt + 'T: '+entries[T_index]

            # dG
            if not dG_index == 14:
                dG.append(entries[dG_index])
                printtxt = printtxt + ', dG: '+entries[dG_index]

            # K
            if not K_index == 14:
                K.append(entries[K_index])
                printtxt = printtxt + ', K: '+entries[K_index]

            # kab
            if not kab_index == 14:
                kab.append(entries[kab_index])
                printtxt = printtxt + ', kab: '+entries[kab_index]


        # read index of dG, K and T
        if 'T' in entries:
            header_flag = False

            # index of T
            while not entries[T_index] == 'T': T_index += 1

            # index of K
            if 'K' in entries:
                while not entries[K_index] == 'K': K_index += 1
            else:
                K_index = 14

            # index of kab
            if 'kab' in entries:
                while not entries[kab_index] == 'kab': kab_index += 1
            else:
                kab_index = 14

            # index of dG
            if 'dG' in entries:
                while not entries[dG_index] == 'dG': dG_index += 1
            else:
                dG_index = 14

        # give feedback
        if output:
            print(printtxt)

    # close file
    file.close()

    # return van't Hoff list
    return {'dG':dG, 'kab':kab, 'K':K, 'T':T}



class Transition_state(wx.Frame):
    def __init__(self, main, theory, *args, **kwds):
        # connect to mainframe
        self.main = main.main

        # connect to vanthoff
        self.vanthoff = main

        # Theory
        self.theory = theory

        # number of data
        self.lendata = self.vanthoff.lendata

        # Read calculated dS, dH and dC
        # linear model
        if self.vanthoff.linear_fit:
            self.dS_linear = self.vanthoff.linear_fit['dS']
            self.dH_linear = self.vanthoff.linear_fit['dH']
            self.dS_error = self.vanthoff.mc_errors[0]
            self.dH_error = self.vanthoff.mc_errors[1]
        else:
            self.dS_linear = None
            self.dH_linear = None

        # logarithmic model
        if self.vanthoff.logarithmic_fit:
            self.dS_logarithmic = self.vanthoff.logarithmic_fit['dS']
            self.dH_logarithmic = self.vanthoff.logarithmic_fit['dH']
            self.dC_logarithmic = self.vanthoff.logarithmic_fit['dC']
        else:
            self.dS_logarithmic = None
            self.dH_logarithmic = None
            self.dC_logarithmic = None

        # Build frame
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.Centre()

        # Background color
        self.SetBackgroundColour(wx.NullColour)

        # build GUI
        self.build()

        # Sync to van'T Hoff grid
        self.sync()


    def build(self):
        # main sizer
        mainsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Subsizer
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Image
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        mainsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # right sizer
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # title
        self.title = wx.StaticText(self, -1, "Calculation of Activation Barriers using\nTansition-State Theory by the "+self.theory+" Equation")
        self.title.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        right_sizer.Add(self.title, 0, wx.ALL|wx.ALIGN_LEFT, 10)

        # Text
        self.text1 = wx.StaticText(self, -1, "Enter experimental data below.\n\nEnter k(AB) (k(AB) / k(BA) = pb / pa; k(AB) = kex * pb) \nand the corresponding temperature in Kelvin.\n")
        right_sizer.Add(self.text1, 0, wx.ALL, 5)

        # The grid
        self.main.transition_grid = NESSY_grid(self, -1, size=(1, 1))
        self.main.transition_grid.CreateGrid(self.lendata, 3)
        self.main.transition_grid.SetMinSize((470, 150))
        self.main.transition_grid.SetColLabelValue(0, 'k(AB)')
        self.main.transition_grid.SetColSize(0, 120)
        self.main.transition_grid.SetColLabelValue(1, 'T [K]')
        self.main.transition_grid.SetColSize(1, 120)
        self.main.transition_grid.SetColLabelValue(2, 'dG [J/(mol*K)]')
        self.main.transition_grid.SetColSize(2, 120)
        right_sizer.Add(self.main.transition_grid, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Directory
        directory_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text3 = wx.StaticText(self, -1, 'Output directory:')
        self.text3.SetMinSize((120, 23))
        directory_sizer.Add(self.text3, 0, wx.LEFT|wx.RIGHT, 5)
        self.directory = wx.TextCtrl(self, -1, str(self.vanthoff.directory.GetValue()))
        self.directory.SetMinSize((250, 23))
        directory_sizer.Add(self.directory, 0, wx.LEFT, 5)

        self.button_dir = wx.Button(self, -1, "+")
        self.button_dir.SetMinSize((25, 23))
        self.Bind(wx.EVT_BUTTON, self.sel_dir, self.button_dir)
        directory_sizer.Add(self.button_dir, 0, wx.RIGHT, 5)
        right_sizer.Add(directory_sizer, 0, wx.TOP, 15)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_ok = wx.Button(self, -1, "Calculate")
        self.button_clear = wx.Button(self, -1, "Clear")
        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.calculate, self.button_ok)
        #self.Bind(wx.EVT_BUTTON, self.clear, self.button_clear)
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        sizer_buttons.Add(self.button_ok, 0, wx.ALL, 10)
        sizer_buttons.Add(self.button_clear, 0, wx.ALL, 10)
        sizer_buttons.Add(self.button_close, 0, wx.ALL, 10)
        right_sizer.Add(sizer_buttons, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Text
        if self.dS_linear:
            self.text2 = wx.StaticText(self, -1, "Calculated dS = "+str(self.dS_linear/1000)[0:10]+" kJ/(mol*K), dH = "+str(self.dH_linear/1000)[0:10]+" kJ/mol")
            right_sizer.Add(self.text2, 0, wx.ALL, 5)

        # Pack dialog
        mainsizer.Add(right_sizer, 0, 0, 0)
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()
        self.Center()


    def calc_exec(self):
        # start calculation in thread
        try:
            _thread.start_new_thread(self.calc_thread, ())
        except:
            print("Can't start calculation!")
            return


    def calc_running(self, event):
        '''Displays a cycling progress bar.'''
        # Build the progress dialog
        dlg = PP.PyProgress(self, -1, "NESSY", "Performing van't Hoff analysis.")

        #security counter
        canceled = 0

        # display
        while self.keepGoing or canceled > 1000:
            # wait 30 ms
            wx.MilliSleep(30)

            # increase cancel
            canceled += 1

            # update bar
            keepGoing = dlg.UpdatePulse()

        # Close dialog
        dlg.Destroy()

        # Feedback
        message(self.message, self)


    def calc_thread(self):
        # collect variables
        T = []
        kab = []
        dG = []
        for i in range(self.lendata):
            # only append data is data is present
            if not str(self.main.transition_grid.GetCellValue(i, 1)) == '':
                # T
                try:
                    T.append(float(self.main.transition_grid.GetCellValue(i, 1)))
                # entry is not a number
                except:
                    continue

                # Kab
                if not str(self.main.transition_grid.GetCellValue(i, 0)) == '':
                    # only append if entries are numbers
                    try:
                        kab.append(float(self.main.transition_grid.GetCellValue(i, 0)))
                    except:
                        kab.append(0)

                # dG
                if not str(self.main.transition_grid.GetCellValue(i, 2)) == '':
                    # only append if entries are numbers
                    try:
                        dG.append(float(self.main.transition_grid.GetCellValue(i, 2)))
                    except:
                        dG.append(0)

        # abort if not enough data is present
        if len(T) < 2:
            print('Not enough data present!\n\nAborting Transition state activation barrier calculation.')
            self.keepGoing = False
            return

        # error of kab
        data = self.calc_error(T, kab)

        # Fit fro dS* and dH*
        fit = self.fit(self.theory, data)

        # directory for plots
        directory = str(self.directory.GetValue())

        # Temperature to create plot
        temperature = 300

        # craete fre energy plot
        if len(dG) > 2:
            # collect dG and T
            kab_dG = []
            T_dG = []
            dG_dG = []
            for i in range(self.lendata):
                if not str(self.main.transition_grid.GetCellValue(i, 0)) == '' and not str(self.main.transition_grid.GetCellValue(i, 1)) == '' and not str(self.main.transition_grid.GetCellValue(i, 2)) == '':
                    # collect kab
                    kab_dG.append(float(self.main.transition_grid.GetCellValue(i, 0)))

                    # collect T
                    T_dG.append(float(self.main.transition_grid.GetCellValue(i, 1)))

                    # dG
                    dG_dG.append(float(self.main.transition_grid.GetCellValue(i, 2)))

            # calculate
            data = self.calc_dG_landscape(T_dG, dG_dG, kab_dG)

            # plot
            self.plot(ground=(data[0])/1000, ground_error=(data[3])/1000, barrier=data[1]/1000, barrier_error=data[4]/1000, label='dG at '+str(int(data[2]))+' K [kJ/mol]', directory=directory)

            # sync temperature
            temperature = int(data[2])

        # create plot Entropy plot
        if self.dS_linear:
            self.plot(ground=self.dS_linear/1000, ground_error= self.dS_error/1000, barrier=fit[1]/1000, barrier_error=fit[3]/1000, label='dS at '+str(temperature)+' K [kJ/mol]', temperature=temperature, directory=directory)

        # create plot Entalpy plot
        if self.dH_linear:
            self.plot(ground=self.dH_linear/1000, ground_error= self.dH_error/1000, barrier=fit[0]/1000, barrier_error=fit[2]/1000, label='dH [kJ/mol]', directory=directory)

        # feedback
        self.message = 'Calculation finished.\n\ndH* = '+str(fit[0]/1000)+' +/- '+str(fit[2]/1000)+' kJ/mol\ndS* = '+str(fit[1]/1000)+' +/- '+str(fit[3]/1000)+' kJ/(mol*K)'
        if len(dG) > 2:
            self.message = self.message + '\ndG* = '+str(data[1]/1000)+' +/- '+str(data[4]/1000)+' kJ/mol'
        self.message = self.message + '\n\nPlots are summarized in 2D plots in results tree.'
        self.keepGoing = False


    def calc_dG_landscape(self, T_dG, dG_dG, kab_dG):
        # Constants
        R = 8.31447215
        kb = 1.3806504 * 10**(-23)
        h = 6.62606896 * 10**(-34)

        # detect highest temperature
        max = 0
        for i in range(len(T_dG)):
            if T_dG[i] > max:
                max = T_dG[i]

        # pool dG and kab of highest temperature
        data = []
        data_kab = []
        for i in range(len(T_dG)):
            if T_dG[i] == max:
                data.append(dG_dG[i])
                data_kab.append(kab_dG[i])

        # calculate mean of dG
        ground_dG = mean(data)

        # calculate error of dG
        ground_dG_error = sqrt(var(data, ddof = 1))

        # Calculate activation barrier
        barrier_dG = (-1)*R*max*log((mean(data_kab)*h)/(kb*max))

        # calculate error
        kab_error = sqrt(var(data_kab, ddof = 1))

        # mean of kab
        kab_mean = mean(data_kab)

        # Monte Carlo simulations for error
        barrier_dG_sim = []
        for mc in range(1000):
            barrier_dG_sim.append((-1)*R*max*log(((kab_mean+uniform(-kab_error, kab_error))*h)/(kb*max)))

        # remove imaginary numbers
        dg_mcs = []
        for i in range(len(barrier_dG_sim)):
            if not 'j' in str(barrier_dG_sim[i]):
                dg_mcs.append(barrier_dG_sim[i])

        # calculate error of dG*
        barrier_dG_error = sqrt(var(dg_mcs, ddof = 1))

        # Return
        return [ground_dG, barrier_dG, max, ground_dG_error, barrier_dG_error]


    def calc_error(self, T, kab):
        # Craete datapoints and errors

        # Entries to exclude
        exclude = []

        # Container fro temporary data
        reps = []

        # kab and error container
        kab_mean = []
        kab_error = []
        kab_T = []
        error_container = []
        T_container = []

        # loop over T
        for i in range(len(T)):
            # add Temperature
            if not T[i] in T_container:
                # add T
                T_container.append(T[i])

                # create value container
                error_container.append([])

            # get the index
            index = T_container.index(T[i])

            # Store value
            error_container[index].append(kab[i])

        # mean
        for i in range(len(T_container)):
            kab_mean.append(mean(error_container[i]))

        # error
        for i in range(len(T_container)):
            kab_error.append(sqrt(var(error_container[i], ddof=1)))

        for i in range(len(T_container)):
            print(str(T_container[i])+', '+str(kab_mean[i])+', '+str(kab_error[i]))

        # return kab and error
        return [kab_mean, kab_error, T_container]


    def calculate(self, event):
        # Running flag
        self.keepGoing = True

         # evaluation
        if str(self.directory.GetValue()) == '':
            error_popup('No output directory selected!')
            return

        # start calculation in thread
        self.calc_exec()

        # busy dialog
        wx.CallAfter(self.calc_running, ())


    def close(self, event):
        self.Destroy()


    def fit(self, theory, data):
        # Fitting to transition state theories

        # Eyring equation
        if theory is 'Eyring':
            #  initial guess
            dS = -0.1
            dH = 0.1
            p_estimate = [dH, dS]

            # data
            kab_mean = data[0]
            kab_error = data[1]
            kab_T = data[2]

            # fit
            fit = leastsq(Eyring_fit, array(p_estimate), args=(array(kab_mean), array(kab_T), array(kab_error)), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

            # return dH and dS
            dH = fit[0][0]
            dS = fit[0][1]

            # Monte Carlo
            dH_sim = []
            dS_sim = []

            # loop 500 times
            p = [dH, dS]
            for mc in range(500):
                # create synthetic data
                kab_mean_sim = []
                for i in range(len(kab_T)):
                    kab_tmp = Eyring(kab_T[i], p)+uniform(-kab_error[i], kab_error[i])

                    # avoid beeing negative
                    while kab_tmp < 0:
                        kab_tmp =  Eyring(kab_T[i], p)+uniform(-kab_error[i], kab_error[i])

                    # store
                    kab_mean_sim.append(kab_tmp)

                # fit
                fit = leastsq(Eyring_fit, array([dH, dS]), args=(array(kab_mean_sim), array(kab_T), array(kab_error)), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

                # store dH and dS
                dH_sim.append(fit[0][0])
                dS_sim.append(fit[0][1])

            # error
            dH_err = sqrt(var(dH_sim, ddof = 1))
            dS_err = sqrt(var(dS_sim, ddof = 1))

            return [dH, dS, dH_err, dS_err]


    def plot(self, ground=0, ground_error=0, barrier=0, barrier_error=0, label=None, temperature=1, directory=None):
        """Function to generate energy landscape plots and a csv summary.

        ground:         Difference between ground states
        ground_error:   Error of ground states.
        barrier:        Energy barrier
        barrier_error:  Error of barrier.
        label:          Label of Y axis
        temperature:    Absolute temperature"""

        #x = ['State A', 'Transition', 'State B']
        x = [0, 1, 2]
        y = [0, barrier*temperature, ground*temperature]
        y_err = [0, barrier_error*temperature, ground_error*temperature]

        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # Box ratio
        pylab.axes([0.14, 0.125, 0.8, 0.5])

        # craete baseline
        pylab.plot([-0.5, 2.5], [0, 0], 'k--')

        # craete plot
        pylab.plot(x, y, 'r_', markersize=70, markeredgewidth= 5)

        # create error
        pylab.errorbar(x, y, yerr=y_err, ecolor='r', fmt=None, elinewidth=2, capsize=8)

        # label of axis
        pylab.ylabel(label, fontsize=19, weight='bold')
        pylab.xticks(x, ['State A', 'Transition', 'State B'])

        # Size of axis labels
        pylab.xticks(fontsize=18)
        pylab.yticks(fontsize=18)

        # Scale
        pylab.xlim(-0.5, 2.5)

        # y limit
        y_limit = [0, y[1]+y_err[1], y[1]-y_err[1], y[2]+y_err[2], y[2]-y_err[2]]
        min = 0
        max = 0
        for i in range(len(y_limit)):
            if min > y_limit[i]:
                min = y_limit[i]
            if max < y_limit[i]:
                max = y_limit[i]
        pylab.ylim(int((min-14)/10)*10+1, int((max+14)/10)*10)
        

        # save file
        pylab.savefig(directory+sep+label[0:2]+'_landscape.svg')
        pylab.savefig(directory+sep+label[0:2]+'_landscape.png', dpi = 72, transparent = True)

        # clear graph
        pylab.cla()
        pylab.close()

        # add to results tab
        self.main.tree_results.AppendItem(self.main.plots2d, directory+sep+label[0:2]+'_landscape.png', 0)
        self.main.plot2d.append(directory+sep+label[0:2]+'_landscape.png')

        # create the csv file
        # create the file
        file = open(directory+sep+label[0:2]+'_landscape.csv', 'w')

        # write the header
        file.write('State A;Transition;error;State B;error\n')

        # write the values
        file.write('0;'+str(barrier*temperature)+';'+str(barrier_error*temperature)+';'+str(ground*temperature)+';'+str(ground_error*temperature))

        # Write units
        file.write('\n\nkJ/mol;kJ/mol;kJ/mol;kJ/mol;kJ/mol')

        # close file
        file.close()

        # Add resutls to tree and save
        self.main.tree_results.AppendItem(self.main.txt, directory+sep+label[0:2]+'_landscape.csv', 0)
        self.main.results_txt.append(directory+sep+label[0:2]+'_landscape.csv')


    def sel_dir(self, event):
        dir = opendir('Select output directory.', str(self.directory.GetValue()), self)
        if dir:
            self.directory.SetValue(dir)

        # brings dialog to top
        self.Raise()


    def sync(self, type='read'):
        # syncronising variables
        if type == 'read':
            # add temperature
            for i in range(self.lendata):
                self.main.transition_grid.SetCellValue(i, 1, str(self.main.vanthoff_grid.GetCellValue(i, 2)))

            # kab
            for i in range(self.lendata):
                self.main.transition_grid.SetCellValue(i, 0, str(self.main.vanthoff_grid.GetCellValue(i, 0)))

            # dG
            for i in range(self.lendata):
                self.main.transition_grid.SetCellValue(i, 2, str(self.main.vanthoff_grid.GetCellValue(i, 3)))



class Vanthoff(wx.Frame):
    def __init__(self, main, *args, **kwds):
        # link parameters
        self.main = main

        # number of data
        self.lendata = 500

        # Build fit containers
        self.linear_fit = None
        self.logarithmic_fit = None

        # Build frame
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)
        self.Centre()

        # Background color
        self.SetBackgroundColour(wx.NullColour)

        # Build dialog
        self.build()

        # Synchronize data
        self.sync()


    def build(self):
        # main sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Subsizer
        subsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Image
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        subsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # right sizer
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # title
        self.title = wx.StaticText(self, -1, "van't Hoff Analysis")
        self.title.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        right_sizer.Add(self.title, 0, wx.ALL|wx.ALIGN_LEFT, 10)

        # Text
        self.text1 = wx.StaticText(self, -1, "Enter either dG or K (K = k(B-A)/k(A-B)) together with the absolute temperature.\n")
        right_sizer.Add(self.text1, 0, wx.ALL, 5)

        # The grid
        self.main.vanthoff_grid = NESSY_grid(self, -1, size=(1, 1))
        self.main.vanthoff_grid.CreateGrid(self.lendata, 4)
        self.main.vanthoff_grid.EnableDragColSize(0)
        self.main.vanthoff_grid.EnableDragRowSize(0)
        self.main.vanthoff_grid.EnableDragGridSize(0)
        self.main.vanthoff_grid.SetMinSize((510, 150))
        self.main.vanthoff_grid.SetColLabelValue(0, 'k(AB)')
        self.main.vanthoff_grid.SetColSize(0, 100)
        self.main.vanthoff_grid.SetColLabelValue(1, 'K')
        self.main.vanthoff_grid.SetColSize(1, 100)
        self.main.vanthoff_grid.SetColLabelValue(2, 'T [K]')
        self.main.vanthoff_grid.SetColSize(2, 80)
        self.main.vanthoff_grid.SetColLabelValue(3, 'dG(T) [J/mol]')
        self.main.vanthoff_grid.SetColSize(3, 120)
        right_sizer.Add(self.main.vanthoff_grid, 0, wx.ALL, 5)

        # Import / export
        exp = wx.BoxSizer(wx.HORIZONTAL)
        self.import_button = wx.Button(self, -1, "Import from file")
        self.Bind(wx.EVT_BUTTON, self.import_file, self.import_button)
        exp.Add(self.import_button, 0, wx.ALL, 5)
        self.export_button = wx.Button(self, -1, "Export to file")
        self.Bind(wx.EVT_BUTTON, self.export, self.export_button)
        exp.Add(self.export_button, 0, wx.ALL, 5)
        right_sizer.Add(exp, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Text
        self.text2 = wx.StaticText(self, -1, "\nData will be fitted to linear and exponential van't Hoff models.\nModel selection will be proformed using AICc and error will be\ndeterimined by 500 Monte Carlo Simulations.\n\nLinear model:\t\tlnK = -dH/RT + dS/R\n\nLogarithmic model:\tlnK = dC/R * ( (Th/T)- log(Ts/T) - 1)\n\t\t\t\tTs =  exp(dC - dS) * T\n\t\t\t\tTh = T - (dH/dC)\n")
        right_sizer.Add(self.text2, 0, wx.ALL, 5)

        # Directory
        directory_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.text3 = wx.StaticText(self, -1, 'Output directory:')
        self.text3.SetMinSize((120, 23))
        directory_sizer.Add(self.text3, 0, wx.LEFT|wx.RIGHT, 5)

        if str(self.main.proj_folder.GetValue()) == '':
            dir = ''
        else:
            dir = str(self.main.proj_folder.GetValue())+sep+'vanthoff'
        self.directory = wx.TextCtrl(self, -1, dir)
        self.directory.SetMinSize((290, 23))
        directory_sizer.Add(self.directory, 0, wx.LEFT, 5)

        self.button_dir = wx.Button(self, -1, "+")
        self.button_dir.SetMinSize((25, 23))
        self.Bind(wx.EVT_BUTTON, self.sel_dir, self.button_dir)
        directory_sizer.Add(self.button_dir, 0, wx.RIGHT, 5)
        right_sizer.Add(directory_sizer, 0, 0, 0)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_ok = wx.Button(self, -1, "Calculate")
        self.button_clear = wx.Button(self, -1, "Clear")
        self.button_refresh = wx.Button(self, -1, "Refresh")
        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.calculate, self.button_ok)
        self.Bind(wx.EVT_BUTTON, self.refresh, self.button_refresh)
        self.Bind(wx.EVT_BUTTON, self.clear, self.button_clear)
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        sizer_buttons.Add(self.button_ok, 0, wx.ALL, 10)
        sizer_buttons.Add(self.button_refresh, 0, wx.ALL, 10)
        sizer_buttons.Add(self.button_clear, 0, wx.ALL, 10)
        sizer_buttons.Add(self.button_close, 0, wx.ALL, 10)
        right_sizer.Add(sizer_buttons, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Text
        self.status = wx.StaticText(self, -1, "Waiting...")
        self.status.SetMinSize((450, 23))
        right_sizer.Add(self.status, 0, wx.ALL|wx.ALIGN_RIGHT, 5)

        # Activationbarrier
        self.button_barrier = wx.Button(self, -1, "Calculate activation barrier using Eyring equation.", style = wx.ALIGN_CENTER_VERTICAL)
        self.button_barrier.SetMinSize((430, 40))
        self.Bind(wx.EVT_BUTTON, self.eyring, self.button_barrier)
        right_sizer.Add(self.button_barrier, -1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)

        # Pack window
        # Add right sizer
        subsizer.Add(right_sizer, 0, 0, 0)
        mainsizer.Add(subsizer, 0, 0, 0)

        # Pack dialog
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()
        self.Center()


    def calculate(self, event):
        # syncronize
        self.sync(type='write')

        # Running flag
        self.keepGoing = True

        # evaluation
        if len(self.main.vanthoff['T']) == 0:
            error_popup('No data!')
            return
        if str(self.directory.GetValue()) == '':
            error_popup('No output directory selected!')
            return

        # start calculation in thread
        self.calc_exec()

        # Label
        self.status.SetLabel('Calculating...')

        # busy dialog
        wx.CallAfter(self.calc_running, ())


    def calc_exec(self):
        # start calculation in thread
        try:
            _thread.start_new_thread(self.calc_thread, ())
        except:
            print("Can't start calculation!")
            return


    def calc_running(self, event):
        '''Displays a cycling progress bar.'''
        # Build the progress dialog
        dlg = PP.PyProgress(self, -1, "NESSY", "Performing van't Hoff analysis.")

        #security counter
        canceled = 0

        # display
        while self.keepGoing or canceled > 1000:
            # wait 30 ms
            wx.MilliSleep(30)

            # increase cancel
            canceled += 1

            # update bar
            keepGoing = dlg.UpdatePulse()

        # Close dialog
        dlg.Destroy()


    def calc_thread(self):
        # collect variables
        dG = self.main.vanthoff['dG']
        K = self.main.vanthoff['K']
        T = self.main.vanthoff['T']

        # Calculate lnK
        lnK_single = []
        R = 8.31447215
        # loop over entries of T
        for entry in range(0, len(T)):
            # K
            if not K[entry] == '':
                lnK_single.append(log(float(K[entry])))

            # dG
            else:
                if not dG[entry] == '':
                    lnK_tmp = float(dG[entry]) / (R*float(T[entry]))
                    lnK_single.append(lnK_tmp)

        # convert T to floats
        T = [float(x) for x in T]

        # Containers for error caclulation
        T_container = []
        error_container = []        

        # loop over entries
        for entry in range(0, len(T)):
            # create new temperature entry, if not already present
            if not T[entry] in T_container:
                # add new temperature
                T_container.append(T[entry])

                # add new lnK for error calculation
                error_container.append([])

            # get index
            index = T_container.index(T[entry])

            # Store lnK
            error_container[index].append(lnK_single[entry])

            # Calculate mean lnK
            lnK = []
            for i in range(len(error_container)):
                lnK.append(mean(error_container[i]))


            # Calculate mean lnK error
            lnK_error = []
            for i in range(len(error_container)):
                lnK_error.append(sqrt(var(error_container[i], ddof=1)))


        # linear fit
        self.linear_fit = self.fit(lnK, lnK_error, T_container, mode='linear')

        # logarithmic fit
        self.logarithmic_fit = self.fit(lnK, lnK_error, T_container, mode='logarithmic')

        # report finished calculation
        self.finished()
        self.keepGoing = False


    def close(self, event):
        self.Destroy()


    def eyring(self, event):
        transition = Transition_state(self, 'Eyring', self, -1, '')
        transition.Show()


    def export(self, event):
        filename = savefile('Select file to export.', str(self.directory.GetValue()), '', 'all files (*.*)|*', self)
        if filename:
            # write file
            file = open(filename, 'w')
            file.write('kab;K;T;dG\n')

            # loop over datagrid
            for i in range(self.lendata):
                kab = str(self.main.vanthoff_grid.GetCellValue(i, 0))
                K = str(self.main.vanthoff_grid.GetCellValue(i, 1))
                T = str(self.main.vanthoff_grid.GetCellValue(i, 2))
                dG = str(self.main.vanthoff_grid.GetCellValue(i, 3))

                # skip if no data
                if T == '':
                    continue

                # write line
                file.write(kab+';'+K+';'+T+';'+dG+'\n')

            # close file
            file.close()

            # message
            message('Saved '+filename+'.', self)


    def clear(self, event):
        self.main.vanthoff = {'dG':[], 'kab':[], 'K':[], 'T':[]}
        for i in range(0, 4):
            for j in range (0, self.lendata):
                self.main.vanthoff_grid.SetCellValue(j, i, '')
        self.sync()


    def finished(self):
        wx.CallAfter(self.status.SetLabel, ("Done. Plots are in '2D plots', CSV files in 'Text Files'."))
        wx.CallAfter(self.main.MainTab.SetSelection, (self.main.MainTab.GetPageCount() - 2))


    def fit(self, lnK, lnK_error, T, mode='linear'):
        # linear fit
        if mode == 'linear':
            # if not enough data points are colelcted, abort.
            if len(T) < 2:
                self.finished()
                print('Could not fit to linear model, as number\nof parameters is bigger than number of data points!\n\n')
                return None

            linfit = leastsq(lin_fit, array([10.1, 10.1]), args=(array(lnK), array(T), array(lnK_error)), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

            # values
            dS = linfit[0][0]
            dH = linfit[0][1]
            dC = None

        # logarithmic fit
        if mode == 'logarithmic':
            # if not enough data points are colelcted, abort.
            if len(T) < 3:
                self.finished()
                print('Could not fit to logarithmic model, as number\nof parameters is bigger than number of data points!')
                return None

            logfit = leastsq(log_fit, array([10.1, 10.1, 10.1]), args=(array(lnK), array(T), array(lnK_error)), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

            # values
            dS = logfit[0][0]
            dH = logfit[0][1]
            dC = logfit[0][2]

        # Monte Carlo simulation
        # linear
        if mode == 'linear':
            mc_error = self.mc(lnK, lnK_error, T, dS, dH, model='linear')
        # logarithmic
        if mode == 'logarithmic':
            mc_error = self.mc(lnK, lnK_error, T, dS, dH, dC, model='logarithmic')

        # Calculate Chi2
        # linear
        if mode == 'linear':
            y_real = array(lnK)
            y_estimated = lin_model(array(T), [dS, dH])
            chi2 = sum((y_real - y_estimated)**2/array(lnK_error)**2)

         # logarithmic
        if mode == 'logarithmic':
            y_real = array(lnK)
            y_estimated = log_model(array(T), [dS, dH, dC])
            chi2 = sum((y_real - y_estimated)**2/array(lnK_error)**2)

        # plot
        # linear
        if mode == 'linear':
            self.plot(lnK, lnK_error, mc_error, chi2, T, dS, dH, model='linear')
        # logarithmic
        if mode == 'logarithmic':
            self.plot(lnK, lnK_error, mc_error, chi2, T, dS, dH, dC, model='logarithmic')

        return {'dS':dS, 'dH':dH, 'dC':dC, 'chi2':chi2}


    def import_file(self, event):
        # import file
        filename = openfile('Select file to import.', str(self.directory.GetValue()), '', 'all files (*.*)|*', self)

        # read file
        if filename:
            # read file
            self.main.vanthoff = vanthoff_list([filename], output=False)

            # refresh
            self.sync()


    def mc(self, lnK, lnK_error, T, dS=None, dH=None, dC=None, model='linear'):
        # Monte Carlo Simulation
        dS_mc = []
        dH_mc = []
        dC_mc = []

        for mc in range(0, 500):
            # parameters
            if model == 'linear':
                p = [dS, dH]
            else:
                p = [dS, dH, dC]

            # craete synthetic data
            x = T
            y = []
            for sim in range(0, len(x)):
                y.append(lin_model(x[sim], p)+uniform(-lnK_error[sim], lnK_error[sim]))

            # minimise
            if model == 'linear':
                linear_fit = leastsq(lin_fit, array(p), args=(array(y), array(x), array(lnK_error)), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)
            else:
                linear_fit = leastsq(log_fit, array(p), args=(array(y), array(x), array(lnK_error)), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

            # store dS and dH
            dS_mc.append(linear_fit[0][0])
            dH_mc.append(linear_fit[0][1])
            if not model == 'linear':
                dC_mc.append(linear_fit[0][2])

        # error
        dS_err = sqrt(var(dS_mc, ddof = 1))
        dH_err = sqrt(var(dH_mc, ddof = 1))
        if not model == 'linear':
            dC_err = sqrt(var(dC_mc, ddof = 1))
        else:
            dC_err = None

        # store MC results
        self.mc_errors = [dS_err, dH_err, dC_err]

        return [dS_err, dH_err, dC_err]


    def plot(self, lnK, lnK_error, mc_error, chi2, T, dS=None, dH=None, dC=None, model=None):
        # creating van't Hoff plots
        # directory
        directory = str(self.directory.GetValue())

        # create directory
        try:
            makedirs(directory)
        except:
            a = 'dummy'

        # create x and y values
        x = T
        y = lnK

        # Inverse T
        x = [1/i for i in x]

        # Frame width
        params={'axes.linewidth' : self.main.FRAMEWIDTH}
        pylab.rcParams.update(params)

        # Box ratio
        pylab.axes([0.14, 0.125, 0.8, 0.5])

        # plot
        # invert x values
        pylab.errorbar(x, y, yerr = lnK_error, fmt='ko')

        # fit
        x_fit = linspace(278, 320, num=100)
        if model=='logarithmic':
            y_fit = log_model(x_fit, [dS, dH, dC])
        else:
            y_fit = lin_model(x_fit, [dS, dH])
        # plot
        x_fit = [1/i for i in x_fit]
        pylab.plot(x_fit, y_fit, 'r-')

        # sort x values
        x.sort()

        # min and max
        min = x[0] - 0.01*x[0]
        max = x[len(x)-1] + 0.01*x[len(x)-1]

        # Labels
        pylab.xlim(min, max)
        pylab.xlabel('1/T [1/K]', fontsize=19, weight='bold')
        pylab.ylabel('lnK', fontsize=19, weight='bold')
        pylab.xticks(fontsize=17)
        pylab.yticks(fontsize=17)

        # file root
        if model=='logarithmic':
            fileroot = directory+sep+'vant_Hoff_logarithmic_model'
        else:
            fileroot = directory+sep+'vant_Hoff_linear_model'

        # svg image
        pylab.savefig(fileroot+self.main.PLOTFORMAT)

        # png image
        if model=='logarithmic':  # logarithmic model
            pylab.figtext(0.1, 0.9, 'dS = '+str(dS)[0:10]+' +/- '+str(mc_error[0])[0:6]+', dH = '+str(dH)[0:10]+' +/- '+str(mc_error[1])[0:6]+'\ndC = '+str(dC)[0:10]+' +/- '+str(mc_error[2])[0:6])

        else:   # linear model
            pylab.figtext(0.1, 0.9, 'dS = '+str(dS)[0:10]+' +/- '+str(mc_error[0])[0:6]+', dH = '+str(dH)[0:10]+' +/- '+str(mc_error[1])[0:6])
        pylab.savefig(fileroot+'.png', dpi = 72, transparent = True)

        # add to results tab
        self.main.tree_results.AppendItem (self.main.plots2d, fileroot+'.png', 0)
        self.main.plot2d.append(fileroot+'.png')

        # CSV file
        # Data points
        file = open(directory+sep+'dG_data_points.csv', 'w')
        file.write('1/T [1/K];lnK;error\n')

        # loop over x values
        for xv in range(0, len(x)):
            file.write(str(x[xv])+';'+str(lnK[xv])+';'+str(lnK_error[xv])+'\n')
        file.close()

        # Add resutls to tree and save
        self.main.tree_results.AppendItem(self.main.txt, directory+sep+'dG_data_points.csv', 0)
        self.main.results_txt.append(directory+sep+'dG_data_points.csv')

        # Fit
        file = open(fileroot+'_fit.csv', 'w')
        file.write('1/T [1/K];lnK\n')
        for xv in range(0, len(x_fit)):
            file.write(str(x_fit[xv])+';'+str(y_fit[xv])+'\n')
        file.close()

        # Add resutls to tree and save
        self.main.tree_results.AppendItem(self.main.txt, fileroot+'_fit.csv', 0)
        self.main.results_txt.append(fileroot+'_fit.csv')

        # log fit
        if model=='logarithmic':
            file = open(fileroot+'.csv', 'w')
            file.write('dS;err;dH;err;dC;err;Chi2;AICc\n')
            file.write(str(dS)+';'+str(mc_error[0])+';'+str(dH)+';'+str(mc_error[1])+';'+str(dC)+';'+str(mc_error[1])+';'+str(chi2)+';'+str(AICc(chi2, 4, len(self.main.vanthoff['T']))))
            file.close()

        # linear fit
        else:
            file = open(fileroot+'.csv', 'w')
            file.write('dS;err;dH;err;Chi2;AICc\n')
            file.write(str(dS)+';'+str(mc_error[0])+';'+str(dH)+';'+str(mc_error[1])+';'+str(chi2)+';'+str(AICc(chi2, 4, len(self.main.vanthoff['T']))))
            file.close()

        # Add resutls to tree and save
        self.main.tree_results.AppendItem(self.main.txt, fileroot+'.csv', 0)
        self.main.results_txt.append(fileroot+'.csv')

        # clear plot
        pylab.cla()
        pylab.clf()
        pylab.close()


    def refresh(self, event):
        self.sync()


    def sel_dir(self, event):
        dir = opendir('Select output directory.', str(self.directory.GetValue()), self)
        if dir:
            self.directory.SetValue(dir)

        # brings dialog to top
        self.Raise()


    def sync(self, type='read'):
        # syncronising variables
        if type == 'read':
            # dG
            for i in range(0, len(self.main.vanthoff['dG'])):
                self.main.vanthoff_grid.SetCellValue(i, 3, str(self.main.vanthoff['dG'][i]))

            # K
            for i in range(0, len(self.main.vanthoff['K'])):
                self.main.vanthoff_grid.SetCellValue(i, 1, str(self.main.vanthoff['K'][i]))

            # T
            for i in range(0, len(self.main.vanthoff['T'])):
                self.main.vanthoff_grid.SetCellValue(i, 2, str(self.main.vanthoff['T'][i]))

            # kab
            for i in range(0, len(self.main.vanthoff['kab'])):
                self.main.vanthoff_grid.SetCellValue(i, 0, str(self.main.vanthoff['kab'][i]))

        # writing variables
        if type == 'write':
            # empty variables
            self.main.vanthoff = {'dG':[], 'kab':[], 'K':[], 'T':[]}

            # dG
            for i in range(0, self.lendata):
                if not self.main.vanthoff_grid.GetCellValue(i, 2) == '':
                    self.main.vanthoff['dG'].append(str(self.main.vanthoff_grid.GetCellValue(i, 3)))

            # K
            for i in range(0, self.lendata):
                if not self.main.vanthoff_grid.GetCellValue(i, 2) == '':
                    self.main.vanthoff['K'].append(str(self.main.vanthoff_grid.GetCellValue(i, 1)))

            # T
            for i in range(0, self.lendata):
                if not self.main.vanthoff_grid.GetCellValue(i, 2) == '':
                    self.main.vanthoff['T'].append(str(self.main.vanthoff_grid.GetCellValue(i, 2)))

            # kab
            for i in range(0, self.lendata):
                if not self.main.vanthoff_grid.GetCellValue(i, 2) == '':
                    self.main.vanthoff['kab'].append(str(self.main.vanthoff_grid.GetCellValue(i, 0)))
