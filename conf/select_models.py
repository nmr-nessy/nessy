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
import wx

# NESSY modules
from conf.message import question, error_popup
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC


class Select_models(wx.Dialog):
    def __init__(self, main, *args, **kwds):
        # connect parameters
        self.main = main

        # Experiment
        self.dispmode = self.main.sel_experiment[0].GetSelection()    # 0: CPMG dispersion, 1 + 2: Spin lock dispersion, 3: H/D exchange

        # build window
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.bitmap.SetMinSize((100, 250))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # Main sizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        if self.dispmode == 0:  self.label_title = wx.StaticText(self, -1, "Select CPMG Models")
        else:                   self.label_title = wx.StaticText(self, -1, "Select R1rho Models")
        self.label_title.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.label_title, 0, wx.ALL|wx.ALIGN_LEFT, 5)

        # Model 1
        sizer_model_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_model1 = wx.StaticText(self, -1, "Model 1: no exchange")
        self.label_model1.SetMinSize((220, 17))
        sizer_model_1.Add(self.label_model1, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.model_1 = wx.ToggleButton(self, -1, "On")
        self.model_1.SetMinSize((50, 25))
        self.model_1.SetValue(True)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.model1, self.model_1)
        sizer_model_1.Add(self.model_1, 0, wx.LEFT|wx.RIGHT, 5)
        mainsizer.Add(sizer_model_1, 0, 0, 0)

        # Moddel 2
        sizer_model_2 = wx.BoxSizer(wx.HORIZONTAL)
        if self.dispmode == 0:  self.label_model2 = wx.StaticText(self, -1, "Model 2: fast exchange 2 states")
        else:                   self.label_model2 = wx.StaticText(self, -1, "Model 2: fast exchange 2 states")
        self.label_model2.SetMinSize((220, 17))
        sizer_model_2.Add(self.label_model2, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.model_2 = wx.ToggleButton(self, -1, "On")
        self.model_2.SetMinSize((50, 25))
        self.model_2.SetValue(True)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.model2, self.model_2)
        sizer_model_2.Add(self.model_2, 0, wx.LEFT|wx.RIGHT, 5)
        mainsizer.Add(sizer_model_2, 0, 0, 0)

        # Model 3
        sizer_model_3 = wx.BoxSizer(wx.HORIZONTAL)
        if self.dispmode == 0:  self.label_model3 = wx.StaticText(self, -1, "Model 3: slow exchange 2 states")
        else:                   self.label_model3 = wx.StaticText(self, -1, "Model 3: Asymmetric populations")
        self.label_model3.SetMinSize((220, 17))
        sizer_model_3.Add(self.label_model3, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.model_3 = wx.ToggleButton(self, -1, "On")
        self.Bind(wx.EVT_TOGGLEBUTTON, self.model3, self.model_3)
        self.model_3.SetMinSize((50, 25))
        self.model_3.SetValue(True)
        sizer_model_3.Add(self.model_3, 0, wx.LEFT|wx.RIGHT, 5)
        mainsizer.Add(sizer_model_3, 0, 0, 0)

        # Model 4
        sizer_model_4 = wx.BoxSizer(wx.HORIZONTAL)
        if self.dispmode == 0:  self.label_model4 = wx.StaticText(self, -1, "Model 4: fast exchange 3 states")
        else:                   self.label_model4 = wx.StaticText(self, -1, "Model 4: General expression 2 states")
        self.label_model4.SetMinSize((220, 17))
        sizer_model_4.Add(self.label_model4, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.model_4 = wx.ToggleButton(self, -1, "Off")
        self.Bind(wx.EVT_TOGGLEBUTTON, self.model4, self.model_4)
        self.model_4.SetMinSize((50, 25))
        self.model_4.SetValue(True)
        sizer_model_4.Add(self.model_4, 0, wx.LEFT|wx.RIGHT, 5)
        mainsizer.Add(sizer_model_4, 0, 0, 0)

        # Model 5
        sizer_model_5 = wx.BoxSizer(wx.HORIZONTAL)
        if self.dispmode == 0:  self.label_model5 = wx.StaticText(self, -1, "Model 5: slow exchange 3 states")
        else:                   self.label_model5 = wx.StaticText(self, -1, "Model 5: Not implemented.")
        self.label_model5.SetMinSize((220, 17))
        sizer_model_5.Add(self.label_model5, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.model_5 = wx.ToggleButton(self, -1, "Off")
        self.Bind(wx.EVT_TOGGLEBUTTON, self.model5, self.model_5)
        self.model_5.SetMinSize((50, 25))
        self.model_5.SetValue(True)
        sizer_model_5.Add(self.model_5, 0, wx.LEFT|wx.RIGHT, 5)
        mainsizer.Add(sizer_model_5, 0, 0, 0)

        # Line
        self.static_line_2 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_2, 0, wx.EXPAND|wx.ALL, 10)

        # Model 6
        sizer_model_6 = wx.BoxSizer(wx.HORIZONTAL)
        if self.dispmode == 0:  self.label_model6 = wx.StaticText(self, -1, "Model 6: 2 states, all time scales")
        else:                   self.label_model6 = wx.StaticText(self, -1, "Model 6: Not implemented.")
        self.label_model6.SetMinSize((220, 17))
        sizer_model_6.Add(self.label_model6, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.model_6 = wx.ToggleButton(self, -1, "Off")
        self.Bind(wx.EVT_TOGGLEBUTTON, self.model6, self.model_6)
        self.model_6.SetMinSize((50, 25))
        self.model_6.SetValue(True)
        sizer_model_6.Add(self.model_6, 0, wx.LEFT|wx.RIGHT, 5)
        mainsizer.Add(sizer_model_6, 0, 0, 0)

        # Line
        self.static_line_1 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_1, 0, wx.EXPAND|wx.ALL, 10)

        # Model 7
        sizer_model_7 = wx.BoxSizer(wx.HORIZONTAL)
        if self.dispmode == 0:  self.label_model7 = wx.StaticText(self, -1, "Model 7: Model 2 fitting all parameters")
        else:                   self.label_model7 = wx.StaticText(self, -1, "Model 7: Not implemented.")
        self.label_model7.SetMinSize((220, 17))
        sizer_model_7.Add(self.label_model7, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.model_7 = wx.ToggleButton(self, -1, "Off")
        self.Bind(wx.EVT_TOGGLEBUTTON, self.model7, self.model_7)
        self.model_7.SetMinSize((50, 25))
        self.model_7.SetValue(True)
        sizer_model_7.Add(self.model_7, 0, wx.LEFT|wx.RIGHT, 5)
        mainsizer.Add(sizer_model_7, 0, 0, 0)

        # Line
        self.static_line_2 = wx.StaticLine(self, -1)
        mainsizer.Add(self.static_line_2, 0, wx.EXPAND|wx.ALL, 10)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.model4, self.model_4)
        self.button_save = wx.Button(self, -1, "Save")
        self.Bind(wx.EVT_BUTTON, self.save, self.button_save)
        sizer_buttons.Add(self.button_save, 0, wx.ALL, 5)
        self.button_cancel = wx.Button(self, -1, "Cancel")
        sizer_buttons.Add(self.button_cancel, 0, wx.ALL, 5)
        self.Bind(wx.EVT_BUTTON, self.close, self.button_cancel)
        mainsizer.Add(sizer_buttons, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Pack dialog
        self.topsizer.Add(mainsizer, 0, 0, 0)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()

        self.sync()


    def close(self, event):
        self.Destroy()


    def model1(self, event):
        self.model_1.SetLabel('On')
        self.model_1.SetValue(True)


    def model2(self, event):
        if self.model_2.GetValue():
            self.model_2.SetLabel('On')
        else:
            self.model_2.SetLabel('Off')


    def model3(self, event):
        if self.model_3.GetValue():
            self.model_3.SetLabel('On')
        else:
            self.model_3.SetLabel('Off')


    def model4(self, event):
        if self.model_4.GetValue():
            self.model_4.SetLabel('On')
        else:
            self.model_4.SetLabel('Off')


    def model5(self, event):
        if self.model_5.GetValue():
            self.model_5.SetLabel('On')
        else:
            self.model_5.SetLabel('Off')


    def model6(self, event):
        if self.model_6.GetValue():
            self.model_6.SetLabel('On')
        else:
            self.model_6.SetLabel('Off')

    def model7(self, event):
        if self.model_7.GetValue():
            self.model_7.SetLabel('On')
        else:
            self.model_7.SetLabel('Off')


    def save(self, event):
        q = question('Save settings?')

        if q:
            # Model flags
            self.main.MODELS = [self.model_1.GetValue(), self.model_2.GetValue(), self.model_3.GetValue(), self.model_4.GetValue(), self.model_5.GetValue(), self.model_6.GetValue(), self.model_7.GetValue()]

            # close
            self.Destroy()


    def sync(self):
        # Enable or disable buttons
        self.model_1.SetValue(self.main.MODELS[0])
        self.model_2.SetValue(self.main.MODELS[1])
        self.model_3.SetValue(self.main.MODELS[2])
        self.model_4.SetValue(self.main.MODELS[3])
        self.model_5.SetValue(self.main.MODELS[4])
        self.model_6.SetValue(self.main.MODELS[5])
        try:
            self.model_7.SetValue(self.main.MODELS[6])
        except:
            a = 'older version of NESSY save file'

        # Change labels
        self.model2(None)
        self.model3(None)
        self.model4(None)
        self.model5(None)
        self.model6(None)
        self.model7(None)
