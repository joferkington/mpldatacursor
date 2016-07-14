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

def _coords2index(im, x, y, inverted=False):
    """
    Converts data coordinates to index coordinates of the array.

    Parameters
    -----------
    im : An AxesImage instance
        The image artist to operation on
    x : number
        The x-coordinate in data coordinates.
    y : number
        The y-coordinate in data coordinates.
    inverted : bool, optional
        If True, convert index to data coordinates instead of data coordinates
        to index.

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

    if inverted:
        trans = trans.inverted()

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

    This will yield x and y values that are interpolated between vertices
    (instead of just being the position of the mouse) or snapped to the nearest
    vertex if only the vertices are drawn.

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

    # For points-only lines, snap to the nearest point.
    linestyle = event.artist.get_linestyle()
    if linestyle in ['none', ' ', '', None, 'None']:
        return dict(x=xorig[i], y=yorig[i])

    # ax.step is actually implemented as a Line2D with a different drawstyle...
    xs_data = xorig[max(i - 1, 0) : i + 2]
    ys_data = yorig[max(i - 1, 0) : i + 2]
    drawstyle = event.artist.drawStyles[event.artist.get_drawstyle()]
    if drawstyle == "_draw_lines":
        pass
    elif drawstyle == "_draw_steps_pre":
        xs_data = _interleave(xs_data, xs_data[:-1])
        ys_data = _interleave(ys_data, ys_data[1:])
    elif drawstyle == "_draw_steps_post":
        xs_data = _interleave(xs_data, xs_data[1:])
        ys_data = _interleave(ys_data, ys_data[:-1])
    elif drawstyle == "_draw_steps_mid":
        mid_xs = (xs_data[:-1] + xs_data[1:]) / 2
        xs_data = _interleave(xs_data, np.column_stack([mid_xs, mid_xs]))
        ys_data = _interleave(
            ys_data, np.column_stack([ys_data[:-1], ys_data[1:]]))
    else:
        raise ValueError(
            "Unknown drawstyle: {}".format(event.artist.get_drawstyle()))
    # The artist transform may be different from the axes transform (e.g.,
    # axvline/axhline)
    artist_transform = event.artist.get_transform()
    axes_transform = event.artist.axes.transData
    xs_screen, ys_screen = (
        artist_transform.transform(
            np.column_stack([xs_data, ys_data]))).T
    xclick_screen, yclick_screen = (
        axes_transform.transform([xclick, yclick]))
    x_screen, y_screen = _interpolate_line(xs_screen, ys_screen,
                                           xclick_screen, yclick_screen)
    x, y = axes_transform.inverted().transform([x_screen, y_screen])

    return dict(x=x, y=y)

def _interleave(a, b):
    """Interleave arrays a and b; b may have multiple columns and must be
    shorter by 1.
    """
    b = np.column_stack([b]) # Turn b into a column array.
    nx, ny = b.shape
    c = np.zeros((nx + 1, ny + 1))
    c[:, 0] = a
    c[:-1, 1:] = b
    return c.ravel()[:-(c.shape[1] - 1)]

def _interpolate_line(xorig, yorig, xclick, yclick):
    """Find the nearest point on a polyline segment to the point *xclick*
    *yclick*."""
    candidates = []
    # The closest point may be a vertex.
    for x, y in zip(xorig, yorig):
        candidates.append((np.hypot(xclick - x, yclick - y), (x, y)))
    # Or it may be a projection on a segment.
    for (x0, x1), (y0, y1) in zip(zip(xorig, xorig[1:]), zip(yorig, yorig[1:])):
        vec1 = np.array([x1 - x0, y1 - y0])
        vec1 /= np.linalg.norm(vec1)
        vec2 = np.array([xclick - x0, yclick - y0])
        dist_along = vec1.dot(vec2)
        x, y = np.array([x0, y0]) + dist_along * vec1
        # Drop if out of the segment.
        if (x - x0) * (x - x1) > 0 or (y - y0) * (y - y1) > 0:
            continue
        candidates.append((np.hypot(xclick - x, yclick - y), (x, y)))
    _, (x, y) = min(candidates)
    return x, y

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

def errorbar_props(event):
    if hasattr(event.artist, '_mpldatacursor_parent'):
        container = event.artist._mpldatacursor_parent
    else:
        return {}
    
    if hasattr(event, 'ind') and event.ind is not None:
        i = event.ind[0]
    else:
        return {}

    xerr = yerr = [None] * i
    if container.has_yerr and container.has_xerr:
        xerr = _extract_xerr(container[2][0])
        yerr = _extract_yerr(container[2][1])
    elif container.has_yerr:
        xerr = _extract_xerr(container[2][0])
    elif container.has_xerr:
        yerr = _extract_xerr(container[2][0])

    x, y = container[0].get_xydata().T
    return {'xerror':xerr[i], 'yerror':yerr[i], 'x':x[i], 'y':y[i]}

def _extract_yerr(errbar_artist):
    segments = errbar_artist.get_segments()
    return [abs(np.diff(seg[:,1])[0]) for seg in segments]

def _extract_xerr(errbar_artist):
    segments = errbar_artist.get_segments()
    return [abs(np.diff(seg[:,0])[0]) for seg in segments]

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
    """
    Returns the width, height, left, and bottom of a rectangle artist.

    Parameters
    -----------
    event : PickEvent
        The pick event to process

    Returns
    --------
    A dict with keys:
        `width` : The width of the rectangle
        `height` : The height of the rectangle
        `left` : The minimum x-coordinate of the rectangle
        `right` : The maximum x-coordinate of the rectangle
        `bottom` : The minimum y-coordinate of the rectangle
        `top` : The maximum y-coordinate of the rectangle
        `xcenter` : The mean x-coordinate of the rectangle
        `ycenter` : The mean y-coordinate of the rectangle
        `label` : The label for the rectangle or None
    """
    artist = event.artist
    width, height = artist.get_width(), artist.get_height()
    left, bottom = artist.xy
    right, top = left + width, bottom + height
    xcenter = left + 0.5 * width
    ycenter = bottom + 0.5 * height

    label = artist.get_label()
    if label is None or label.startswith('_nolegend'):
        try:
            label = artist._mpldatacursor_label
        except AttributeError:
            label = None

    return dict(width=width, height=height, left=left, bottom=bottom,
                label=label, right=right, top=top,
                xcenter=xcenter, ycenter=ycenter)

def get_xy(artist):
    """
    Attempts to get the x,y data for individual items subitems of the artist.
    Returns None if this is not possible.

    At present, this only supports Line2D's and basic collections.
    """
    xy = None

    if hasattr(artist, 'get_offsets'):
        xy = artist.get_offsets().T
    elif hasattr(artist, 'get_xydata'):
        xy = artist.get_xydata().T

    return xy
