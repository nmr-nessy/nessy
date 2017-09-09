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

# script to check dependencies

# Pyhton import
import sys
try:
    from urllib import urlopen
except ImportError:
    from urllib.request import urlopen

# NESSY import
from conf.message import message


def version_check(current_version):
    """Function to check for updates."""
    newest_version = urlopen('http://download.gna.org/nessy/latest_version.txt').read()

    # return, if SVN version
    if 'svn' in current_version:    return

    # return True, if update available
    if not current_version in newest_version:     message('Newer Version of NESSY is available:\n\nNESSY '+str(newest_version)+'\n\nSee: http://home.gna.org/nessy/')




class Dep_check():
    """Class to check if dependencies are installed."""

    def __init__(self):
        # NumPy
        try:
            import numpy
        except:
            print('Python module numpy (python-numpy) is missing!\n\nCheck out: http://numpy.scipy.org/\n\n')
            sys.exit(0)

        # SciPy
        try:
            import scipy
        except:
            print('Python module scipy (python-scipy) is missing!\n\nCheck out: http://www.scipy.org/\n\n')
            sys.exit(0)

        # xwPython
        try:
            import wx
        except:
            print('Python module wxPython (python-wxgtk2.8 or greater) is missing!\n\nCheck out: http://www.wxpython.org/\n\n')
            sys.exit(0)

        # Pylab
        try:
            import matplotlib
            matplotlib.use('template')
        except:
            print('Python module Pylab (python-matplotlib) is missing!\n\nCheck out: http://matplotlib.sourceforge.net/\n\n')
            sys.exit(0)
