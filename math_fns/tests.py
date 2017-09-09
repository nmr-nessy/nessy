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

# Statistical tests


def Alpha(B1, B2, Rex1, Rex2):
    """Determination of exchnage time regime using:

    alpha = ( (B2 + B1) / (B2 - B1) ) * ( (Rex2 - Rex1) / (Rex2 + Rex1) )

    B1 / B2:        Static magnetic field.
    Rex1/Rex2:      Exchange constant of fast exchange model.
    """

    return ((B2 + B1) / (B2 - B1) ) * ( (Rex2 - Rex1) / (Rex2 + Rex1) )


def AIC(chi2, k):
    """AIC = chi2 + 2k.

    k = number of parameters (one of them being the intercept)"""

    return (chi2 + 2*k)


def AICc(chi2, k, n):
    """AICc = AIC + (2k(k+1)) / (n-k-1).

    k = number of parameters (one of them being the intercept)
    n = sample size"""

    return ((chi2 + 2*k) + ((2*k*(k+1)) / (n-k-1)) )


def F_test(chi2_1, k_1, chi2_2, k_2, n):
    """F-test

        (chi2(simpler) - chi2(higher)) / (k(higher) - k(simpler))
    F =  ----------------------------------------------------------
                        chi2(higher) / (n - k(higher)

    chi2_1:     chi2 of model with less parameters
    k_1:        number if parameters of model with less parameters
    chi2_2:     chi2 of model with more parameters
    k_2:        number if parameters of model with more parameters
    n:          sample size
    """

    F = ( (chi2_1 - chi2_2) / (k_2 - k_1) ) / ( chi2_2 / (n - k_2))

    return F




