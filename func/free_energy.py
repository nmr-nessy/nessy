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
from scipy import sqrt, log, exp

# NESSY modules
from conf.message import error_popup, message, question
from conf.path import NESSY_PIC, IMPORT_DATA_SIDE_PIC, PAPB, dG, dG_tr



class Formula(wx.Frame):
    def __init__(self, *args, **kwds):
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

        # mainsizer
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        self.title = wx.StaticText(self, -1, "Formula")
        self.title.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        mainsizer.Add(self.title, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)

        # dG
        self.label_dg = wx.StaticText(self, -1, "Free Energy dG:")
        mainsizer.Add(self.label_dg, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5)
        self.bitmap1 = wx.StaticBitmap(self, -1, wx.Bitmap(dG, wx.BITMAP_TYPE_ANY))
        mainsizer.Add(self.bitmap1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)

        # dG*
        self.label_dg_tr = wx.StaticText(self, -1, "Free Energy of the Transition State dG* (Eyring equation):")
        mainsizer.Add(self.label_dg_tr, 0, wx.LEFT|wx.RIGHT|wx.TOP|wx.ALIGN_CENTER_VERTICAL, 5)
        self.bitmap1 = wx.StaticBitmap(self, -1, wx.Bitmap(dG_tr, wx.BITMAP_TYPE_ANY))
        mainsizer.Add(self.bitmap1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)

        # Populations
        self.label_pop = wx.StaticText(self, -1, "Populations:")
        mainsizer.Add(self.label_pop, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(PAPB, wx.BITMAP_TYPE_ANY))
        mainsizer.Add(self.bitmap, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)

        # close button
        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        mainsizer.Add(self.button_close, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)

        # Pack window
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()


    def close(self, event):
        self.Destroy()




class Free_energy(wx.Frame):
    def __init__(self, main, *args, **kwds):
        # link parameters
        self.main = main

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
        self.title = wx.StaticText(self, -1, "Free Energy Calculator")
        self.title.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        right_sizer.Add(self.title, 0, wx.ALL|wx.ALIGN_LEFT, 10)

        # Phi
        sizer_phi = wx.BoxSizer(wx.HORIZONTAL)
        self.label_phi = wx.StaticText(self, -1, "Phi [(rad/s)**2]:")
        self.label_phi.SetMinSize((110, 17))
        sizer_phi.Add(self.label_phi, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

        self.phi = wx.TextCtrl(self, -1, "")
        self.phi.SetMinSize((100, 23))
        sizer_phi.Add(self.phi, 0, wx.LEFT|wx.RIGHT, 5)
        right_sizer.Add(sizer_phi, 0, 0, 0)

        # kex
        sizer_kex = wx.BoxSizer(wx.HORIZONTAL)
        self.label_kex = wx.StaticText(self, -1, "kex [1/s]:")
        self.label_kex.SetMinSize((110, 17))
        sizer_kex.Add(self.label_kex, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

        self.kex = wx.TextCtrl(self, -1, "")
        self.kex.SetMinSize((100, 23))
        sizer_kex.Add(self.kex, 0, wx.LEFT|wx.RIGHT, 5)
        right_sizer.Add(sizer_kex, 0, 0, 0)

        # dw
        sizer_dw = wx.BoxSizer(wx.HORIZONTAL)
        self.label_dw = wx.StaticText(self, -1, "dw [rad/s]:")
        self.label_dw.SetMinSize((110, 17))
        sizer_dw.Add(self.label_dw, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)

        self.dw = wx.TextCtrl(self, -1, "")
        self.dw.SetMinSize((100, 23))
        sizer_dw.Add(self.dw, 0, wx.LEFT|wx.RIGHT, 5)
        right_sizer.Add(sizer_dw, 0, 0, 0)

        # line
        self.static_line_1 = wx.StaticLine(self, -1)
        right_sizer.Add(self.static_line_1, 0, wx.ALL|wx.EXPAND, 10)

        # Populations
        sizer_papb = wx.BoxSizer(wx.VERTICAL)
        sizer_populations = wx.BoxSizer(wx.HORIZONTAL)

        sizer_pa = wx.BoxSizer(wx.HORIZONTAL)
        self.label_pa = wx.StaticText(self, -1, "pa:")
        self.label_pa.SetMinSize((110, 17))
        sizer_pa.Add(self.label_pa, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.pa = wx.TextCtrl(self, -1, "")
        self.pa.SetMinSize((100, 23))
        sizer_pa.Add(self.pa, 0, wx.LEFT|wx.RIGHT, 5)
        sizer_papb.Add(sizer_pa, 0, 0, 0)

        sizer_pb = wx.BoxSizer(wx.HORIZONTAL)
        self.label_pb = wx.StaticText(self, -1, "pb:")
        sizer_pb.Add(self.label_pb, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.label_pb.SetMinSize((110, 17))
        self.pb = wx.TextCtrl(self, -1, "")
        self.pb.SetMinSize((100, 23))
        sizer_pb.Add(self.pb, 0, wx.LEFT|wx.RIGHT, 5)
        sizer_papb.Add(sizer_pb, 0, 0, 0)
        sizer_populations.Add(sizer_papb, 1, 0, 0)

        self.button_calc = wx.Button(self, -1, "Calculate\n(Model 2)")
        self.Bind(wx.EVT_BUTTON, self.calc_populations, self.button_calc)
        sizer_populations.Add(self.button_calc, 0, wx.LEFT|wx.RIGHT, 5)
        right_sizer.Add(sizer_populations, 1, 0, 0)

        # line
        self.static_line_2 = wx.StaticLine(self, -1)
        right_sizer.Add(self.static_line_2, 0, wx.ALL|wx.EXPAND, 10)

        # temperature
        sizer_temp = wx.BoxSizer(wx.HORIZONTAL)
        self.label_temp = wx.StaticText(self, -1, "Temperature T [K]:")
        self.label_temp.SetMinSize((110, 17))
        sizer_temp.Add(self.label_temp, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.temp = wx.TextCtrl(self, -1, "298")
        self.temp.SetMinSize((100, 23))
        sizer_temp.Add(self.temp, 0, wx.LEFT|wx.RIGHT, 5)
        right_sizer.Add(sizer_temp, 0, 0, 0)

        # line
        self.static_line_3 = wx.StaticLine(self, -1)
        right_sizer.Add(self.static_line_3, 0, wx.ALL|wx.EXPAND, 10)

        # dG
        sizer_dG = wx.BoxSizer(wx.HORIZONTAL)
        self.label_dG = wx.StaticText(self, -1, "dG [J/mol]:")
        self.label_dG.SetMinSize((110, 17))
        sizer_dG.Add(self.label_dG, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.dG = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY)
        self.dG.SetMinSize((100, 23))
        self.dG.SetBackgroundColour(wx.Colour(192, 192, 192))
        sizer_dG.Add(self.dG, 0, wx.LEFT|wx.RIGHT, 5)
        self.button_vanthoff = wx.Button(self, -1, "--> van't Hoff")
        self.button_vanthoff.SetMinSize((100, 23))
        self.Bind(wx.EVT_BUTTON, self.vanthoff, self.button_vanthoff)
        sizer_dG.Add(self.button_vanthoff, 0, wx.LEFT|wx.RIGHT, 5)
        right_sizer.Add(sizer_dG, 0, 0, 0)

        # dg_tr
        sizer_dg_tr = wx.BoxSizer(wx.HORIZONTAL)
        self.label_dg_tr = wx.StaticText(self, -1, "dG* [J/mol]:")
        self.label_dg_tr.SetMinSize((110, 17))
        sizer_dg_tr.Add(self.label_dg_tr, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 5)
        self.dG_tr = wx.TextCtrl(self, -1, "", style=wx.TE_READONLY)
        self.dG_tr.SetMinSize((100, 23))
        self.dG_tr.SetBackgroundColour(wx.Colour(192, 192, 192))
        sizer_dg_tr.Add(self.dG_tr, 0, wx.LEFT|wx.RIGHT, 5)
        right_sizer.Add(sizer_dg_tr, 0, 0, 0)

        # Buttons
        sizer_buttons = wx.BoxSizer(wx.HORIZONTAL)
        self.button_ok = wx.Button(self, -1, "Calculate")
        self.button_formula = wx.Button(self, -1, "Formula")
        self.button_close = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.calculate, self.button_ok)
        self.Bind(wx.EVT_BUTTON, self.close, self.button_close)
        self.Bind(wx.EVT_BUTTON, self.formula, self.button_formula)
        sizer_buttons.Add(self.button_ok, 0, wx.ALL, 10)
        sizer_buttons.Add(self.button_formula, 0, wx.ALL, 10)
        sizer_buttons.Add(self.button_close, 0, wx.ALL, 10)
        right_sizer.Add(sizer_buttons, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)

        # Pack window
        # Add right sizer
        subsizer.Add(right_sizer, 0, 0, 0)
        mainsizer.Add(subsizer, 0, 0, 0)

        # Pack dialog
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)
        self.Layout()


    def calc_populations(self, event):
        # evaluate import
        try:
            Phi = float(self.phi.GetValue())
        except:
            error_popup('No Phi specified!')
            return
        try:
            dw = float(self.dw.GetValue())
        except:
            error_popup('No dw specified!')
            return

        # pa
        pa = (1+sqrt(1-(4*(Phi/(dw*dw)))))/2
        self.pa.SetValue(str(pa))

        # pb
        pb = (1-sqrt(1-(4*(Phi/(dw*dw)))))/2
        self.pb.SetValue(str(pb))


    def calculate(self, event):
        # evaluate import
        try:
            pa = float(self.pa.GetValue())
        except:
            error_popup('No pa specified!')
            return
        try:
            pb = float(self.pb.GetValue())
        except:
            error_popup('No pb specified!')
            return
        try:
            temp = float(self.temp.GetValue())
        except:
            error_popup('No Temperature specified!')
            return

        # dG
        dG = 8.314472*temp*log(pa/pb)
        self.dG.SetValue(str(dG))

        # dG*
        try:
            kex = float(self.kex.GetValue())
            pb = float(self.pb.GetValue())
            kab = kex*pb

            # Eyring equation
            dG_tr = 8.314472*temp*log(temp*1.3806488*10**(-23)/(kab*6.62606957*10**(-34)))
            self.dG_tr.SetValue(str(dG_tr))
        except:
            return


    def close(self, event):
        self.Destroy()


    def formula(self, event):
        formula=Formula(None, -1, "")
        formula.Show()

    def vanthoff(self, event):
        # abort, if no dG or same
        if str(self.dG.GetValue()) == '':
            error_popup('No dG calculated!')
            return
        if str(self.dG.GetValue()) in self.main.vanthoff['dG']:
            q = question("dG value is already present in van't Hoff analysis.\n\nDo you really want to add this value?")
            if not q:
                return

        # kex has to be given
        if str(self.kex.GetValue()) == '':
            error_popup('kex is missing!')
            return

        # populations
        if str(self.pa.GetValue()) == '' or str(self.pb.GetValue()) == '':
            error_popup('Populations are missing!')
            return

        # dG
        self.main.vanthoff['dG'].append(str(self.dG.GetValue()))

        # temperature
        self.main.vanthoff['T'].append(str(self.temp.GetValue()))

        # kab
        kab = str(float(self.kex.GetValue()) / (1 + (float(self.pa.GetValue())/float(self.pb.GetValue()))))
        self.main.vanthoff['kab'].append(kab)

        # K
        K = str(exp(float(self.dG.GetValue()) / (8.314472 * float(self.temp.GetValue()))))
        self.main.vanthoff['K'].append(K)

        # message
        message("Successfully added dG value to van't Hoff analysis.")
