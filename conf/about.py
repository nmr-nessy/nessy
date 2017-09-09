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
from os import sep

# NESSY modules
from conf.path import NESSY_PIC, SPLASH_PIC
from conf.settings import VERSION



class about_NESSY(wx.Dialog):
    def __init__(self, *args, **kwds):

        # Window
        kwds["style"] = wx.STAY_ON_TOP
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle("NESSY")
        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(wx.Bitmap(NESSY_PIC, wx.BITMAP_TYPE_ANY))
        self.SetIcon(_icon)

        # Sizer
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Image
        self.nessy = wx.StaticBitmap(self, -1, wx.Bitmap(SPLASH_PIC, wx.BITMAP_TYPE_ANY))
        sizer.Add(self.nessy, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
        self.nessy.Bind(wx.EVT_LEFT_DOWN, self.close_about)

        '''# Title
        self.label_1 = wx.StaticText(self, -1, "NESSY "+VERSION)
        self.label_1.SetFont(wx.Font(13, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        sizer.Add(self.label_1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE|wx.TOP, 10)

        # Description
        self.label_2 = wx.StaticText(self, -1, "NESSY - Nmr rElaxation diSpersion SpectroscopY\n\nNESSY is a software to analyse NMR relaxation dispersion data and\ncalculate us - ms motion of proteins\n\n(C) 2010 - 2011 Michael Bieri", style=wx.ALIGN_CENTRE)
        self.label_2.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        sizer.Add(self.label_2, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 15)

        # Reference
        reference = wx.StaticText(self, -1, "Automated NMR relaxation dispersion data analysis using NESSY\nM. Bieri and P. Gooley, BMC Bioinformatics 2011, 12:421", style=wx.ALIGN_CENTRE)
        reference.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "Sans"))
        sizer.Add(reference, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 5)

        # Close button
        self.button_close_about = wx.Button(self, -1, "Close")
        self.Bind(wx.EVT_BUTTON, self.close_about, self.button_close_about)
        sizer.Add(self.button_close_about, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 5)'''

        # Layout
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Layout()


    def close_about(self, event): # close
        self.Destroy()



def info_nessy():
    aboutnessy = about_NESSY(None, -1, "")
    aboutnessy.Show()
