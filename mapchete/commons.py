#!/usr/bin/env python

import sys
import math
import numpy as np

NODATA = -1

"""
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

- Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

- Neither the name of the project nor the names of its contributors may be
used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
def hillshade(
    elevation,
    xres,
    yres,
    nodata=None,
    azimuth=315.0,
    altitude=45.0,
    z=1.0,
    scale=1.0
    ):
    """ Return a pair of arrays 2 pixels smaller than the input elevation array.

        Slope is returned in radians, from 0 for sheer face to pi/2 for
        flat ground. Aspect is returned in radians, counterclockwise from -pi
        at north around to pi.

        Logic here is borrowed from hillshade.cpp:
          http://www.perrygeo.net/wordpress/?p=7
    """
    width, height = elevation.shape[0] - 2, elevation.shape[1] - 2

    window = [z * elevation[row:(row + height), col:(col + width)]
              for (row, col)
              in product(range(3), range(3))]

    x = ((window[0] + window[3] + window[3] + window[6]) \
       - (window[2] + window[5] + window[5] + window[8])) \
      / (8.0 * xres);

    y = ((window[6] + window[7] + window[7] + window[8]) \
       - (window[0] + window[1] + window[1] + window[2])) \
      / (8.0 * yres);

    # in radians, from 0 to pi/2
    slope = pi/2 - np.arctan(np.sqrt(x*x + y*y))

    # in radians counterclockwise, from -pi at north back to pi
    aspect = np.arctan2(x, y)

    deg2rad = math.pi / 180.0

    shaded = np.sin(altitude * deg2rad) * np.sin(slope * deg2rad) \
           + np.cos(altitude * deg2rad) * np.cos(slope * deg2rad) \
           * np.cos((azimuth - 90.0) * deg2rad - aspect);

    shaded = shaded * 255

    if nodata is not None:
        for pane in window:
            shaded[pane == nodata] = NODATA


    # invert values & return array in original shape
    shaded = -shaded+256
    shaded[shaded<1] = 0
    return np.pad(shaded, 1, mode='constant')
