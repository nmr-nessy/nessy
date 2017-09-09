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


# Collection of Rex


def Rex_fast(Phi, kex):
    """Calculation of Rex for fast exchange.

    Phi in Rad/s
    kex in 1/s
    """

    # calculate
    return Phi / kex


def Rex_slow(pb, kex, dw):
    """Calculation of Rex fro slow exchange.

    kex in 1/s
    dw in rad/s
    """

    # calculate
    return (pb*(1-pb)*kex) / (1 + (kex/dw)**2)
