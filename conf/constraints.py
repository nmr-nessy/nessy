#################################################################################
#                                                                               #
#   (C) 2011 Michael Bieri                                                      #
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
import wx

# NESSY modules
from conf.message import question
from conf.filedialog import savefile
from conf.path import IMPORT_DATA_SIDE_PIC
from elements.variables import Constraints_container




class Constraints(wx.Dialog):
    def __init__(self, main, *args, **kwds):
        # connect
        self.main = main

        # Experiment
        self.dispmode = self.main.sel_experiment[0].GetSelection()    # 0: CPMG dispersion, 1 + 2: SPin lock dispersion, 3: H/D exchange

        # build window
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")

        # build content
        self.build()


    def build(self):
        # Image
        self.topsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(IMPORT_DATA_SIDE_PIC, wx.BITMAP_TYPE_ANY))
        self.topsizer.Add(self.bitmap, 0, wx.ALL, 5)

        # right sizer
        rightsizer = wx.BoxSizer(wx.VERTICAL)

        # header
        self.header = wx.StaticText(self, -1, "Specifiy Boundaries and Initial Guess")
        self.header.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        rightsizer.Add(self.header, 0, wx.ALL, 10)

        # notebook
        self.models = wx.Notebook(self, -1, style=0)

        # model 1
        self.model1()

        # model 2
        self.model2()

        # model 3
        self.model3()

        # model 4
        self.model4()

        # model 5
        self.model5()

        # model 6
        self.model6()

        # Pack notebook
        rightsizer.Add(self.models, 0, wx.ALL|wx.EXPAND, 0)

        # Buttons
        sizer_1 = wx.BoxSizer(wx.HORIZONTAL)

        # Save / cancel
        self.button_cancel = wx.Button(self, -1, "Cancel")
        self.button_save = wx.Button(self, -1, "Save")
        sizer_1.Add(self.button_cancel, 0, 0, 0)
        sizer_1.Add(self.button_save, 0, wx.RIGHT, 170)
        self.Bind(wx.EVT_BUTTON, self.cancel, self.button_cancel)
        self.Bind(wx.EVT_BUTTON, self.save, self.button_save)

        # Export / Import
        self.button_export = wx.Button(self, -1, "Export to file")
        sizer_1.Add(self.button_export, 0, 0, 0)
        self.button_import = wx.Button(self, -1, "Import from file")
        sizer_1.Add(self.button_import, 0, 0, 0)
        self.Bind(wx.EVT_BUTTON, self.export, self.button_export)
        self.Bind(wx.EVT_BUTTON, self.do_import, self.button_import)
        rightsizer.Add(sizer_1, 0, wx.TOP|wx.BOTTOM, 10)

        # Pack window
        self.topsizer.Add(rightsizer, 0, wx.RIGHT, 10)
        self.SetSizer(self.topsizer)
        self.topsizer.Fit(self)
        self.Layout()


    def do_import(self, event):
        a = ''


    def cancel(self, event):
        self.Destroy()


    def export(self, event):
        # filename
        filename = savefile('select file to save', str(self.main.proj_folder.GetValue()), 'constraints.txt', 'all files (*.*)|*', self)

        # abort if canceled
        if not filename:
            return

        # create the file
        file = open(filename, 'w')

        # Write header
        file.write('NESSY constraints and initial guess for models 1 - 6\n')
        file.write('====================================================\n\n')

        # Constraints
        file.write('Constraints:\n')

        # R2
        file.write('\n')
        file.write('R2,'+str(self.m1_r2_low.GetValue())+','+str(self.m2_r2_low.GetValue())+','+str(self.m3_r2_low.GetValue())+','+str(self.m4_r2_low.GetValue())+','+str(self.m5_r2_low.GetValue())+','+str(self.m6_r2_low.GetValue())+'\n')
        file.write('R2,'+str(self.m1_r2_up.GetValue())+','+str(self.m2_r2_up.GetValue())+','+str(self.m3_r2_up.GetValue())+','+str(self.m4_r2_up.GetValue())+','+str(self.m5_r2_up.GetValue())+','+str(self.m6_r2_up.GetValue())+'\n')
        # kex
        file.write('\n')
        file.write('kex,0,'+str(self.m2_kex_low.GetValue())+','+str(self.m3_kex_low.GetValue())+','+str(self.m4_kex_low.GetValue())+','+str(self.m5_kex_low.GetValue())+','+str(self.m6_kex_low.GetValue())+'\n')
        file.write('kex,0,'+str(self.m2_kex_up.GetValue())+','+str(self.m3_kex_up.GetValue())+','+str(self.m4_kex_up.GetValue())+','+str(self.m5_kex_up.GetValue())+','+str(self.m6_kex_up.GetValue())+'\n')
        # kex2
        file.write('\n')
        file.write('kex2,0,0,0,'+str(self.m4_kex2_low.GetValue())+','+str(self.m5_kex2_low.GetValue())+',0\n')
        file.write('kex2,0,0,0,'+str(self.m4_kex2_up.GetValue())+','+str(self.m5_kex2_up.GetValue())+',0\n')
        # Phi
        file.write('\n')
        file.write('phi,0,'+str(self.m2_phi_low.GetValue())+',0,'+str(self.m4_phi_low.GetValue())+',0,0\n')
        file.write('phi,0,'+str(self.m2_phi_up.GetValue())+',0,'+str(self.m4_phi_up.GetValue())+',0,0\n')
        # Phi2
        file.write('\n')
        file.write('phi2,0,0,0,'+str(self.m4_phi2_low.GetValue())+',0,0\n')
        file.write('phi2,0,0,0,'+str(self.m4_phi2_up.GetValue())+',0,0\n')
        # dw
        file.write('\n')
        file.write('dw,0,0,'+str(self.m3_dw_low.GetValue())+',0,'+str(self.m5_dw_low.GetValue())+','+str(self.m6_dw_low.GetValue())+'\n')
        file.write('dw,0,0,'+str(self.m3_dw_up.GetValue())+',0,'+str(self.m5_dw_up.GetValue())+','+str(self.m6_dw_up.GetValue())+'\n')
        # dw2
        file.write('\n')
        file.write('dw2,0,0,0,0'+str(self.m5_dw2_low.GetValue())+',0\n')
        file.write('dw2,0,0,0,0'+str(self.m5_dw2_up.GetValue())+',0\n')
        # pb
        file.write('\n')
        file.write('pb,0,0,'+str(self.m3_pb_low.GetValue())+',0,'+str(self.m5_pb_low.GetValue())+','+str(self.m6_pb_low.GetValue())+'\n')
        file.write('pb,0,0,'+str(self.m3_pb_up.GetValue())+',0,'+str(self.m5_pb_up.GetValue())+','+str(self.m6_pb_up.GetValue())+'\n')
        # pc
        file.write('\n')
        file.write('pc,0,0,0,0'+str(self.m5_pc_low.GetValue())+',0\n')
        file.write('pc,0,0,0,0'+str(self.m5_pc_up.GetValue())+',0\n')

        # Initial guess
        file.write('\nInitial guess:\n')

        # syncronize
        self.save(None, False)

        # R2
        file.write('R2,'+str(Constraints_container.r2)+'\n')
        # kex
        file.write('kex,'+str(Constraints_container.kex)+'\n')
        # kex2
        file.write('kex2,'+str(Constraints_container.kex2)+'\n')
        # phi
        file.write('phi,'+str(Constraints_container.phi)+'\n')
        # phi2
        file.write('phi2,'+str(Constraints_container.phi2)+'\n')
        # dw
        file.write('dw,'+str(Constraints_container.dw)+'\n')
        # dw2
        file.write('dw2,'+str(Constraints_container.dw2)+'\n')
        # pb
        file.write('pb,'+str(Constraints_container.pb)+'\n')
        # pc
        file.write('pc,'+str(Constraints_container.pc)+'\n')

        # close file
        file.close()

    def model1(self):
        # Build model 1
        # model 1 tab
        self.m1 = wx.Panel(self.models, -1)

        # tab sizer
        container = wx.BoxSizer(wx.VERTICAL)

        # Title of tab
        sizer_rhead = wx.BoxSizer(wx.HORIZONTAL)
        self.label_param = wx.StaticText(self.m1, -1, "Parameter")
        self.label_param.SetMinSize((100, 17))
        self.label_param.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_param, 0, 0, 0)

        self.label_lower = wx.StaticText(self.m1, -1, "Lower boundary")
        self.label_lower.SetMinSize((150, 17))
        self.label_lower.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_lower, 0, 0, 0)

        self.label_upper = wx.StaticText(self.m1, -1, "Upper boundary")
        self.label_upper.SetMinSize((150, 17))
        self.label_upper.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_upper, 0, 0, 0)

        self.label_guess = wx.StaticText(self.m1, -1, "Initial guess")
        self.label_guess.SetMinSize((150, 17))
        self.label_guess.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        container.Add(sizer_rhead, 0, wx.ALL, 10)
        sizer_rhead.Add(self.label_guess, 0, 0, 0)

        # Values
        # R2
        sizer_r2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_r2 = wx.StaticText(self.m1, -1, "R20 [1/s]:")
        self.label_r2.SetMinSize((100, 16))
        sizer_r2.Add(self.label_r2, 0, 0, 0)

        self.m1_r2_low = wx.TextCtrl(self.m1, -1, str(self.main.CONS_R2[0][0]))
        self.m1_r2_low.SetMinSize((150, 23))
        sizer_r2.Add(self.m1_r2_low, 0, 0, 0)

        self.m1_r2_up = wx.TextCtrl(self.m1, -1, str(self.main.CONS_R2[0][1]))
        self.m1_r2_up.SetMinSize((150, 23))
        sizer_r2.Add(self.m1_r2_up, 0, 0, 0)

        self.m1_r2_guess = wx.TextCtrl(self.m1, -1, str(self.main.INI_R2[0]))
        self.m1_r2_guess.SetMinSize((150, 23))
        sizer_r2.Add(self.m1_r2_guess, 0, 0, 0)
        container.Add(sizer_r2, 0, wx.LEFT|wx.RIGHT, 10)

        # Pack tab
        self.m1.SetSizer(container)

        # add to notebook
        self.models.AddPage(self.m1, "Model 1")


    def model2(self):
        # Build model 2
        # model 2 tab
        self.m2 = wx.Panel(self.models, -1)

        # tab sizer
        container = wx.BoxSizer(wx.VERTICAL)

        # Title of tab
        sizer_rhead = wx.BoxSizer(wx.HORIZONTAL)
        self.label_param = wx.StaticText(self.m2, -1, "Parameter")
        self.label_param.SetMinSize((100, 17))
        self.label_param.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_param, 0, 0, 0)

        self.label_lower = wx.StaticText(self.m2, -1, "Lower boundary")
        self.label_lower.SetMinSize((150, 17))
        self.label_lower.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_lower, 0, 0, 0)

        self.label_upper = wx.StaticText(self.m2, -1, "Upper boundary")
        self.label_upper.SetMinSize((150, 17))
        self.label_upper.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_upper, 0, 0, 0)

        self.label_guess = wx.StaticText(self.m2, -1, "Initial guess")
        self.label_guess.SetMinSize((150, 17))
        self.label_guess.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        container.Add(sizer_rhead, 0, wx.ALL, 10)
        sizer_rhead.Add(self.label_guess, 0, 0, 0)

        # Values
        # R2
        sizer_r2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_r2 = wx.StaticText(self.m2, -1, "R20 [1/s]:")
        self.label_r2.SetMinSize((100, 16))
        sizer_r2.Add(self.label_r2, 0, 0, 0)

        self.m2_r2_low = wx.TextCtrl(self.m2, -1, str(self.main.CONS_R2[1][0]))
        self.m2_r2_low.SetMinSize((150, 23))
        sizer_r2.Add(self.m2_r2_low, 0, 0, 0)

        self.m2_r2_up = wx.TextCtrl(self.m2, -1, str(self.main.CONS_R2[1][1]))
        self.m2_r2_up.SetMinSize((150, 23))
        sizer_r2.Add(self.m2_r2_up, 0, 0, 0)

        self.m2_r2_guess = wx.TextCtrl(self.m2, -1, str(self.main.INI_R2[1]))
        self.m2_r2_guess.SetMinSize((150, 23))
        sizer_r2.Add(self.m2_r2_guess, 0, 0, 0)
        container.Add(sizer_r2, 0, wx.LEFT|wx.RIGHT, 10)

        # Phi
        sizer_phi = wx.BoxSizer(wx.HORIZONTAL)
        self.label_phi = wx.StaticText(self.m2, -1, "Phi [ppm**2]:")
        self.label_phi.SetMinSize((100, 16))
        sizer_phi.Add(self.label_phi, 0, 0, 0)

        self.m2_phi_low = wx.TextCtrl(self.m2, -1, str(self.main.CONS_phi[1][0]))
        self.m2_phi_low.SetMinSize((150, 23))
        sizer_phi.Add(self.m2_phi_low, 0, 0, 0)

        self.m2_phi_up = wx.TextCtrl(self.m2, -1, str(self.main.CONS_phi[1][1]))
        self.m2_phi_up.SetMinSize((150, 23))
        sizer_phi.Add(self.m2_phi_up, 0, 0, 0)

        self.m2_phi_guess = wx.TextCtrl(self.m2, -1, str(self.main.INI_phi[1]))
        self.m2_phi_guess.SetMinSize((150, 23))
        sizer_phi.Add(self.m2_phi_guess, 0, 0, 0)
        container.Add(sizer_phi, 0, wx.LEFT|wx.RIGHT, 10)

        # kex
        sizer_kex = wx.BoxSizer(wx.HORIZONTAL)
        self.label_kex = wx.StaticText(self.m2, -1, "kex [1/s]:")
        self.label_kex.SetMinSize((100, 16))
        sizer_kex.Add(self.label_kex, 0, 0, 0)

        self.m2_kex_low = wx.TextCtrl(self.m2, -1, str(self.main.CONS_kex[1][0]))
        self.m2_kex_low.SetMinSize((150, 23))
        sizer_kex.Add(self.m2_kex_low, 0, 0, 0)

        self.m2_kex_up = wx.TextCtrl(self.m2, -1, str(self.main.CONS_kex[1][1]))
        self.m2_kex_up.SetMinSize((150, 23))
        sizer_kex.Add(self.m2_kex_up, 0, 0, 0)

        self.m2_kex_guess = wx.TextCtrl(self.m2, -1, str(self.main.INI_kex[1]))
        self.m2_kex_guess.SetMinSize((150, 23))
        sizer_kex.Add(self.m2_kex_guess, 0, 0, 0)
        container.Add(sizer_kex, 0, wx.LEFT|wx.RIGHT, 10)

        # Pack tab
        self.m2.SetSizer(container)

        # add to notebook
        self.models.AddPage(self.m2, "Model 2")


    def model3(self):
        # Build model 3
        # model 3 tab
        self.m3 = wx.Panel(self.models, -1)

        # tab sizer
        container = wx.BoxSizer(wx.VERTICAL)

        # Title of tab
        sizer_rhead = wx.BoxSizer(wx.HORIZONTAL)
        self.label_param = wx.StaticText(self.m3, -1, "Parameter")
        self.label_param.SetMinSize((100, 17))
        self.label_param.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_param, 0, 0, 0)

        self.label_lower = wx.StaticText(self.m3, -1, "Lower boundary")
        self.label_lower.SetMinSize((150, 17))
        self.label_lower.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_lower, 0, 0, 0)

        self.label_upper = wx.StaticText(self.m3, -1, "Upper boundary")
        self.label_upper.SetMinSize((150, 17))
        self.label_upper.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_upper, 0, 0, 0)

        self.label_guess = wx.StaticText(self.m3, -1, "Initial guess")
        self.label_guess.SetMinSize((150, 17))
        self.label_guess.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        container.Add(sizer_rhead, 0, wx.ALL, 10)
        sizer_rhead.Add(self.label_guess, 0, 0, 0)

        # Values
        # R2
        sizer_r2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_r2 = wx.StaticText(self.m3, -1, "R20 [1/s]:")
        self.label_r2.SetMinSize((100, 16))
        sizer_r2.Add(self.label_r2, 0, 0, 0)

        self.m3_r2_low = wx.TextCtrl(self.m3, -1, str(self.main.CONS_R2[2][0]))
        self.m3_r2_low.SetMinSize((150, 23))
        sizer_r2.Add(self.m3_r2_low, 0, 0, 0)

        self.m3_r2_up = wx.TextCtrl(self.m3, -1, str(self.main.CONS_R2[2][1]))
        self.m3_r2_up.SetMinSize((150, 23))
        sizer_r2.Add(self.m3_r2_up, 0, 0, 0)

        self.m3_r2_guess = wx.TextCtrl(self.m3, -1, str(self.main.INI_R2[2]))
        self.m3_r2_guess.SetMinSize((150, 23))
        sizer_r2.Add(self.m3_r2_guess, 0, 0, 0)
        container.Add(sizer_r2, 0, wx.LEFT|wx.RIGHT, 10)

        # kex
        sizer_kex = wx.BoxSizer(wx.HORIZONTAL)
        self.label_kex = wx.StaticText(self.m3, -1, "kex [1/s]:")
        self.label_kex.SetMinSize((100, 16))
        sizer_kex.Add(self.label_kex, 0, 0, 0)

        self.m3_kex_low = wx.TextCtrl(self.m3, -1, str(self.main.CONS_kex[2][0]))
        self.m3_kex_low.SetMinSize((150, 23))
        sizer_kex.Add(self.m3_kex_low, 0, 0, 0)

        self.m3_kex_up = wx.TextCtrl(self.m3, -1, str(self.main.CONS_kex[2][1]))
        self.m3_kex_up.SetMinSize((150, 23))
        sizer_kex.Add(self.m3_kex_up, 0, 0, 0)

        self.m3_kex_guess = wx.TextCtrl(self.m3, -1, str(self.main.INI_kex[2]))
        self.m3_kex_guess.SetMinSize((150, 23))
        sizer_kex.Add(self.m3_kex_guess, 0, 0, 0)
        container.Add(sizer_kex, 0, wx.LEFT|wx.RIGHT, 10)

        # dw
        sizer_dw = wx.BoxSizer(wx.HORIZONTAL)
        self.label_dw = wx.StaticText(self.m3, -1, "dw [ppm]:")
        self.label_dw.SetMinSize((100, 16))
        sizer_dw.Add(self.label_dw, 0, 0, 0)

        self.m3_dw_low = wx.TextCtrl(self.m3, -1, str(self.main.CONS_dw[2][0]))
        self.m3_dw_low.SetMinSize((150, 23))
        sizer_dw.Add(self.m3_dw_low, 0, 0, 0)

        self.m3_dw_up = wx.TextCtrl(self.m3, -1, str(self.main.CONS_dw[2][1]))
        self.m3_dw_up.SetMinSize((150, 23))
        sizer_dw.Add(self.m3_dw_up, 0, 0, 0)

        self.m3_dw_guess = wx.TextCtrl(self.m3, -1, str(self.main.INI_dw[2]))
        self.m3_dw_guess.SetMinSize((150, 23))
        sizer_dw.Add(self.m3_dw_guess, 0, 0, 0)
        container.Add(sizer_dw, 0, wx.LEFT|wx.RIGHT, 10)

        # pb
        sizer_pb = wx.BoxSizer(wx.HORIZONTAL)
        self.label_pb = wx.StaticText(self.m3, -1, "pb:")
        self.label_pb.SetMinSize((100, 16))
        sizer_pb.Add(self.label_pb, 0, 0, 0)

        self.m3_pb_low = wx.TextCtrl(self.m3, -1, str(self.main.CONS_pb[2][0]))
        self.m3_pb_low.SetMinSize((150, 23))
        sizer_pb.Add(self.m3_pb_low, 0, 0, 0)

        self.m3_pb_up = wx.TextCtrl(self.m3, -1, str(self.main.CONS_pb[2][1]))
        self.m3_pb_up.SetMinSize((150, 23))
        sizer_pb.Add(self.m3_pb_up, 0, 0, 0)

        self.m3_pb_guess = wx.TextCtrl(self.m3, -1, str(self.main.INI_pb[2]))
        self.m3_pb_guess.SetMinSize((150, 23))
        sizer_pb.Add(self.m3_pb_guess, 0, 0, 0)
        container.Add(sizer_pb, 0, wx.LEFT|wx.RIGHT, 10)

        # Pack tab
        self.m3.SetSizer(container)

        # add to notebook
        if self.dispmode == 0:  self.models.AddPage(self.m3, "Model 3")
        else:                   self.models.AddPage(self.m3, "Models 3+4")


    def model4(self):
        # Build model 4
        # model 4 tab
        self.m4 = wx.Panel(self.models, -1)

        # tab sizer
        container = wx.BoxSizer(wx.VERTICAL)

        # Title of tab
        sizer_rhead = wx.BoxSizer(wx.HORIZONTAL)
        self.label_param = wx.StaticText(self.m4, -1, "Parameter")
        self.label_param.SetMinSize((100, 17))
        self.label_param.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_param, 0, 0, 0)

        self.label_lower = wx.StaticText(self.m4, -1, "Lower boundary")
        self.label_lower.SetMinSize((150, 17))
        self.label_lower.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_lower, 0, 0, 0)

        self.label_upper = wx.StaticText(self.m4, -1, "Upper boundary")
        self.label_upper.SetMinSize((150, 17))
        self.label_upper.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_upper, 0, 0, 0)

        self.label_guess = wx.StaticText(self.m4, -1, "Initial guess")
        self.label_guess.SetMinSize((150, 17))
        self.label_guess.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        container.Add(sizer_rhead, 0, wx.ALL, 10)
        sizer_rhead.Add(self.label_guess, 0, 0, 0)

        # Values
        # R2
        sizer_r2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_r2 = wx.StaticText(self.m4, -1, "R20 [1/s]:")
        self.label_r2.SetMinSize((100, 16))
        sizer_r2.Add(self.label_r2, 0, 0, 0)

        self.m4_r2_low = wx.TextCtrl(self.m4, -1, str(self.main.CONS_R2[3][0]))
        self.m4_r2_low.SetMinSize((150, 23))
        sizer_r2.Add(self.m4_r2_low, 0, 0, 0)

        self.m4_r2_up = wx.TextCtrl(self.m4, -1, str(self.main.CONS_R2[3][1]))
        self.m4_r2_up.SetMinSize((150, 23))
        sizer_r2.Add(self.m4_r2_up, 0, 0, 0)

        self.m4_r2_guess = wx.TextCtrl(self.m4, -1, str(self.main.INI_R2[3]))
        self.m4_r2_guess.SetMinSize((150, 23))
        sizer_r2.Add(self.m4_r2_guess, 0, 0, 0)
        container.Add(sizer_r2, 0, wx.LEFT|wx.RIGHT, 10)

        # Phi
        sizer_phi = wx.BoxSizer(wx.HORIZONTAL)
        self.label_phi = wx.StaticText(self.m4, -1, "Phi [ppm**2]:")
        self.label_phi.SetMinSize((100, 16))
        sizer_phi.Add(self.label_phi, 0, 0, 0)

        self.m4_phi_low = wx.TextCtrl(self.m4, -1, str(self.main.CONS_phi[3][0]))
        self.m4_phi_low.SetMinSize((150, 23))
        sizer_phi.Add(self.m4_phi_low, 0, 0, 0)

        self.m4_phi_up = wx.TextCtrl(self.m4, -1, str(self.main.CONS_phi[3][1]))
        self.m4_phi_up.SetMinSize((150, 23))
        sizer_phi.Add(self.m4_phi_up, 0, 0, 0)

        self.m4_phi_guess = wx.TextCtrl(self.m4, -1, str(self.main.INI_phi[3]))
        self.m4_phi_guess.SetMinSize((150, 23))
        sizer_phi.Add(self.m4_phi_guess, 0, 0, 0)
        container.Add(sizer_phi, 0, wx.LEFT|wx.RIGHT, 10)

        # kex
        sizer_kex = wx.BoxSizer(wx.HORIZONTAL)
        self.label_kex = wx.StaticText(self.m4, -1, "kex [1/s]:")
        self.label_kex.SetMinSize((100, 16))
        sizer_kex.Add(self.label_kex, 0, 0, 0)

        self.m4_kex_low = wx.TextCtrl(self.m4, -1, str(self.main.CONS_kex[3][0]))
        self.m4_kex_low.SetMinSize((150, 23))
        sizer_kex.Add(self.m4_kex_low, 0, 0, 0)

        self.m4_kex_up = wx.TextCtrl(self.m4, -1, str(self.main.CONS_kex[3][1]))
        self.m4_kex_up.SetMinSize((150, 23))
        sizer_kex.Add(self.m4_kex_up, 0, 0, 0)

        self.m4_kex_guess = wx.TextCtrl(self.m4, -1, str(self.main.INI_kex[3]))
        self.m4_kex_guess.SetMinSize((150, 23))
        sizer_kex.Add(self.m4_kex_guess, 0, 0, 0)
        container.Add(sizer_kex, 0, wx.LEFT|wx.RIGHT, 10)

        # phi2
        sizer_phi2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_phi2 = wx.StaticText(self.m4, -1, "phi2 [ppm**2]:")
        self.label_phi2.SetMinSize((100, 16))
        sizer_phi2.Add(self.label_phi2, 0, 0, 0)

        self.m4_phi2_low = wx.TextCtrl(self.m4, -1, str(self.main.CONS_phi2[3][0]))
        self.m4_phi2_low.SetMinSize((150, 23))
        sizer_phi2.Add(self.m4_phi2_low, 0, 0, 0)

        self.m4_phi2_up = wx.TextCtrl(self.m4, -1, str(self.main.CONS_phi2[3][1]))
        self.m4_phi2_up.SetMinSize((150, 23))
        sizer_phi2.Add(self.m4_phi2_up, 0, 0, 0)

        self.m4_phi2_guess = wx.TextCtrl(self.m4, -1, str(self.main.INI_phi2[3]))
        self.m4_phi2_guess.SetMinSize((150, 23))
        sizer_phi2.Add(self.m4_phi2_guess, 0, 0, 0)
        container.Add(sizer_phi2, 0, wx.LEFT|wx.RIGHT, 10)

        # kex2
        sizer_kex2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_kex2 = wx.StaticText(self.m4, -1, "kex2 [1/s]:")
        self.label_kex2.SetMinSize((100, 16))
        sizer_kex2.Add(self.label_kex2, 0, 0, 0)

        self.m4_kex2_low = wx.TextCtrl(self.m4, -1, str(self.main.CONS_kex2[3][0]))
        self.m4_kex2_low.SetMinSize((150, 23))
        sizer_kex2.Add(self.m4_kex2_low, 0, 0, 0)

        self.m4_kex2_up = wx.TextCtrl(self.m4, -1, str(self.main.CONS_kex2[3][1]))
        self.m4_kex2_up.SetMinSize((150, 23))
        sizer_kex2.Add(self.m4_kex2_up, 0, 0, 0)

        self.m4_kex2_guess = wx.TextCtrl(self.m4, -1, str(self.main.INI_kex2[3]))
        self.m4_kex2_guess.SetMinSize((150, 23))
        sizer_kex2.Add(self.m4_kex2_guess, 0, 0, 0)
        container.Add(sizer_kex2, 0, wx.LEFT|wx.RIGHT, 10)

        # Pack tab
        self.m4.SetSizer(container)

        # add to notebook
        if self.dispmode == 0: self.models.AddPage(self.m4, "Model 4")


    def model5(self):
        # Build model 5
        # model 5 tab
        self.m5 = wx.Panel(self.models, -1)

        # tab sizer
        container = wx.BoxSizer(wx.VERTICAL)

        # Title of tab
        sizer_rhead = wx.BoxSizer(wx.HORIZONTAL)
        self.label_param = wx.StaticText(self.m5, -1, "Parameter")
        self.label_param.SetMinSize((100, 17))
        self.label_param.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_param, 0, 0, 0)

        self.label_lower = wx.StaticText(self.m5, -1, "Lower boundary")
        self.label_lower.SetMinSize((150, 17))
        self.label_lower.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_lower, 0, 0, 0)

        self.label_upper = wx.StaticText(self.m5, -1, "Upper boundary")
        self.label_upper.SetMinSize((150, 17))
        self.label_upper.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_upper, 0, 0, 0)

        self.label_guess = wx.StaticText(self.m5, -1, "Initial guess")
        self.label_guess.SetMinSize((150, 17))
        self.label_guess.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        container.Add(sizer_rhead, 0, wx.ALL, 10)
        sizer_rhead.Add(self.label_guess, 0, 0, 0)

        # Values
        # R2
        sizer_r2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_r2 = wx.StaticText(self.m5, -1, "R20 [1/s]:")
        self.label_r2.SetMinSize((100, 16))
        sizer_r2.Add(self.label_r2, 0, 0, 0)

        self.m5_r2_low = wx.TextCtrl(self.m5, -1, str(self.main.CONS_R2[4][0]))
        self.m5_r2_low.SetMinSize((150, 23))
        sizer_r2.Add(self.m5_r2_low, 0, 0, 0)

        self.m5_r2_up = wx.TextCtrl(self.m5, -1, str(self.main.CONS_R2[4][1]))
        self.m5_r2_up.SetMinSize((150, 23))
        sizer_r2.Add(self.m5_r2_up, 0, 0, 0)

        self.m5_r2_guess = wx.TextCtrl(self.m5, -1, str(self.main.INI_R2[4]))
        self.m5_r2_guess.SetMinSize((150, 23))
        sizer_r2.Add(self.m5_r2_guess, 0, 0, 0)
        container.Add(sizer_r2, 0, wx.LEFT|wx.RIGHT, 10)

        # kex
        sizer_kex = wx.BoxSizer(wx.HORIZONTAL)
        self.label_kex = wx.StaticText(self.m5, -1, "kex [1/s]:")
        self.label_kex.SetMinSize((100, 16))
        sizer_kex.Add(self.label_kex, 0, 0, 0)

        self.m5_kex_low = wx.TextCtrl(self.m5, -1, str(self.main.CONS_kex[4][0]))
        self.m5_kex_low.SetMinSize((150, 23))
        sizer_kex.Add(self.m5_kex_low, 0, 0, 0)

        self.m5_kex_up = wx.TextCtrl(self.m5, -1, str(self.main.CONS_kex[4][1]))
        self.m5_kex_up.SetMinSize((150, 23))
        sizer_kex.Add(self.m5_kex_up, 0, 0, 0)

        self.m5_kex_guess = wx.TextCtrl(self.m5, -1, str(self.main.INI_kex[4]))
        self.m5_kex_guess.SetMinSize((150, 23))
        sizer_kex.Add(self.m5_kex_guess, 0, 0, 0)
        container.Add(sizer_kex, 0, wx.LEFT|wx.RIGHT, 10)

        # dw
        sizer_dw = wx.BoxSizer(wx.HORIZONTAL)
        self.label_dw = wx.StaticText(self.m5, -1, "dw [ppm]:")
        self.label_dw.SetMinSize((100, 16))
        sizer_dw.Add(self.label_dw, 0, 0, 0)

        self.m5_dw_low = wx.TextCtrl(self.m5, -1, str(self.main.CONS_dw[4][0]))
        self.m5_dw_low.SetMinSize((150, 23))
        sizer_dw.Add(self.m5_dw_low, 0, 0, 0)

        self.m5_dw_up = wx.TextCtrl(self.m5, -1, str(self.main.CONS_dw[4][1]))
        self.m5_dw_up.SetMinSize((150, 23))
        sizer_dw.Add(self.m5_dw_up, 0, 0, 0)

        self.m5_dw_guess = wx.TextCtrl(self.m5, -1, str(self.main.INI_dw[4]))
        self.m5_dw_guess.SetMinSize((150, 23))
        sizer_dw.Add(self.m5_dw_guess, 0, 0, 0)
        container.Add(sizer_dw, 0, wx.LEFT|wx.RIGHT, 10)

        # pb
        sizer_pb = wx.BoxSizer(wx.HORIZONTAL)
        self.label_pb = wx.StaticText(self.m5, -1, "pb:")
        self.label_pb.SetMinSize((100, 16))
        sizer_pb.Add(self.label_pb, 0, 0, 0)

        self.m5_pb_low = wx.TextCtrl(self.m5, -1, str(self.main.CONS_pb[4][0]))
        self.m5_pb_low.SetMinSize((150, 23))
        sizer_pb.Add(self.m5_pb_low, 0, 0, 0)

        self.m5_pb_up = wx.TextCtrl(self.m5, -1, str(self.main.CONS_pb[4][1]))
        self.m5_pb_up.SetMinSize((150, 23))
        sizer_pb.Add(self.m5_pb_up, 0, 0, 0)

        self.m5_pb_guess = wx.TextCtrl(self.m5, -1, str(self.main.INI_pb[4]))
        self.m5_pb_guess.SetMinSize((150, 23))
        sizer_pb.Add(self.m5_pb_guess, 0, 0, 0)
        container.Add(sizer_pb, 0, wx.LEFT|wx.RIGHT, 10)

        # kex2
        sizer_kex2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_kex2 = wx.StaticText(self.m5, -1, "kex2 [1/s]:")
        self.label_kex2.SetMinSize((100, 16))
        sizer_kex2.Add(self.label_kex2, 0, 0, 0)

        self.m5_kex2_low = wx.TextCtrl(self.m5, -1, str(self.main.CONS_kex2[4][0]))
        self.m5_kex2_low.SetMinSize((150, 23))
        sizer_kex2.Add(self.m5_kex2_low, 0, 0, 0)

        self.m5_kex2_up = wx.TextCtrl(self.m5, -1, str(self.main.CONS_kex2[4][1]))
        self.m5_kex2_up.SetMinSize((150, 23))
        sizer_kex2.Add(self.m5_kex2_up, 0, 0, 0)

        self.m5_kex2_guess = wx.TextCtrl(self.m5, -1, str(self.main.INI_kex2[4]))
        self.m5_kex2_guess.SetMinSize((150, 23))
        sizer_kex2.Add(self.m5_kex2_guess, 0, 0, 0)
        container.Add(sizer_kex2, 0, wx.LEFT|wx.RIGHT, 10)

        # dw2
        sizer_dw2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_dw2 = wx.StaticText(self.m5, -1, "dw2 [ppm]:")
        self.label_dw2.SetMinSize((100, 16))
        sizer_dw2.Add(self.label_dw2, 0, 0, 0)

        self.m5_dw2_low = wx.TextCtrl(self.m5, -1, str(self.main.CONS_dw2[4][0]))
        self.m5_dw2_low.SetMinSize((150, 23))
        sizer_dw2.Add(self.m5_dw2_low, 0, 0, 0)

        self.m5_dw2_up = wx.TextCtrl(self.m5, -1, str(self.main.CONS_dw2[4][1]))
        self.m5_dw2_up.SetMinSize((150, 23))
        sizer_dw2.Add(self.m5_dw2_up, 0, 0, 0)

        self.m5_dw2_guess = wx.TextCtrl(self.m5, -1, str(self.main.INI_dw2[4]))
        self.m5_dw2_guess.SetMinSize((150, 23))
        sizer_dw2.Add(self.m5_dw2_guess, 0, 0, 0)
        container.Add(sizer_dw2, 0, wx.LEFT|wx.RIGHT, 10)

        # pc
        sizer_pc = wx.BoxSizer(wx.HORIZONTAL)
        self.label_pc = wx.StaticText(self.m5, -1, "pc:")
        self.label_pc.SetMinSize((100, 16))
        sizer_pc.Add(self.label_pc, 0, 0, 0)

        self.m5_pc_low = wx.TextCtrl(self.m5, -1, str(self.main.CONS_pc[4][0]))
        self.m5_pc_low.SetMinSize((150, 23))
        sizer_pc.Add(self.m5_pc_low, 0, 0, 0)

        self.m5_pc_up = wx.TextCtrl(self.m5, -1, str(self.main.CONS_pc[4][1]))
        self.m5_pc_up.SetMinSize((150, 23))
        sizer_pc.Add(self.m5_pc_up, 0, 0, 0)

        self.m5_pc_guess = wx.TextCtrl(self.m5, -1, str(self.main.INI_pc[4]))
        self.m5_pc_guess.SetMinSize((150, 23))
        sizer_pc.Add(self.m5_pc_guess, 0, 0, 0)
        container.Add(sizer_pc, 0, wx.LEFT|wx.RIGHT, 10)

        # Pack tab
        self.m5.SetSizer(container)

        # add to notebook
        if self.dispmode == 0: self.models.AddPage(self.m5, "Model 5")


    def model6(self):
        # Build model 6
        # model 6 tab
        self.m6 = wx.Panel(self.models, -1)

        # tab sizer
        container = wx.BoxSizer(wx.VERTICAL)

        # Title of tab
        sizer_rhead = wx.BoxSizer(wx.HORIZONTAL)
        self.label_param = wx.StaticText(self.m6, -1, "Parameter")
        self.label_param.SetMinSize((100, 17))
        self.label_param.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_param, 0, 0, 0)

        self.label_lower = wx.StaticText(self.m6, -1, "Lower boundary")
        self.label_lower.SetMinSize((150, 17))
        self.label_lower.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_lower, 0, 0, 0)

        self.label_upper = wx.StaticText(self.m6, -1, "Upper boundary")
        self.label_upper.SetMinSize((150, 17))
        self.label_upper.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer_rhead.Add(self.label_upper, 0, 0, 0)

        self.label_guess = wx.StaticText(self.m6, -1, "Initial guess")
        self.label_guess.SetMinSize((150, 17))
        self.label_guess.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        container.Add(sizer_rhead, 0, wx.ALL, 10)
        sizer_rhead.Add(self.label_guess, 0, 0, 0)

        # Values
        # R2
        sizer_r2 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_r2 = wx.StaticText(self.m6, -1, "R20 [1/s]:")
        self.label_r2.SetMinSize((100, 16))
        sizer_r2.Add(self.label_r2, 0, 0, 0)

        self.m6_r2_low = wx.TextCtrl(self.m6, -1, str(self.main.CONS_R2[5][0]))
        self.m6_r2_low.SetMinSize((150, 23))
        sizer_r2.Add(self.m6_r2_low, 0, 0, 0)

        self.m6_r2_up = wx.TextCtrl(self.m6, -1, str(self.main.CONS_R2[5][1]))
        self.m6_r2_up.SetMinSize((150, 23))
        sizer_r2.Add(self.m6_r2_up, 0, 0, 0)

        self.m6_r2_guess = wx.TextCtrl(self.m6, -1, str(self.main.INI_R2[5]))
        self.m6_r2_guess.SetMinSize((150, 23))
        sizer_r2.Add(self.m6_r2_guess, 0, 0, 0)
        container.Add(sizer_r2, 0, wx.LEFT|wx.RIGHT, 10)

        # kex
        sizer_kex = wx.BoxSizer(wx.HORIZONTAL)
        self.label_kex = wx.StaticText(self.m6, -1, "kex [1/s]:")
        self.label_kex.SetMinSize((100, 16))
        sizer_kex.Add(self.label_kex, 0, 0, 0)

        self.m6_kex_low = wx.TextCtrl(self.m6, -1, str(self.main.CONS_kex[5][0]))
        self.m6_kex_low.SetMinSize((150, 23))
        sizer_kex.Add(self.m6_kex_low, 0, 0, 0)

        self.m6_kex_up = wx.TextCtrl(self.m6, -1, str(self.main.CONS_kex[5][1]))
        self.m6_kex_up.SetMinSize((150, 23))
        sizer_kex.Add(self.m6_kex_up, 0, 0, 0)

        self.m6_kex_guess = wx.TextCtrl(self.m6, -1, str(self.main.INI_kex[5]))
        self.m6_kex_guess.SetMinSize((150, 23))
        sizer_kex.Add(self.m6_kex_guess, 0, 0, 0)
        container.Add(sizer_kex, 0, wx.LEFT|wx.RIGHT, 10)

        # dw
        sizer_dw = wx.BoxSizer(wx.HORIZONTAL)
        self.label_dw = wx.StaticText(self.m6, -1, "dw [ppm]:")
        self.label_dw.SetMinSize((100, 16))
        sizer_dw.Add(self.label_dw, 0, 0, 0)

        self.m6_dw_low = wx.TextCtrl(self.m6, -1, str(self.main.CONS_dw[5][0]))
        self.m6_dw_low.SetMinSize((150, 23))
        sizer_dw.Add(self.m6_dw_low, 0, 0, 0)

        self.m6_dw_up = wx.TextCtrl(self.m6, -1, str(self.main.CONS_dw[5][1]))
        self.m6_dw_up.SetMinSize((150, 23))
        sizer_dw.Add(self.m6_dw_up, 0, 0, 0)

        self.m6_dw_guess = wx.TextCtrl(self.m6, -1, str(self.main.INI_dw[5]))
        self.m6_dw_guess.SetMinSize((150, 23))
        sizer_dw.Add(self.m6_dw_guess, 0, 0, 0)
        container.Add(sizer_dw, 0, wx.LEFT|wx.RIGHT, 10)

        # pb
        sizer_pb = wx.BoxSizer(wx.HORIZONTAL)
        self.label_pb = wx.StaticText(self.m6, -1, "pb:")
        self.label_pb.SetMinSize((100, 16))
        sizer_pb.Add(self.label_pb, 0, 0, 0)

        self.m6_pb_low = wx.TextCtrl(self.m6, -1, str(self.main.CONS_pb[5][0]))
        self.m6_pb_low.SetMinSize((150, 23))
        sizer_pb.Add(self.m6_pb_low, 0, 0, 0)

        self.m6_pb_up = wx.TextCtrl(self.m6, -1, str(self.main.CONS_pb[5][1]))
        self.m6_pb_up.SetMinSize((150, 23))
        sizer_pb.Add(self.m6_pb_up, 0, 0, 0)

        self.m6_pb_guess = wx.TextCtrl(self.m6, -1, str(self.main.INI_pb[5]))
        self.m6_pb_guess.SetMinSize((150, 23))
        sizer_pb.Add(self.m6_pb_guess, 0, 0, 0)
        container.Add(sizer_pb, 0, wx.LEFT|wx.RIGHT, 10)

        # Pack tab
        self.m6.SetSizer(container)

        # add to notebook
        if self.dispmode == 0: self.models.AddPage(self.m6, "Models 6 and 7")


    def save(self, event, close=True):
        # Question
        if close:
            q = question('Do you want to save changes?\n\nChanging initial guess and constraints might influence final results.', self)
            if not q:
                return

        # Initial guess
        # R2
        self.main.INI_R2 = [float(self.m1_r2_guess.GetValue()), float(self.m2_r2_guess.GetValue()), float(self.m3_r2_guess.GetValue()), float(self.m4_r2_guess.GetValue()), float(self.m5_r2_guess.GetValue()), float(self.m6_r2_guess.GetValue())]
        # kex
        self.main.INI_kex = [0, float(self.m2_kex_guess.GetValue()), float(self.m3_kex_guess.GetValue()), float(self.m4_kex_guess.GetValue()), float(self.m5_kex_guess.GetValue()), float(self.m6_kex_guess.GetValue())]
        self.main.INI_kex2 = [0, 0, 0, float(self.m4_kex2_guess.GetValue()), float(self.m5_kex2_guess.GetValue()), 0]
        # Phi
        self.main.INI_phi = [0, float(self.m2_phi_guess.GetValue()), 0, float(self.m4_phi_guess.GetValue()), 0, 0]
        self.main.INI_phi2 = [0, 0, 0, float(self.m4_phi2_guess.GetValue()), 0, 0]
        # dw
        self.main.INI_dw = [0, 0, float(self.m3_dw_guess.GetValue()), 0, float(self.m5_dw_guess.GetValue()), float(self.m6_dw_guess.GetValue())]
        self.main.INI_dw2 = [0, 0, 0, 0, float(self.m5_dw2_guess.GetValue()), 0]
        # pb
        self.main.INI_pb = [0, 0, float(self.m3_pb_guess.GetValue()), 0, float(self.m5_pb_guess.GetValue()), float(self.m6_pb_guess.GetValue())]
        # pc
        self.main.INI_pc = [0, 0, 0, 0, float(self.m5_pc_guess.GetValue()), 0]

        # Constraints
        self.main.CONS_R2 = [[float(self.m1_r2_low.GetValue()), float(self.m1_r2_up.GetValue())], [float(self.m2_r2_low.GetValue()), float(self.m2_r2_up.GetValue())], [float(self.m3_r2_low.GetValue()), float(self.m3_r2_up.GetValue())], [float(self.m4_r2_low.GetValue()), float(self.m4_r2_up.GetValue())], [float(self.m5_r2_low.GetValue()), float(self.m5_r2_up.GetValue())], [float(self.m6_r2_low.GetValue()), float(self.m6_r2_up.GetValue())]]
        self.main.CONS_kex = [[0, 0], [float(self.m2_kex_low.GetValue()), float(self.m2_kex_up.GetValue())], [float(self.m3_kex_low.GetValue()), float(self.m3_kex_up.GetValue())], [float(self.m4_kex_low.GetValue()), float(self.m4_kex_up.GetValue())], [float(self.m5_kex_low.GetValue()), float(self.m5_kex_up.GetValue())], [float(self.m6_kex_low.GetValue()), float(self.m6_kex_up.GetValue())]]
        self.main.CONS_kex2 = [[0, 0], [0, 0], [0, 0], [float(self.m4_kex2_low.GetValue()), float(self.m4_kex2_up.GetValue())], [float(self.m5_kex2_low.GetValue()), float(self.m5_kex2_up.GetValue())], [0, 0]]
        self.main.CONS_phi = [[0, 0], [float(self.m2_phi_low.GetValue()), float(self.m2_phi_up.GetValue())], [0, 0], [float(self.m4_phi_low.GetValue()), float(self.m4_phi_up.GetValue())], [0, 0], [0, 0]]
        self.main.CONS_phi2 = [[0, 0], [0, 0], [0, 0], [float(self.m4_phi2_low.GetValue()), float(self.m4_phi2_up.GetValue())], [0, 0], [0, 0]]
        self.main.CONS_dw = [[0, 0], [0, 0], [float(self.m3_dw_low.GetValue()), float(self.m3_dw_up.GetValue())], [0, 0], [float(self.m5_dw_low.GetValue()), float(self.m5_dw_up.GetValue())], [float(self.m6_dw_low.GetValue()), float(self.m6_dw_up.GetValue())]]
        self.main.CONS_dw2 = [[0, 0], [0, 0], [0, 0], [0, 0], [float(self.m5_dw2_low.GetValue()), float(self.m5_dw2_up.GetValue())], [0, 0]]
        self.main.CONS_pb = [[0, 0], [0, 0], [float(self.m3_pb_low.GetValue()), float(self.m3_pb_up.GetValue())], [0, 0], [float(self.m5_pb_low.GetValue()), float(self.m5_pb_up.GetValue())], [float(self.m6_pb_low.GetValue()), float(self.m6_pb_up.GetValue())]]
        self.main.CONS_pc = [[0, 0], [0, 0], [0, 0], [0, 0], [float(self.m5_pc_low.GetValue()), float(self.m5_pc_up.GetValue())], [0, 0]]

        # Fill up constraints container
        Constraints_container.r2 = self.main.CONS_R2
        Constraints_container.kex = self.main.CONS_kex
        Constraints_container.kex2 = self.main.CONS_kex2
        Constraints_container.phi = self.main.CONS_phi
        Constraints_container.phi2 = self.main.CONS_phi2
        Constraints_container.dw = self.main.CONS_dw
        Constraints_container.dw2 = self.main.CONS_dw2
        Constraints_container.pb = self.main.CONS_pb
        Constraints_container.pc = self.main.CONS_pc

        # Close dialog
        if close:
            self.Destroy()
