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
from math import exp
from os import sep
from random import uniform
import wx

# NESSY modules
from conf.path import NESSY_PIC, SYNTHETIC_PIC
from conf.filedialog import opendir
from conf.message import error_popup, message
from math_fns.models import model_1, model_2, model_3, model_4, model_5



class Initial_guess(wx.Dialog):
    """Set up initial Guess."""
    def __init__(self, model, main, *args, **kwds):
        # assign parameters
        self.model = int(model)
        self.main = main

        # create window
        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Build entries
        self.build()


    def build(self):
        # mainsizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # header
        self.header = wx.StaticText(self, -1, "Set Parameters")
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        # R2
        sizer_r2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_r2 = wx.StaticText(self, -1, "R2 [1/s]:")
        self.label_r2.SetMinSize((100, 17))
        sizer_r2.Add(self.label_r2, 0, wx.ALL, 5)

        self.r2 = wx.TextCtrl(self, -1, str(self.main.p[0][0]))
        self.r2.SetMinSize((80, 23))
        sizer_r2.Add(self.r2, 0, wx.RIGHT, 5)
        mainsizer.Add(sizer_r2, 1, wx.EXPAND, 0)

        # Model 2
        if self.model == 2:
            # Phi
            sizer_phi = wx.BoxSizer(wx.HORIZONTAL)
            self.label_phi = wx.StaticText(self, -1, "Phi [1/s]:")
            self.label_phi.SetMinSize((100, 17))
            sizer_phi.Add(self.label_phi, 0, wx.ALL, 5)

            self.phi = wx.TextCtrl(self, -1, str(self.main.p[1][1]))
            self.phi.SetMinSize((80, 23))
            sizer_phi.Add(self.phi, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_phi, 1, wx.EXPAND, 0)


            # Kex
            sizer_kex = wx.BoxSizer(wx.HORIZONTAL)
            self.label_kex = wx.StaticText(self, -1, "kex [1/s]:")
            self.label_kex.SetMinSize((100, 17))
            sizer_kex.Add(self.label_kex, 0, wx.ALL, 5)

            self.kex = wx.TextCtrl(self, -1, str(self.main.p[1][2]))
            self.kex.SetMinSize((80, 23))
            sizer_kex.Add(self.kex, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_kex, 1, wx.EXPAND, 0)

        # Model 3
        if self.model == 3:
            # Kex
            sizer_kex = wx.BoxSizer(wx.HORIZONTAL)
            self.label_kex = wx.StaticText(self, -1, "kex [1/s]:")
            self.label_kex.SetMinSize((100, 17))
            sizer_kex.Add(self.label_kex, 0, wx.ALL, 5)

            self.kex = wx.TextCtrl(self, -1, str(self.main.p[2][1]))
            self.kex.SetMinSize((80, 23))
            sizer_kex.Add(self.kex, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_kex, 1, wx.EXPAND, 0)

            # dw
            sizer_dw = wx.BoxSizer(wx.HORIZONTAL)
            self.label_dw = wx.StaticText(self, -1, "dw [1/s]:")
            self.label_dw.SetMinSize((100, 17))
            sizer_dw.Add(self.label_dw, 0, wx.ALL, 5)

            self.dw = wx.TextCtrl(self, -1, str(self.main.p[2][2]))
            self.dw.SetMinSize((80, 23))
            sizer_dw.Add(self.dw, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_dw, 1, wx.EXPAND, 0)

            # pb
            sizer_pb = wx.BoxSizer(wx.HORIZONTAL)
            self.label_pb = wx.StaticText(self, -1, "pb:")
            self.label_pb.SetMinSize((100, 17))
            sizer_pb.Add(self.label_pb, 0, wx.ALL, 5)

            self.pb = wx.TextCtrl(self, -1, str(self.main.p[2][3]))
            self.pb.SetMinSize((80, 23))
            sizer_pb.Add(self.pb, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_pb, 1, wx.EXPAND, 0)

        # Model 4
        if self.model == 4:
            # Phi1
            sizer_phi = wx.BoxSizer(wx.HORIZONTAL)
            self.label_phi = wx.StaticText(self, -1, "Phi [1/s]:")
            self.label_phi.SetMinSize((100, 17))
            sizer_phi.Add(self.label_phi, 0, wx.ALL, 5)

            self.phi = wx.TextCtrl(self, -1, str(self.main.p[3][1]))
            self.phi.SetMinSize((80, 23))
            sizer_phi.Add(self.phi, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_phi, 1, wx.EXPAND, 0)


            # Kex1
            sizer_kex = wx.BoxSizer(wx.HORIZONTAL)
            self.label_kex = wx.StaticText(self, -1, "kex [1/s]:")
            self.label_kex.SetMinSize((100, 17))
            sizer_kex.Add(self.label_kex, 0, wx.ALL, 5)

            self.kex = wx.TextCtrl(self, -1, str(self.main.p[3][2]))
            self.kex.SetMinSize((80, 23))
            sizer_kex.Add(self.kex, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_kex, 1, wx.EXPAND, 0)

            # phi2
            sizer_phi2 = wx.BoxSizer(wx.HORIZONTAL)
            self.label_phi2 = wx.StaticText(self, -1, "phi2 [1/s]:")
            self.label_phi2.SetMinSize((100, 17))
            sizer_phi2.Add(self.label_phi2, 0, wx.ALL, 5)

            self.phi2 = wx.TextCtrl(self, -1, str(self.main.p[3][3]))
            self.phi2.SetMinSize((80, 23))
            sizer_phi2.Add(self.phi2, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_phi2, 1, wx.EXPAND, 0)

            # Kex2
            sizer_kex2 = wx.BoxSizer(wx.HORIZONTAL)
            self.label_kex2 = wx.StaticText(self, -1, "kex2 [1/s]:")
            self.label_kex2.SetMinSize((100, 17))
            sizer_kex2.Add(self.label_kex2, 0, wx.ALL, 5)

            self.kex2 = wx.TextCtrl(self, -1, str(self.main.p[3][4]))
            self.kex2.SetMinSize((80, 23))
            sizer_kex2.Add(self.kex2, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_kex2, 1, wx.EXPAND, 0)

        # Model 5
        if self.model == 5:
            # Kex
            sizer_kex = wx.BoxSizer(wx.HORIZONTAL)
            self.label_kex = wx.StaticText(self, -1, "kex [1/s]:")
            self.label_kex.SetMinSize((100, 17))
            sizer_kex.Add(self.label_kex, 0, wx.ALL, 5)

            self.kex = wx.TextCtrl(self, -1, str(self.main.p[4][1]))
            self.kex.SetMinSize((80, 23))
            sizer_kex.Add(self.kex, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_kex, 1, wx.EXPAND, 0)

            # dw
            sizer_dw = wx.BoxSizer(wx.HORIZONTAL)
            self.label_dw = wx.StaticText(self, -1, "dw [1/s]:")
            self.label_dw.SetMinSize((100, 17))
            sizer_dw.Add(self.label_dw, 0, wx.ALL, 5)

            self.dw = wx.TextCtrl(self, -1, str(self.main.p[4][2]))
            self.dw.SetMinSize((80, 23))
            sizer_dw.Add(self.dw, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_dw, 1, wx.EXPAND, 0)

            # pb
            sizer_pb = wx.BoxSizer(wx.HORIZONTAL)
            self.label_pb = wx.StaticText(self, -1, "pb:")
            self.label_pb.SetMinSize((100, 17))
            sizer_pb.Add(self.label_pb, 0, wx.ALL, 5)

            self.pb = wx.TextCtrl(self, -1, str(self.main.p[4][3]))
            self.pb.SetMinSize((80, 23))
            sizer_pb.Add(self.pb, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_pb, 1, wx.EXPAND, 0)

            # kex2
            sizer_kex2 = wx.BoxSizer(wx.HORIZONTAL)
            self.label_kex2 = wx.StaticText(self, -1, "kex2 [1/s]:")
            self.label_kex2.SetMinSize((100, 17))
            sizer_kex2.Add(self.label_kex2, 0, wx.ALL, 5)

            self.kex2 = wx.TextCtrl(self, -1, str(self.main.p[4][4]))
            self.kex2.SetMinSize((80, 23))
            sizer_kex2.Add(self.kex2, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_kex2, 1, wx.EXPAND, 0)

            # dw2
            sizer_dw2 = wx.BoxSizer(wx.HORIZONTAL)
            self.label_dw2 = wx.StaticText(self, -1, "dw2 [1/s]:")
            self.label_dw2.SetMinSize((100, 17))
            sizer_dw2.Add(self.label_dw2, 0, wx.ALL, 5)

            self.dw2 = wx.TextCtrl(self, -1, str(self.main.p[4][5]))
            self.dw2.SetMinSize((80, 23))
            sizer_dw2.Add(self.dw2, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_dw2, 1, wx.EXPAND, 0)

            # pc
            sizer_pc = wx.BoxSizer(wx.HORIZONTAL)
            self.label_pc = wx.StaticText(self, -1, "pc:")
            self.label_pc.SetMinSize((100, 17))
            sizer_pc.Add(self.label_pc, 0, wx.ALL, 5)

            self.pc = wx.TextCtrl(self, -1, str(self.main.p[4][6]))
            self.pc.SetMinSize((80, 23))
            sizer_pc.Add(self.pc, 0, wx.RIGHT, 5)
            mainsizer.Add(sizer_pc, 1, wx.EXPAND, 0)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_create = wx.Button(self, -1, "Start")
        self.Bind(wx.EVT_BUTTON, self.start, self.button_create)
        sizer_buttons.Add(self.button_create, 0, wx.ALL, 5)

        self.button_cancel = wx.Button(self, -1, "Abort")
        self.Bind(wx.EVT_BUTTON, self.abort, self.button_cancel)
        sizer_buttons.Add(self.button_cancel, 0, wx.ALL, 5)
        mainsizer.Add(sizer_buttons, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Pack dialog
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()

    def start(self, event):
        # set parameters
        # model 1
        if self.model == 1:
            self.main.p[0] = [float(self.r2.GetValue())]

        # model 2
        if self.model == 2:
            self.main.p[1] = [float(self.r2.GetValue()), float(self.phi.GetValue()), float(self.kex.GetValue())]

        # model 3
        if self.model == 3:
            self.main.p[2] = [float(self.r2.GetValue()), float(self.kex.GetValue()), float(self.dw.GetValue()), float(self.pb.GetValue())]

        # model 4
        if self.model == 4:
            self.main.p[3] = [float(self.r2.GetValue()), float(self.phi.GetValue()), float(self.kex.GetValue()), float(self.phi2.GetValue()), float(self.kex2.GetValue())]

        # model 3
        if self.model == 5:
            self.main.p[4] = [float(self.r2.GetValue()), float(self.kex.GetValue()), float(self.dw.GetValue()), float(self.pb.GetValue()), float(self.kex2.GetValue()), float(self.dw2.GetValue()), float(self.pc.GetValue())]


        # close dialog
        self.Destroy()


    def abort(self, event):
        self.main.p = None
        self.Destroy()



class Synthetic_data(wx.Dialog):
    """Class to generate synthetic data."""

    def __init__(self, directory, *args, **kwds):
        # directory
        self.proj_directory = directory

        # Experiment type
        self.exp_mode = 0

        # initial guess
        p1 = ['15.23']
        p2 = ['15.23', '47457.43', '3750.25']
        p3 = ['15.23', '306.15', '1875.51', '0.072']
        p4 = ['15.23', '47457.43', '3750.25', '27457.43', '750.25']
        p5 = ['15.23', '157.48', '1222.74', '0.062', '428.55', '52.25', '0.33']
        self.p = [p1, p2, p3, p4, p5]

        # Create the dialog
        kwds["style"] = wx.CAPTION
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Build window
        self.build()


    def build(self):
        # mainsizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # subsizer
        subsizer = wx.BoxSizer(wx.HORIZONTAL)

        # bitmap
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(SYNTHETIC_PIC, wx.BITMAP_TYPE_ANY))
        subsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # right sizer
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # header
        self.header = wx.StaticText(self, -1, "Synthetic Data Creator")
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        right_sizer.Add(self.header, 0, wx.ALL, 5)

        # frequencies
        sizer_freq = wx.BoxSizer(wx.HORIZONTAL)
        self.label_freq = wx.StaticText(self, -1, "CPMG frequencies (x-values) [Hz]:")
        self.label_freq.SetMinSize((230, 17))
        sizer_freq.Add(self.label_freq, 0, wx.LEFT|wx.TOP, 5)

        self.freq = wx.TextCtrl(self, -1, "0, 25, 50, 50, 75, 75, 100, 150, 150, 200, 200, 300, 500, 600, 700, 900, 1000, 1500, 2000")
        self.freq.SetMinSize((300, 23))
        sizer_freq.Add(self.freq, 0, wx.RIGHT, 5)
        right_sizer.Add(sizer_freq, 0, 0, 0)

        # CPMG delay
        sizer_delay = wx.BoxSizer(wx.HORIZONTAL)
        self.label_delay = wx.StaticText(self, -1, "CPMG delay [s]:")
        self.label_delay.SetMinSize((230, 17))
        sizer_delay.Add(self.label_delay, 0, wx.LEFT|wx.TOP, 5)

        self.cpmg_delay = wx.TextCtrl(self, -1, "0.08")
        self.cpmg_delay.SetMinSize((80, 23))
        sizer_delay.Add(self.cpmg_delay, 0, 0, 0)
        right_sizer.Add(sizer_delay, 0, wx.EXPAND, 0)

        # directory
        sizer_directory = wx.BoxSizer(wx.HORIZONTAL)
        self.label_directory = wx.StaticText(self, -1, "Output directory:")
        self.label_directory.SetMinSize((230, 17))
        sizer_directory.Add(self.label_directory, 0, wx.LEFT|wx.TOP, 5)

        self.directory = wx.TextCtrl(self, -1, self.proj_directory)
        self.directory.SetMinSize((265, 23))
        sizer_directory.Add(self.directory, 0, wx.TOP, 5)

        self.button_directory = wx.Button(self, -1, "+")
        self.button_directory.SetMinSize((30, 23))
        self.Bind(wx.EVT_BUTTON, self.select_directory, self.button_directory)
        sizer_directory.Add(self.button_directory, 0, wx.LEFT|wx.RIGHT|wx.TOP, 5)
        right_sizer.Add(sizer_directory, 0, wx.EXPAND, 0)

        # model
        sizer_model = wx.BoxSizer(wx.HORIZONTAL)
        self.label_model = wx.StaticText(self, -1, "Model:")
        self.label_model.SetMinSize((230, 17))
        sizer_model.Add(self.label_model, 0, wx.LEFT|wx.TOP, 5)

        self.model = wx.ComboBox(self, -1, choices=["1:\tno exchange", "2:\t2 states fast exchange", "3:\t2 states slow exchange", "4:\t3 states fast exchange", "5:\t3 states slow exchange"], style=wx.CB_DROPDOWN)
        self.model.SetMinSize((300, 25))
        self.model.SetSelection(1)
        sizer_model.Add(self.model, 0, wx.TOP, 5)
        right_sizer.Add(sizer_model, 0, wx.EXPAND, 0)

        # error
        sizer_error = wx.BoxSizer(wx.HORIZONTAL)
        self.label_error = wx.StaticText(self, -1, "Error [%]:")
        self.label_error.SetMinSize((230, 17))
        sizer_error.Add(self.label_error, 0, wx.LEFT|wx.TOP|wx.ALIGN_BOTTOM, 5)

        self.error = wx.Slider(self, -1, 5, 1, 20, style=wx.SL_HORIZONTAL|wx.SL_LABELS)
        self.error.SetMinSize((300, 38))
        sizer_error.Add(self.error, 0, wx.RIGHT|wx.TOP, 5)
        right_sizer.Add(sizer_error, 0, wx.EXPAND, 0)

        # Experiment Typt
        sizer_expsel = wx.BoxSizer(wx.HORIZONTAL)
        # CPMG
        self.cpmg = wx.RadioButton(self, -1, "CPMG")
        sizer_expsel.Add(self.cpmg, 0, wx.LEFT|wx.RIGHT, 5)
        self.Bind(wx.EVT_RADIOBUTTON, self.selcpmg, self.cpmg)
        # On resonance R1rho
        self.onresonance = wx.RadioButton(self, -1, "On resonance R1rho")
        sizer_expsel.Add(self.onresonance, 0, wx.LEFT|wx.RIGHT, 5)
        self.Bind(wx.EVT_RADIOBUTTON, self.selon, self.onresonance)
        # Off resonance R1rho
        self.offresonance = wx.RadioButton(self, -1, "Off resonance R1rho")
        sizer_expsel.Add(self.offresonance, 0, wx.LEFT|wx.RIGHT, 5)
        self.Bind(wx.EVT_RADIOBUTTON, self.seloff, self.offresonance)
        right_sizer.Add(sizer_expsel, 0, wx.TOP|wx.BOTTOM|wx.ALIGN_CENTER_HORIZONTAL, 10)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_create = wx.Button(self, -1, "Create")
        self.Bind(wx.EVT_BUTTON, self.craete_lists, self.button_create)
        sizer_buttons.Add(self.button_create, 0, wx.ALL, 5)

        self.button_restore = wx.Button(self, -1, "Restore default")
        self.Bind(wx.EVT_BUTTON, self.restore, self.button_restore)
        sizer_buttons.Add(self.button_restore, 0, wx.ALL, 5)

        self.button_cancel = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.cancel, self.button_cancel)
        sizer_buttons.Add(self.button_cancel, 0, wx.ALL, 5)
        right_sizer.Add(sizer_buttons, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Pack right sizer
        subsizer.Add(right_sizer, 0, wx.EXPAND, 0)

        # Pack window
        mainsizer.Add(subsizer, 0, wx.EXPAND, 0)
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()


    def cancel(self, event):
        self.Destroy()


    def craete_lists(self, event):
        # check entries
        if str(self.directory.GetValue()) == '':
            error_popup('No directory specified!')
            return

        # create x values
        x_values = str(self.freq.GetValue()).split(',')

        # error
        error = float(self.error.GetValue()) / 200

        # CPMG delay
        cpmg_delay = float(self.cpmg_delay.GetValue())

        # reference intensity
        I0 = 10000

        # models
        # CPMG
        if self.exp_mode == 0:
            models = {"1:\tno exchange": model_1, "2:\t2 states fast exchange": model_2, "3:\t2 states slow exchange": model_3, "4:\t3 states fast exchange": model_4, "5:\t3 states slow exchange": model_5}


        # selected model
        selected_model = str(self.model.GetValue())

        # set initial guess
        guess = Initial_guess(selected_model[0:1], self, None, -1, "")
        guess.ShowModal()

        # Abort
        if self.p == None:
            return

        # csv file containers
        csv_x = []
        csv_y = []

        # loop over x-values
        for y in range(0, len(x_values)):
            # reference
            if int(x_values[y]) == 0:
                # save file
                filename = str(self.directory.GetValue())+sep+'Dataset_'+str(y+1)+'.txt'

                # open file
                file = open(filename, 'w')
                file.write('Dummy-1-NH\tNone\tNone\t'+str(I0))
                file.close()

            # datapoint
            else:
                # calculate R2eff
                R2eff_tmp = models[selected_model](float(x_values[y]), self.p[int(selected_model[0:1])-1])
                R2eff = R2eff_tmp + uniform(-error, error)*R2eff_tmp

                # calculate intensity
                y_value = I0 / exp(R2eff*cpmg_delay)

                # save file
                filename = str(self.directory.GetValue())+sep+'Dataset_'+str(y+1)+'.txt'

                # open file
                file = open(filename, 'w')
                file.write('Dummy-1-NH\tNone\tNone\t'+str(y_value))
                file.close()

                # for csv file
                csv_x.append(str(x_values[y]))
                csv_y.append(str(R2eff))

        # write vd list
        file = open(str(self.directory.GetValue())+sep+'vd', 'w')
        for i in range(0, len(x_values)):
            file.write(str(int(x_values[i]))+'\n')
        file.close()

        # create csv file
        file = open(str(self.directory.GetValue())+sep+'Synthetic_R2eff.csv', 'w')
        if self.exp_mode == 0:
            file.write('CPMG freq [Hz];R2eff [1/s]\n\n')
        else:
            file.write('Spin lock field [Hz];R1rho [1/s]\n\n')
        for i in range(0, len(csv_x)):
            file.write(str(int(csv_x[i]))+';'+str(float(csv_y[i]))+'\n')
        file.close()


        # feedback
        message('Synthetic data set was successfully created!\n\nData is in Sparky format.', self)


    def restore(self, event):
        # CPMG frequencies
        self.freq.SetValue("0, 25, 50, 50, 75, 75, 100, 150, 150, 200, 200, 300, 500, 600, 700, 900, 1000, 1500, 2000")

        # CPMG delay
        self.cpmg_delay.SetValue("0.04")

        # Directory
        self.directory.SetValue(self.proj_directory)

        # error
        self.error.SetValue(5)


    def select_directory(self, event):
        folder = opendir('Select folder', str(self.directory.GetValue()), self)
        if folder:
            self.directory.SetValue(folder)


    def selcpmg(self, event):
        self.label_delay.SetLabel('CPMG delay [s]:')
        self.label_freq.SetLabel("CPMG frequencies (x-values) [Hz]:")
        self.exp_mode = 0


    def selon(self, event):
        self.label_delay.SetLabel('Spin lock time [s]')
        self.label_freq.SetLabel("Spin lock field [Hz]:")
        self.exp_mode = 1


    def seloff(self, event):
        self.label_delay.SetLabel('Spin lock time [s]')
        self.label_freq.SetLabel("Spin lock field [Hz]:")
        self.exp_mode = 2
