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


# Splash Screen

# Python modules
import wx
try:
    from wx import SplashScreen, SPLASH_CENTRE_ON_SCREEN, SPLASH_TIMEOUT
except ImportError:
    from wx.adv import SplashScreen, SPLASH_CENTRE_ON_SCREEN, SPLASH_TIMEOUT

# NESSY modules
from conf.path import SPLASH_PIC, SPLASH_EXIT_PIC


class Splash(SplashScreen):
    """Splash Screen."""

    def __init__(self, parent=None):
        aBitmap = wx.Image(name = SPLASH_PIC).ConvertToBitmap()
        splashStyle = SPLASH_CENTRE_ON_SCREEN | SPLASH_TIMEOUT

        splashDuration = 2000 # milliseconds

        SplashScreen.__init__(self, aBitmap, splashStyle,
                                 splashDuration, parent)
        wx.Yield()

class Splash_exit(SplashScreen):
    """Splash Screen."""

    def __init__(self, parent=None):
        aBitmap = wx.Image(name = SPLASH_EXIT_PIC).ConvertToBitmap()
        splashStyle = SPLASH_CENTRE_ON_SCREEN | SPLASH_TIMEOUT

        splashDuration = 2000 # milliseconds

        SplashScreen.__init__(self, aBitmap, splashStyle,
                                 splashDuration, parent)
        wx.Yield()
