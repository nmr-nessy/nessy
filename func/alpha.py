#################################################################################
#                                                                               #
#   (C) 2011 Michael Bieri                                                      #
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


# Estimation of exchange regime and manual model selection

# Python modules
from scipy.optimize import leastsq
from scipy import array
try:
    import thread as _thread
except ImportError:
    import _thread
import wx

# NESSY modules
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC
from conf.message import error_popup
from curvefit.exclude import exclude
from math_fns.tests import Alpha
from math_fns.models import model_2_residuals
from func.r2eff import R2_eff as calc_R2eff
from func.pooled_variance import Pooled_variance




class Manual_model_selection(wx.Frame):
    def __init__(self, main, *args, **kwds):
        # assign parameters
        self.main = main

        # Store selected residues
        self.included_residues = self.main.INCLUDE_RES

        # running flag
        self.running = False

        # Create Window
        kwds["style"] = wx.CAPTION|wx.CLOSE_BOX
        wx.Frame.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Build Elements
        self.build()

        # Sync
        self.sync()


    def alpha(self, event):
        # starts calculation in thread.
        try:
            _thread.start_new_thread(self.alpha_calc, ())
        except:
            a = 'something wrong'


    def alpha_calc(self):
        # Calculation of alpha values

        # Abort if not enough experiments are set
        if not self.main.NUMOFDATASETS > 1:
            error_popup('Not enough experiments set to perform Alpha analysis.\n\nData recorded at two different magnetic fields are required.', self)
            return

        # no residues loaded
        if self.residue_name == []:
            error_popup('No experiment set up.\n\nAborting Alpha analysis.', self)
            return

        # Sow start analysis tab
        self.main.MainTab.SetSelection(self.main.MainTab.GetPageCount()-3)

        # Containers
        self.Rex = []

        # loop over first two experiments to calculate Rex
        for exp in range(2):
            # Calculate R2eff
            calc_R2eff(self.main, exp)

            # Calculate pooled variance
            Pooled_variance(self.main, exp)

            # fit to model 2
            self.Rex.append(self.fit(exp))

        # Calculate Alpha
        # loop over Rex
        for r in range(len(self.Rex[0])):
            # Test if Rex was calculated for both experiments
            if self.Rex[1][r][1] and self.Rex[0][r][1]:
                # Rex
                Rex1 = self.Rex[0][r][1]
                Rex2 = self.Rex[1][r][1]

                # B0
                B1 = float(self.main.B0[0].GetValue())
                B2 = float(self.main.B0[1].GetValue())

                # alpha
                if B1 < B2:
                    alpha = Alpha(B1, B2, Rex1, Rex2)
                else:
                    alpha = Alpha(B2, B1, Rex2, Rex1)

                # Residue
                res = self.Rex[0][r][0]

                # Write in Summary tab / final
                self.main.Final_grid.SetCellValue(res-1, 17, str(alpha))

                # Fill in table
                # loop over table to match residue
                for i in range(len(self.residue_name)):
                    # Compare and match residues
                    if int(self.residue_name[i].GetLabel().split()[0]) == res:
                        # Write value in manual model selection dialog
                        self.alpha[i].SetLabel(str(alpha))

        # Feedback
        wx.CallAfter(self.main.report_panel.AppendText, '\n------------------------------------------------------------------------------------------------------\nFinished Alpha analysis.\n------------------------------------------------------------------------------------------------------' )



    def build(self):
        """Build the GUI element."""
        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Mainsizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        self.header = wx.StaticText(self, -1, "Manual Model Selection")
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # Text
        self.header = wx.StaticText(self, -1, "Attention, manual model selection might introduce massive\nerrors in data analysis! It is highly recommended to not manually select models.\n\nManual model selection can be performed if chemical exchange regime\nwas determined using (Millet et al, 2000, J. Am. Chem. Soc.):\n\na = ( (B0(2) + B0(1)) / (B0(2) - B0(1)) ) * ( (Rex(2) - Rex(1)) / (Rex(2) + Rex(1)) )")
        mainsizer.Add(self.header, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # Line
        self.static_line = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line, 0, wx.EXPAND|wx.ALL, 5)

        # Calculate alpha
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, -1, "Calculate a:")
        text.SetMinSize((120, 17))
        sizer.Add(text, 0, wx.LEFT|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)

        self.button_a = wx.Button(self, -1, "Calculate")
        self.Bind(wx.EVT_BUTTON, self.alpha, self.button_a)
        sizer.Add(self.button_a, 0, 0, 0)
        mainsizer.Add(sizer, 0, 0, 0)

        # Line
        self.static_line = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line, 0, wx.EXPAND|wx.ALL, 5)

        # Entries
        self.panel_1 = wx.ScrolledWindow(self, -1, style=wx.TAB_TRAVERSAL)
        self.panel_1.SetMinSize((700, 300))
        self.panel_1.SetScrollRate(10, 10)

        sizer_panel = wx.BoxSizer(wx.VERTICAL)

        # containers
        self.residue_name = []
        self.model1 = []
        self.model2 = []
        self.model3 = []
        self.model4 = []
        self.model5 = []
        self.model6 = []
        self.alpha = []
        panel = []

        # loop over residues
        even = False
        for resi in range(0, self.main.RESNO):
            if not str(self.main.data_grid[0].GetCellValue(resi, 0)) == '':
                # create new panel
                panel.append(wx.ScrolledWindow(self.panel_1, -1, style=wx.TAB_TRAVERSAL))
                panel[len(panel)-1].SetMinSize((685, 20))
                if even:
                    panel[len(panel)-1].SetBackgroundColour(wx.Colour(255, 255, 255))
                    even = False
                else:
                    panel[len(panel)-1].SetBackgroundColour(wx.Colour(192, 192, 192))
                    even = True

                sizer = wx.BoxSizer(wx.HORIZONTAL)
                self.residue_name.append(wx.StaticText(panel[len(panel)-1], -1, str(resi+1)+' '+str(self.main.data_grid[0].GetCellValue(resi, 0))))
                self.residue_name[len(self.residue_name)-1].SetMinSize((80, 17))
                sizer.Add(self.residue_name[len(self.residue_name)-1], 0, wx.LEFT|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 5)

                # model1
                self.model1.append(wx.RadioButton(panel[len(panel)-1], -1, "Model 1"))
                sizer.Add(self.model1[len(self.model1)-1], 0, wx.LEFT|wx.RIGHT, 5)
                # model2
                self.model2.append(wx.RadioButton(panel[len(panel)-1], -1, "Model 2"))
                sizer.Add(self.model2[len(self.model2)-1], 0, wx.LEFT|wx.RIGHT, 5)
                # model3
                self.model3.append(wx.RadioButton(panel[len(panel)-1], -1, "Model 3"))
                sizer.Add(self.model3[len(self.model3)-1], 0, wx.LEFT|wx.RIGHT, 5)
                # model4
                self.model4.append(wx.RadioButton(panel[len(panel)-1], -1, "Model 4"))
                sizer.Add(self.model4[len(self.model4)-1], 0, wx.LEFT|wx.RIGHT, 5)
                # model5
                self.model5.append(wx.RadioButton(panel[len(panel)-1], -1, "Model 5"))
                sizer.Add(self.model5[len(self.model5)-1], 0, wx.LEFT|wx.RIGHT, 5)
                # model5
                self.model6.append(wx.RadioButton(panel[len(panel)-1], -1, "Model 6"))
                sizer.Add(self.model6[len(self.model6)-1], 0, wx.LEFT|wx.RIGHT, 5)

                # Alpha
                text = wx.StaticText(panel[len(panel)-1], -1, 'a = ')
                sizer.Add(text, 0, wx.LEFT|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 10)
                self.alpha.append(wx.StaticText(panel[len(panel)-1], -1, 'N/A'))
                sizer.Add(self.alpha[len(self.alpha)-1], 0, wx.LEFT|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, 0)

                # pack panel
                panel[len(panel)-1].SetSizer(sizer)
                sizer_panel.Add(panel[len(panel)-1], 0, 0, 0)

        self.panel_1.SetSizer(sizer_panel)
        mainsizer.Add(self.panel_1, 0, 0, 0)

        # Line
        self.static_line = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line, 0, wx.EXPAND|wx.ALL, 5)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_save = wx.Button(self, -1, "Save")
        self.Bind(wx.EVT_BUTTON, self.save, self.button_save)
        sizer_buttons.Add(self.button_save, 0, 0, 0)

        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        sizer_buttons.Add(self.button_close, 0, 0, 0)
        mainsizer.Add(sizer_buttons, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)

        # Pack dialog
        self.topsizer.Add(mainsizer, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()
        self.Center()


    def close(self, event):
        # Destroy dialog
        self.Destroy()


    def fit(self, exp):
        """Function to fit data to model 2."""
        # Rex container
        Rex = []       # list of [Residue, Rex]

        # loop over residues
        for residue in range(len(self.main.R2eff)):
            # create data containers
            x = []
            y = []

            # Collect x and y
            for i in range(0, self.main.NUM_OF_DATASET[exp]):
                if not self.main.R2eff[residue][i] == None:
                    y.append(float(self.main.R2eff[residue][i]))
                    x.append(float(self.main.CPMGFREQ[exp][i]))

            # abort if no data present
            if x == []:
                Rex.append([residue+1, None])
                continue

            # convert xy to arrays
            x = array(x)
            y = array(y)

            # check if exchange is expected for model 2
            if self.main.FITALLMODELS == False:
                no_exchange = exclude(y, x, self.main.SETTINGS[3], prior=False)

                # no exchnage expected
                if no_exchange:
                    Rex.append([residue+1, None])
                    continue

            # Initial guess.
            p_estimated = [self.main.INI_R2, self.main.INI_phi, self.main.INI_kex_fast]     # [R2, Phi, kex]

            # variance
            variance = self.main.R2eff_variance[exp][residue]

            # minimise
            fit = leastsq(model_2_residuals, p_estimated, args=((y), (x), variance, self.main.report_panel, False), full_output = 1, col_deriv = 1, ftol = self.main.tolerance, xtol = self.main.tolerance, maxfev=2000000)

            # Calculate Rex
            Phi = fit[0][1]
            kex = fit[0][2]
            Rex_tmp = Phi / kex

            # store Rex
            Rex.append([residue+1, Rex_tmp])

        # Return Rex list
        return Rex


    def save(self, event):
        # save selection
        selections = []

        # loop over residues
        for i in range(len(self.model1)):
            # residue
            residue = str(self.residue_name[i].GetLabel()).split()[0]

            # selection
            if self.model1[i].GetValue():
                sel = 1
            if self.model2[i].GetValue():
                sel = 2
            if self.model3[i].GetValue():
                sel = 3
            if self.model4[i].GetValue():
                sel = 4
            if self.model5[i].GetValue():
                sel = 5
            if self.model6[i].GetValue():
                sel = 6

            # store
            selections.append([residue, sel])

        # sync to main
        self.main.MANUAL_SELECTION = selections

        # Destroy dialog
        self.Destroy()


    def sync(self):
        # sync selections
        if self.main.MANUAL_SELECTION:
            # loop over selections
            for i in range(len(self.main.MANUAL_SELECTION)):
                # model
                model = self.main.MANUAL_SELECTION[i][1]

                # model 1
                if str(model) == '1':
                    self.model1[i].SetValue(True)
                # model 2
                if str(model) == '2':
                    self.model2[i].SetValue(True)
                # model 3
                if str(model) == '3':
                    self.model3[i].SetValue(True)
                # model 4
                if str(model) == '4':
                    self.model4[i].SetValue(True)
                # model 5
                if str(model) == '5':
                    self.model5[i].SetValue(True)
                # model 6
                if str(model) == '6':
                    self.model6[i].SetValue(True)

        # Sync models of calculated experiments
        # loop over residues
        for i in range(self.main.RESNO):
            # selected model
            model = str(self.main.Final_grid.GetCellValue(i, 0))

            # read, is model is not empty or 1
            if not model in ['', '1']:
                # set selection
                residue = str(i + 1)

                # find residue
                for res in range(len(self.residue_name)):
                    # match residues
                    if str(self.residue_name[res].GetLabel()).split()[0] == residue:
                        # model 2
                        if str(model) == '2':
                            self.model2[res].SetValue(True)
                        # model 3
                        if str(model) == '3':
                            self.model3[res].SetValue(True)
                        # model 4
                        if str(model) == '4':
                            self.model4[res].SetValue(True)
                        # model 5
                        if str(model) == '5':
                            self.model5[res].SetValue(True)
                        # model 6
                        if str(model) == '6':
                            self.model6[res].SetValue(True)

        # Sync alpha values
        # loop over residues
        for i in range(self.main.RESNO):
            # selected model
            a = str(self.main.Final_grid.GetCellValue(i, 17))

            # read, is model is not empty
            if not a == '':
                # set selection
                residue = str(i + 1)

                # find residue
                for res in range(len(self.residue_name)):
                    # match residues
                    if str(self.residue_name[res].GetLabel()).split()[0] == residue:
                        self.alpha[res].SetLabel(str(a))
