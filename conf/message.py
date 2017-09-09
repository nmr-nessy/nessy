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

def error_popup(msg, parent=None):
    message = wx.MessageDialog(parent, message = msg, style = wx.OK | wx.ICON_ERROR)
    message.ShowModal()

def question(msg, parent=None):
    check = False
    startrelax = wx.MessageDialog(parent, message = msg, style = wx.YES_NO | wx.NO_DEFAULT)
    if startrelax.ShowModal() == wx.ID_YES:
        check = True
    else:
        check = False 
    return check

def message(msg, parent=None):
    message = wx.MessageDialog(parent, msg, style = wx.OK | wx.ICON_INFORMATION)
    message.ShowModal()

def NESSY_error(text):
    message = wx.Dialog(text, style = wx.OK | wx.ICON_ERROR)
    message.Show()
    
