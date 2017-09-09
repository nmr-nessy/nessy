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

# Calculation of R2eff

# Python modules
from math import log


def R2eff_cpmg(T, I0, I):
        """Calculate R2eff.

        T:          CPMG delay
        I0:         reference intensity
        I:          Intensity at CPMG frequency x

        R2eff = (-ln{I(v[CPMG])/I(O)}) / T
        """

        return (1/T)*log(I0/I)


def On_resonance(T, I0, I):
        """Calculate R1p.

        T:          Spin lock time
        I0:         reference intensity
        I:          Intensity at resonance offset at T(x)

        R1rho = 1/T * ln(I0/I)
        """

        return (1/T)*log(I0/I)
