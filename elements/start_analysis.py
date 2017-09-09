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
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  021110307  USA   #
#                                                                               #
#################################################################################


# Python modules
import wx
from os import sep

# NESSY modules
from conf.path import COLLECT_PIC



def build_start_analysis(self):
        """Build start_analysis data notebook GUI element"""
        self.start = wx.Panel(self.MainTab, -1)

        # Sizers
        start_main = wx.BoxSizer(wx.HORIZONTAL)
        left_box = wx.BoxSizer(wx.VERTICAL)
        right_box = wx.BoxSizer(wx.VERTICAL)

        #Start Analysis Tab
        self.label_2 = wx.StaticText(self.start, -1, _("Analysis:"))
        self.label_2.SetMinSize((300, 25))
        self.label_2.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        left_box.Add(self.label_2, -1, 0, 0)

        # collect data
        collect_box = wx.BoxSizer(wx.HORIZONTAL)
        self.label_3 = wx.StaticText(self.start, -1, _("Evaluate Data:    "), style=wx.ALIGN_CENTRE)
        self.label_3.SetMinSize((150, 24))
        collect_box.Add(self.label_3, 0, wx.ADJUST_MINSIZE, 0)
        self.getdata_button = wx.BitmapButton(self.start, 0, wx.Bitmap(COLLECT_PIC, wx.BITMAP_TYPE_ANY))
        self.getdata_button.SetMinSize((28, 28))
        self.Bind(wx.EVT_BUTTON, self.get_data, self.getdata_button)
        collect_box.Add(self.getdata_button, 0, 0, 0)
        # Pack box
        left_box.Add(collect_box, 0, 0, 0)
        self.label_7 = wx.StaticText(self.start, -1, _("Status Summary\n"))
        left_box.Add(self.label_7, 0, wx.TOP, 5)

        # Summary
        self.text_ctrl_1 = wx.TextCtrl(self.start, -1, "", style=wx.TE_MULTILINE|wx.TE_READONLY)
        self.text_ctrl_1.SetMinSize((295, 260))
        self.text_ctrl_1.SetBackgroundColour(wx.Colour(192, 192, 192))
        self.text_ctrl_1.SetForegroundColour('Black')
        left_box.Add(self.text_ctrl_1, 0, 0, 0)

        self.start_calc = wx.Button(self.start, -1, _("Start Calculation"))
        self.Bind(wx.EVT_BUTTON, self.startcalc, self.start_calc)
        left_box.Add(self.start_calc, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 10)

        # Status field
        self.running_panel = wx.Panel(self.start, -1)
        self.running_panel.SetMinSize((295, 60))
        self.running_panel.SetBackgroundColour(wx.Colour(232, 232, 232))
        checkrun = wx.BoxSizer(wx.HORIZONTAL)
        self.checkrun_label = wx.StaticText(self.running_panel, -1, _("waiting..."), style=wx.ALIGN_RIGHT|wx.ALIGN_CENTRE)
        self.checkrun_label.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.checkrun_label.SetForegroundColour('Black')
        self.checkrun_label.SetMinSize((290, 17))
        checkrun.Add(self.checkrun_label, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        self.running_panel.SetSizer(checkrun)
        left_box.Add(self.running_panel, 0, 0, 0)

        # report panel
        self.report_panel = wx.TextCtrl(self.start, -1, _("Execution Protocol......\n\n"), style=wx.TE_MULTILINE|wx.TE_READONLY)
        right_box.Add(self.report_panel, -1, wx.EXPAND, 0)

        # Progress bar
        self.label_6 = wx.StaticText(self.start, -1, _("Progress:  "))
        right_box.Add(self.label_6, 0, wx.TOP, 5)

        self.gauge_1 = wx.Gauge(self.start, 0, 100)
        self.gauge_1.SetMinSize((670, 20))
        right_box.Add(self.gauge_1, 0, wx.EXPAND|wx.BOTTOM|wx.RIGHT, 5)

        # Pack main sizer
        start_main.Add(left_box, 0, wx.LEFT, 5)
        start_main.Add(right_box, -1, wx.EXPAND, 0)
        self.start.SetSizer(start_main)
        self.MainTab.AddPage(self.start, _("Analysis"))
