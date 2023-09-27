# -*- coding: utf-8 -*-
"""
Created on Wed Sep 27 16:29:22 2023

@author: cfai2304
"""
import numpy as np

CALI_DELTA_WL = 2.999

CALI_DELTA_PIX = {1: 93,
                  2: 93,
                  3: 620}

def get_position(wl, n_pixels, grating_no, binning):
    """
    Calculate the wavelength array corresponding
    to the image pixel x-coordinates
    """
    c = CALI_DELTA_WL / CALI_DELTA_PIX[grating_no] * binning
    x = np.arange(n_pixels)
    x0 = wl - c * n_pixels / 2
    
    x = x0 + c * x
    return x