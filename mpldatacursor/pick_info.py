__license__ = """
Copyright (c) 2012 Free Software Foundation

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import numpy as np
import matplotlib.transforms as mtransforms

#-- Artist-specific pick info functions --------------------------------------

def _coords2index(im, x, y):
    """
    Converts data coordinates to index coordinates of the array.

    Parameters
    -----------
    im : A matplotlib image artist.
    x : The x-coordinate in data coordinates.
    y : The y-coordinate in data coordinates.

    Returns
    --------
    i, j : Index coordinates of the array associated with the image.
    """
    xmin, xmax, ymin, ymax = im.get_extent()
    if im.origin == 'upper':
        ymin, ymax = ymax, ymin
    data_extent = mtransforms.Bbox([[ymin, xmin], [ymax, xmax]])
    array_extent = mtransforms.Bbox([[0, 0], im.get_array().shape[:2]])
    trans = mtransforms.BboxTransformFrom(data_extent) +\
            mtransforms.BboxTransformTo(array_extent)
    return trans.transform_point([y,x]).astype(int)

def image_props(event):
    """
    Get information for a pick event on an ``AxesImage`` artist. Returns a dict
    of "i" & "j" index values of the image for the point clicked, and "z": the
    (uninterpolated) value of the image at i,j.

    Parameters
    -----------
    event : PickEvent
        The pick event to process

    Returns
    --------
    props : dict
        A dict with keys: z, i, j
    """
    x, y = event.mouseevent.xdata, event.mouseevent.ydata
    i, j = _coords2index(event.artist, x, y)
    z = event.artist.get_array()[i,j]
    if z.size > 1:
        # Override default numpy formatting for this specific case. Bad idea?
        z = ', '.join('{:0.3g}'.format(item) for item in z)
    return dict(z=z, i=i, j=j)


def line_props(event):
    """
    Get information for a pick event on a Line2D artist (as created with
    ``plot``.)

    This will yield x and y values that are interpolated between verticies
    (instead of just being the position of the mouse) or snapped to the nearest
    vertex only the vertices are drawn.

    Parameters
    -----------
    event : PickEvent
        The pick event to process

    Returns
    --------
    props : dict
        A dict with keys: x & y
    """
    def atan(x, y):
        if abs(y) < 0.0001:
            if x < 0.0:
                return -np.pi / 2.0
            else:
                return np.pi / 2.0
        return np.arctan(x / y)

    xclick, yclick = event.mouseevent.xdata, event.mouseevent.ydata
    i = event.ind[0]
    xorig, yorig = event.artist.get_xydata().T

    # For points-only lines, snap to the nearest point (or if we're at the last
    # point, don't bother interpolating and do the same thing.)
    if event.artist.get_linestyle() == 'none' or i == xorig.size - 1:
        return dict(x=xorig[i], y=yorig[i])

    (x0, x1), (y0, y1) = xorig[[i, i + 1]], yorig[[i, i + 1]]
    dy = yclick - y0
    dx = xclick - x0
    theta1 = atan(x1 - x0, y1 - y0)
    theta2 = atan(dx, dy)
    theta = np.abs(theta2 - theta1)
    dist_along = np.sqrt(dy * dy + dx * dx) * np.cos(theta)
    x = x0 + dist_along * np.sin(theta1)
    y = y0 + dist_along * np.cos(theta1)

    return dict(x=x, y=y)


def collection_props(event):
    """
    Get information for a pick event on an artist collection (e.g.
    LineCollection, PathCollection, PatchCollection, etc).  This will"""
    ind = event.ind[0]
    arr = event.artist.get_array()
    # If a constant color/c/z was specified, don't return it
    if arr is None or len(arr) == 1:
        z = None
    else:
        z = arr[ind]
    return dict(z=z, c=z)


def scatter_props(event):
    """
    Get information for a pick event on a PathCollection artist (usually
    created with ``scatter``).

    Parameters
    -----------
    event : PickEvent
        The pick event to process

    Returns
    --------
    A dict with keys:
        `c`: The value of the color array at the point clicked.
        `s`: The value of the size array at the point clicked.
        `z`: Identical to `c`. Specified for convenience.

    Notes
    -----
    If constant values were specified to ``c`` or ``s`` when calling
    ``scatter``, `c` and/or `z` will be ``None``.
    """
    # Use only the first item, if multiple items were selected
    ind = event.ind[0]

    try:
        sizes = event.artist.get_sizes()
    except AttributeError:
        sizes = None
    # If a constant size/s was specified, don't return it
    if sizes is None or len(sizes) == 1:
        s = None
    else:
        s = sizes[ind]

    try:
        # Snap to the x, y of the point... (assuming it's created by scatter)
        xorig, yorig = event.artist.get_offsets().T
        x, y = xorig[ind], yorig[ind]
        return dict(x=x, y=y, s=s)
    except IndexError:
        # Not created by scatter...
        return dict(s=s)
