__license__ = """
Copyright (c) 2012 mpldatacursor developers

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
from mpl_toolkits import mplot3d

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
    xclick, yclick = event.mouseevent.xdata, event.mouseevent.ydata
    i = event.ind[0]
    xorig, yorig = event.artist.get_xydata().T

    # For points-only lines, snap to the nearest point (or if we're at the last
    # point, don't bother interpolating and do the same thing.)
    linestyle = event.artist.get_linestyle()
    if linestyle in ['none', ' ', '', None, 'None'] or i == xorig.size - 1:
        return dict(x=xorig[i], y=yorig[i])

    # ax.step is actually implemented as a Line2D with a different drawstyle...
    drawstyle = event.artist.get_drawstyle()
    lookup = {'steps-pre':_interpolate_steps_pre,
              'steps-post':_interpolate_steps_post,
              'steps-mid':_interpolate_steps_mid,
              'default':_interpolate_line}
    x, y = lookup[drawstyle](xorig[[i, i+1]], yorig[[i, i+1]], xclick, yclick)

    return dict(x=x, y=y)

def _interpolate_line(xorig, yorig, xclick, yclick):
    """Find the nearest point on a single line segment to the point *xclick*
    *yclick*."""
    (x0, x1), (y0, y1) = xorig, yorig
    vec1 = np.array([x1 - x0, y1 - y0])
    vec1 /= np.linalg.norm(vec1)
    vec2 = np.array([xclick - x0, yclick - y0])
    dist_along = vec1.dot(vec2)
    x, y = np.array([x0, y0]) + dist_along * vec1
    return x, y

def _interpolate_steps_pre(xorig, yorig, xclick, yclick):
    """Interpolate x,y for a stepped line with the default "pre" steps."""
    (x0, x2), (y0, y2) = xorig, yorig
    x1, y1 = x0, y2
    return _interpolate_steps([x0, x1, x2], [y0, y1, y2], xclick, yclick)

def _interpolate_steps_post(xorig, yorig, xclick, yclick):
    """Interpolate x,y for a stepped line with "post" steps."""
    (x0, x2), (y0, y2) = xorig, yorig
    x1, y1 = x2, y0
    return _interpolate_steps([x0, x1, x2], [y0, y1, y2], xclick, yclick)

def _interpolate_steps_mid(xorig, yorig, xclick, yclick):
    """Interpolate x,y for a stepped line with "post" steps."""
    (x0, x3), (y0, y3) = xorig, yorig
    x1, y1 = np.mean(xorig), y0
    x2, y2 = x1, y3
    x, y = [x0, x1, x2, x3], [y0, y1, y2, y3]
    return _interpolate_steps(x, y, xclick, yclick)

def _interpolate_steps(xvals, yvals, xclick, yclick):
    """Multi-segment version of _interpolate_line."""
    segments, distances = [], []
    for x, y in zip(zip(xvals, xvals[1:]), zip(yvals, yvals[1:])):
        dist = _dist2line([x[0], y[0]], [x[1], y[1]], [xclick, yclick])
        distances.append(dist)
        segments.append([x, y])

    i = np.argmin(distances)
    x, y = segments[i]
    return _interpolate_line(x, y, xclick, yclick)

def _dist2line(v, w, p):
    """
    Nearest distance from a point *p* to a finite line segment formed from the
    x,y pairs *v* and *w*. Loosely based on: http://stackoverflow.com/a/1501725
    """
    def _dist(a, b):
        return np.hypot(*(a - b))

    v, w, p = np.atleast_1d(v, w, p)
    t = np.dot(p - v, w - v) / np.linalg.norm(w - v)
    if t < 0:
        return _dist(p, v)
    elif t > 1:
        return _dist(p, w)
    else:
        projection = v + t * (w - v)
        return _dist(p, projection)

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

def three_dim_props(event):
    """
    Get information for a pick event on a 3D artist.

    Parameters
    -----------
    event : PickEvent
        The pick event to process

    Returns
    --------
    A dict with keys:
        `x`: The estimated x-value of the click on the artist
        `y`: The estimated y-value of the click on the artist
        `z`: The estimated z-value of the click on the artist

    Notes
    -----
    Based on mpl_toolkits.axes3d.Axes3D.format_coord
    Many thanks to Ben Root for pointing this out!
    """
    ax = event.artist.axes
    if ax.M is None:
        return {}

    xd, yd = event.mouseevent.xdata, event.mouseevent.ydata
    p = (xd, yd)
    edges = ax.tunit_edges()
    ldists = [(mplot3d.proj3d.line2d_seg_dist(p0, p1, p), i) for \
                i, (p0, p1) in enumerate(edges)]
    ldists.sort()

    # nearest edge
    edgei = ldists[0][1]

    p0, p1 = edges[edgei]

    # scale the z value to match
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    d0 = np.hypot(x0-xd, y0-yd)
    d1 = np.hypot(x1-xd, y1-yd)
    dt = d0+d1
    z = d1/dt * z0 + d0/dt * z1

    x, y, z = mplot3d.proj3d.inv_transform(xd, yd, z, ax.M)
    return dict(x=x, y=y, z=z)

def rectangle_props(event):
    artist = event.artist
    width, height = artist.get_width(), artist.get_height()
    left, bottom = artist.xy
    try:
        label = artist._mpldatacursor_label
    except AttributeError:
        label = None
    return dict(width=width, height=height, left=left, bottom=bottom,
                label=label)
