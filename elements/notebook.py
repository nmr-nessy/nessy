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


import wx
from os import sep

def build_notebook(self):
        """Build notebook GUI element"""

        self.MainTab = wx.Notebook(self, -1)
        self.MainTab.SetBackgroundColour(wx.Colour(237, 236, 235))

        # Sizer
        self.notebook_box = wx.BoxSizer(wx.HORIZONTAL)



def pack_notebook(self):
        """Pack generated tabs"""

        self.notebook_box.Add(self.MainTab, -1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(self.notebook_box)
