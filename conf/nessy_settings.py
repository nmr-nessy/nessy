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


# Python modules
from os import sep
import wx

# NESSY modules
from conf.message import question, error_popup
from conf.path import NESSY_PIC, SETTINGS_SIDE_PIC
from conf.project import stringtolist


class settings(wx.Dialog):
    def __init__(self, main, *args, **kwds):
        """Create Dialog."""

        # assign main frame
        self.main = main

        # Create Window
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY Settings")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Main sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # subsizer
        subsizer = wx.BoxSizer(wx.HORIZONTAL)

        # Image
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(SETTINGS_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        subsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # right sizer
        right_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        self.title = wx.StaticText(self, -1, "NESSY Settings")
        self.title.SetFont(wx.Font(14, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        right_sizer.Add(self.title, 0, wx.ALL, 5)

        # Model Selection Mode
        sizer_modsel = wx.BoxSizer(wx.HORIZONTAL)
        self.label_modsel = wx.StaticText(self, -1, "Model Selection Mode:")
        self.label_modsel.SetMinSize((250, 34))
        sizer_modsel.Add(self.label_modsel, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

        # AICc
        self.aicc = wx.RadioButton(self, -1, "AICc")
        sizer_modsel.Add(self.aicc, 0, wx.LEFT|wx.RIGHT, 5)

        # AIC
        self.aic = wx.RadioButton(self, -1, "AIC")
        sizer_modsel.Add(self.aic, 0, wx.LEFT|wx.RIGHT, 5)

        # F-Test
        self.f_test = wx.RadioButton(self, -1, "F-Test")
        sizer_modsel.Add(self.f_test, 0, wx.LEFT|wx.RIGHT, 5)

        #Chi2
        self.chi = wx.RadioButton(self, -1, "Chi2")
        sizer_modsel.Add(self.chi, 0, wx.LEFT|wx.RIGHT, 5)

        #Alpha
        #self.alpha = wx.RadioButton(self, -1, "Alpha")
        #self.alpha.SetToolTipString("Chemical exchange time regime is characterized by:\nalpha = ( (B(0)2 + B(0)1) / (B(0)2 - B(0)1) ) * ( (Rex2 - Rex1) / (Rex2 + Rex1) )\n\nThis function is only applicable for global fits!\nFast exchange 2-site model has to be calculated.\n\nFor individual fits, it will be automaticall set to AICc.")
        #sizer_modsel.Add(self.alpha, 0, wx.LEFT|wx.RIGHT, 5)

        #Chi2
        self.manual = wx.RadioButton(self, -1, "Manual")
        sizer_modsel.Add(self.manual, 0, wx.LEFT|wx.RIGHT, 5)

        # Pack Model Selection
        right_sizer.Add(sizer_modsel, 0, 0, 0)

        # Monte Carlo
        sizer_mc = wx.BoxSizer(wx.HORIZONTAL)
        self.label_mc = wx.StaticText(self, -1, "Number of Monte Carlo Simulations:")
        self.label_mc.SetMinSize((250, 34))
        sizer_mc.Add(self.label_mc, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.num_mc = wx.SpinCtrl(self, -1, "500", min=2, max=1000)
        sizer_mc.Add(self.num_mc, 0, wx.LEFT|wx.RIGHT, 5)
        right_sizer.Add(sizer_mc, 0, 0, 0)

        # Grid increment
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label_grid = wx.StaticText(self, -1, "Increments for Grid Search:")
        label_grid.SetMinSize((250, 34))
        sizer.Add(label_grid, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

        # R2
        #labelr2 = wx.StaticText(self, -1, "R2: ")
        #sizer.Add(labelr2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        #self.r2 = wx.TextCtrl(self, -1, str(self.main.GRID_INCREMENT[0]))
        #self.r2.SetMinSize((50, 23))
        #sizer.Add(self.r2, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # kex
        labelkex = wx.StaticText(self, -1, "kex: ")
        sizer.Add(labelkex, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.kex = wx.TextCtrl(self, -1, str(self.main.GRID_INCREMENT[1]))
        self.kex.SetMinSize((50, 23))
        sizer.Add(self.kex, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # dw
        labeldw = wx.StaticText(self, -1, "dw: ")
        sizer.Add(labeldw, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.dw = wx.TextCtrl(self, -1, str(self.main.GRID_INCREMENT[2]))
        self.dw.SetMinSize((50, 23))
        sizer.Add(self.dw, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # pb
        labelpb = wx.StaticText(self, -1, "pb: ")
        sizer.Add(labelpb, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.pb = wx.TextCtrl(self, -1, str(self.main.GRID_INCREMENT[3]))
        self.pb.SetMinSize((50, 23))
        sizer.Add(self.pb, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        # phi
        labelphi = wx.StaticText(self, -1, "phi: ")
        sizer.Add(labelphi, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.phi = wx.TextCtrl(self, -1, str(self.main.GRID_INCREMENT[4]))
        self.phi.SetMinSize((50, 23))
        sizer.Add(self.phi, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        right_sizer.Add(sizer, 0, 0, 0)

        # use gridsearch
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "Minimisation Method:")
        label.SetMinSize((250, 34))
        sizer.Add(label, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

        self.minimisation_method = wx.ComboBox(self, -1, choices=["Least square only", "Least square until convergence", "Grid search & least square"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.minimisation_method.SetMinSize((230, 25))
        sizer.Add(self.minimisation_method, 0, wx.LEFT, 5)
        right_sizer.Add(sizer, 0, 0, 0)

        # use gridsearch
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "Fitting accuracy:")
        label.SetMinSize((250, 34))
        sizer.Add(label, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

        self.fit_accuracy = wx.ComboBox(self, -1, choices=["Exact", "Moderate", "Loose"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.fit_accuracy.SetMinSize((230, 25))
        sizer.Add(self.fit_accuracy, 0, wx.LEFT, 5)
        right_sizer.Add(sizer, 0, 0, 0)

        # Number of Data sets
        #sizer_data = wx.BoxSizer(wx.HORIZONTAL)
        #self.label_data = wx.StaticText(self, -1, "Maximum Data Sets:")
        #self.label_data.SetMinSize((250, 34))
        #sizer_data.Add(self.label_data, 0, wx.ALL, 5)
        #self.num_datasets = wx.SpinCtrl(self, -1, "0", min=20, max=100)
        #sizer_data.Add(self.num_datasets, 0, wx.ALL, 5)
        #right_sizer.Add(sizer_data, 0, 0, 0)

        # R20 limit
        #sizer_r2 = wx.BoxSizer(wx.HORIZONTAL)
        #self.label_r2 = wx.StaticText(self, -1, "Limit of R20 relative to\nR2eff of highest frequency [%]:")
        #self.label_r2.SetMinSize((250, 34))
        #sizer_r2.Add(self.label_r2, 0, wx.ALL, 5)
        #self.min_r2 = wx.TextCtrl(self, -1, "30.0")
        #sizer_r2.Add(self.min_r2, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        #right_sizer.Add(sizer_r2, 0, 0, 0)

        # Exclude Difference
        sizer_diff = wx.BoxSizer(wx.HORIZONTAL)
        self.label_diff = wx.StaticText(self, -1, "Minimal Difference Between Lowest\nand Highest R2eff(v[CPMG]) in [1/s]:")
        self.label_diff.SetMinSize((250, 34))
        sizer_diff.Add(self.label_diff, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.min_diff = wx.TextCtrl(self, -1, "2.0")
        sizer_diff.Add(self.min_diff, 0, wx.LEFT|wx.ALIGN_CENTER_VERTICAL, 5)
        right_sizer.Add(sizer_diff, 0, 0, 0)

        # Exclude time point
        sizer_ex = wx.BoxSizer(wx.HORIZONTAL)
        self.label_ex = wx.StaticText(self, -1, "Calculate Models 2-5:")
        self.label_ex.SetMinSize((250, 34))
        sizer_ex.Add(self.label_ex, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.exclude_order = wx.ComboBox(self, -1, choices=["only if exchange is expected", "for entire dataset"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.exclude_order.SetMinSize((230, 25))
        sizer_ex.Add(self.exclude_order, 0, wx.LEFT, 5)
        right_sizer.Add(sizer_ex, 0, 0, 0)

        # Scale y axis R2eff plots
        sizer_plots = wx.BoxSizer(wx.HORIZONTAL)
        self.label_plots = wx.StaticText(self, -1, "Y axis in R2eff / R1rho plots [Hz]:")
        self.label_plots.SetMinSize((250, 34))
        sizer_plots.Add(self.label_plots, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.range_plots = wx.TextCtrl(self, -1, "0-50")
        sizer_plots.Add(self.range_plots, 0, wx.LEFT, 5)
        right_sizer.Add(sizer_plots, 0, 0, 0)

        # Weight of frame in plots
        sizer_weight = wx.BoxSizer(wx.HORIZONTAL)
        self.label_weight = wx.StaticText(self, -1, "Width of frame in plots [points]:")
        self.label_weight.SetMinSize((250, 34))
        sizer_weight.Add(self.label_weight, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.range_weight = wx.TextCtrl(self, -1, str(self.main.FRAMEWIDTH))
        sizer_weight.Add(self.range_weight, 0, wx.LEFT, 5)
        right_sizer.Add(sizer_weight, 0, 0, 0)

        # Image format for plots
        sizer_format = wx.BoxSizer(wx.HORIZONTAL)
        self.label_format = wx.StaticText(self, -1, "Output format for plots:")
        self.label_format.SetMinSize((250, 34))
        sizer_format.Add(self.label_format, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.plot_format = wx.ComboBox(self, -1, choices=["SVG", "PS", "EPS", "PDF"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.plot_format.SetMinSize((60, 25))
        sizer_format.Add(self.plot_format, 0, wx.LEFT, 5)
        right_sizer.Add(sizer_format, 0, 0, 0)

        # Create intensity plots
        sizer_intensity = wx.BoxSizer(wx.HORIZONTAL)
        self.label_intensity = wx.StaticText(self, -1, "Create Intensity plots?")
        self.label_intensity.SetMinSize((250, 34))
        sizer_intensity.Add(self.label_intensity, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.plot_intensity = wx.ComboBox(self, -1, choices=["Yes", "No"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.plot_intensity.SetMinSize((60, 25))
        sizer_intensity.Add(self.plot_intensity, 0, wx.LEFT, 5)
        right_sizer.Add(sizer_intensity, 0, 0, 0)

        # Create R2eff plots
        sizer_r2eff_plots = wx.BoxSizer(wx.HORIZONTAL)
        self.label_r2eff_plots = wx.StaticText(self, -1, "Create R2eff / R1rho plots?")
        self.label_r2eff_plots.SetMinSize((250, 34))
        sizer_r2eff_plots.Add(self.label_r2eff_plots, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.plot_r2eff_plots = wx.ComboBox(self, -1, choices=["Yes", "No"], style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self.plot_r2eff_plots.SetMinSize((60, 25))
        sizer_r2eff_plots.Add(self.plot_r2eff_plots, 0, wx.LEFT, 5)
        right_sizer.Add(sizer_r2eff_plots, 0, 0, 0)

        # Attention Text
        #self.label_Text = wx.StaticText(self, -1, "Attention:\n\nChanging NESSY Settings strongly influences NESSY calculation!\n\nModel Selection: Default method is Akaike Information Criteria with a second order\n correction for small sample sizes (AICc). AICc does not require normally distributed data and \ntakes in account small sample size (n < 50).", style=wx.ALIGN_CENTRE)
        #self.label_Text.SetMinSize((400, 160))
        #right_sizer.Add(self.label_Text, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 15)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_cancel = wx.Button(self, -1, "Cancel")
        self.Bind(wx.EVT_BUTTON, self.cancel, self.button_cancel)
        sizer_buttons.Add(self.button_cancel, 0, wx.ALL, 5)
        self.button_restore = wx.Button(self, -1, "Restore Default")
        self.Bind(wx.EVT_BUTTON, self.restore, self.button_restore)
        sizer_buttons.Add(self.button_restore, 0, wx.ALL, 5)
        self.button_save = wx.Button(self, -1, "Save")
        self.Bind(wx.EVT_BUTTON, self.save, self.button_save)
        sizer_buttons.Add(self.button_save, 0, wx.ALL, 5)
        right_sizer.Add(sizer_buttons, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.TOP, 20)

        # add to right sizer
        subsizer.Add(right_sizer, 0, 0, 0)
        #mainsizer.Add(subsizer, 0, 0, 0)

        # vertical line
        line = wx.StaticLine(self, -1, style=wx.LI_VERTICAL)
        subsizer.Add(line, 0, wx.EXPAND|wx.ALL, 5)

        # Other settings
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Models
        self.button_models = wx.Button(self, -1, "Select Models")
        self.button_models.SetMinSize((150, 40))
        self.Bind(wx.EVT_BUTTON, self.main.models, self.button_models)
        sizer.Add(self.button_models, 0, wx.ALL, 5)

        # residues
        self.button_residues = wx.Button(self, -1, "Select Residues")
        self.button_residues.SetMinSize((150, 40))
        self.Bind(wx.EVT_BUTTON, self.main.select_res, self.button_residues)
        sizer.Add(self.button_residues, 0, wx.ALL, 5)

        # Boundaries
        self.button_bound = wx.Button(self, -1, "Boundaries")
        self.button_bound.SetMinSize((150, 40))
        self.Bind(wx.EVT_BUTTON, self.main.constraints, self.button_bound)
        sizer.Add(self.button_bound, 0, wx.ALL, 5)

        # Manual model seletcion
        self.button_sel = wx.Button(self, -1, "Manual Model Selection")
        self.button_sel.SetMinSize((150, 40))
        self.Bind(wx.EVT_BUTTON, self.main.manual_selection, self.button_sel)
        sizer.Add(self.button_sel, 0, wx.ALL, 5)

        # att to right sizer
        subsizer.Add(sizer, 0, wx.TOP, 50)
        mainsizer.Add(subsizer, 0, 0, 0)

        # Pack dialog
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()

        self.sync(read=True)


    def cancel(self, event): # Cancel
        self.Destroy()


    def save(self, event): # save settings
        if question('Do you want to change NESSY settings?'):
            q = self.sync(read=False)
            if q == 'error': return
            self.Destroy()

    def restore(self, event): # restore default settings
        self.main.SETTINGS = ['AICc', '500', '20', '2.0', '50.0', '0', '40'] # [Model selection, Monte Carlo, Data sets, Difference to exclude, R2 limit]
        self.sync(read=True)
        self.main.FRAMEWIDTH=2
        self.range_weight.SetValue('2')
        self.plot_format.SetSelection(0)


    def sync(self, read=True):

        #read from settings
        if read:

            # Model selection
            if self.main.SETTINGS[0] == 'AICc':
                self.aicc.SetValue(True)
                #self.alpha.SetValue(False)
            if self.main.SETTINGS[0] == 'AIC':
                self.aic.SetValue(True)
                #self.alpha.SetValue(False)
            if self.main.SETTINGS[0] == 'F':
                self.f_test.SetValue(True)
                #self.alpha.SetValue(False)
            if self.main.SETTINGS[0] == 'Chi2':
                self.chi.SetValue(True)
            if self.main.SETTINGS[0] == 'Manual':
                self.manual.SetValue(True)

            # Monte Carlo Simulation
            self.num_mc.SetValue(int(self.main.SETTINGS[1]))

            # Number of Datasets
            #self.num_datasets.SetValue(int(self.main.SETTINGS[2]))

            # Diff to exclude
            self.min_diff.SetValue(self.main.SETTINGS[3])

            # use of grid search
            if self.main.GRIDSEARCH:    self.minimisation_method.SetSelection(2)
            elif self.main.CONVERGENCE: self.minimisation_method.SetSelection(1)
            else:                       self.minimisation_method.SetSelection(0)

            # R2 minit
            #self.min_r2.SetValue(self.main.SETTINGS[4])

            # y-axis range
            self.range_plots.SetValue(str(self.main.SETTINGS[5])+' - '+str(self.main.SETTINGS[6]))

            # Output format for plot
            self.plot_format.SetSelection(self.main.PLOT2SELECTION[self.main.PLOTFORMAT])

            # exclude order
            if self.main.FITALLMODELS:
                self.exclude_order.SetSelection(1)
            else:
                self.exclude_order.SetSelection(0)

            # Create intensity plots
            self.plot_intensity.SetSelection(int(self.main.CREATE_INTENSITYPLOT))

            # Create intensity plots
            self.plot_r2eff_plots.SetSelection(int(self.main.CREATE_R2EFFPLOT))

            # fitting accuracy
            if self.main.tolerance == 1.49012e-20:   self.fit_accuracy.SetSelection(0)
            elif self.main.tolerance == 1.49012e-10: self.fit_accuracy.SetSelection(1)
            elif self.main.tolerance == 1.49012e-5:  self.fit_accuracy.SetSelection(2)
            else:                               self.fit_accuracy.SetSelection(0)

        # change settings
        else:
            # Model Selection
            if self.aicc.GetValue() == True:
                self.main.SETTINGS[0] = 'AICc'
            elif self.aic.GetValue() == True:
                self.main.SETTINGS[0] = 'AIC'
            elif self.f_test.GetValue() == True:
                self.main.SETTINGS[0] = 'F'
            elif self.chi.GetValue() == True:
                self.main.SETTINGS[0] = 'Chi2'
            elif self.manual.GetValue() == True:
                self.main.SETTINGS[0] = 'Manual'

            # Monte Carlo Simulation
            self.main.SETTINGS[1] = str(self.num_mc.GetValue())

            # Number of Datasets
            #self.main.SETTINGS[2] = str(self.num_datasets.GetValue())

            # Diff to exclude
            self.main.SETTINGS[3]= str(self.min_diff.GetValue())

            # R2 minit
            #self.main.SETTINGS[4] = str(self.min_r2.GetValue())

            # y-axis range
            y_range = str(self.range_plots.GetValue()).split('-')
            self.main.SETTINGS[5] = y_range[0].strip()
            self.main.SETTINGS[6] = y_range[1].strip()

            # Frame width for plots
            self.main.FRAMEWIDTH = float(self.range_weight.GetValue())

            # Output format for plot
            self.main.PLOTFORMAT = self.main.SELECTION2PLOT[str(self.plot_format.GetSelection())]

            # exclude order
            if self.exclude_order.GetSelection() == 1:
                self.main.FITALLMODELS = True
            else:
                self.main.FITALLMODELS = False

            # Create intensity plots
            self.main.CREATE_INTENSITYPLOT = str(self.plot_intensity.GetSelection())

            # Create intensity plots
            self.main.CREATE_R2EFFPLOT = str(self.plot_r2eff_plots.GetSelection())

            # use of grid search
            if self.minimisation_method.GetSelection() == 0:
                self.main.GRIDSEARCH = False
                self.main.CONVERGENCE = False
            elif self.minimisation_method.GetSelection() == 1:
                self.main.GRIDSEARCH = False
                self.main.CONVERGENCE = True
            elif self.minimisation_method.GetSelection() == 2:
                self.main.GRIDSEARCH = True
                self.main.CONVERGENCE = False

            # Fitting accuracy
            if self.fit_accuracy.GetSelection() == 0:        self.main.tolerance = 1.49012e-20
            elif self.fit_accuracy.GetSelection() == 1:      self.main.tolerance = 1.49012e-10
            elif self.fit_accuracy.GetSelection() == 2:      self.main.tolerance = 1.49012e-5

            # Increments for grid search
            # test if values
            try:
                r2 = 1#float(self.r2.GetValue())
                kex = float(self.kex.GetValue())
                dw = float(self.dw.GetValue())
                pb = float(self.pb.GetValue())
                phi = float(self.phi.GetValue())
            except:
                error_popup('Increment steps have to be numbers.', self)
                return 'error'
            self.main.GRID_INCREMENT = [r2, kex, dw, pb, phi]
