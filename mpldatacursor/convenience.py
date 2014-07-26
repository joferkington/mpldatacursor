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
from matplotlib import _pylab_helpers as pylab_helpers
from matplotlib import cbook

from .datacursor import DataCursor

def datacursor(artists=None, axes=None, **kwargs):
    """
    Create an interactive data cursor for the specified artists or specified
    axes. The data cursor displays information about a selected artist in a
    "popup" annotation box.

    If a specific sequence of artists is given, only the specified artists will
    be interactively selectable.  Otherwise, all manually-plotted artists in
    *axes* will be used (*axes* defaults to all axes in all figures).

    Parameters
    -----------
    artists : a matplotlib artist or sequence of artists, optional
        The artists to make selectable and display information for. If this is
        not specified, then all manually plotted artists in `axes` will be
        used.
    axes : a matplotlib axes of sequence of axes, optional
        The axes to selected artists from if a sequence of artists is not
        specified.  If `axes` is not specified, then all available axes in all
        figures will be used.
    tolerance : number, optional
        The radius (in points) that the mouse click must be within to select
        the artist. Default: 5 points.
    formatter : callable, optional
        A function that accepts arbitrary kwargs and returns a string that will
        be displayed with annotate. Often, it is convienent to pass in the
        format method of a template string, e.g.
        ``formatter="{label}".format``.
        Keyword arguments passed in to the `formatter` function:
            `x`, `y` : floats
                The x and y data coordinates of the clicked point
            `event` : a matplotlib ``PickEvent``
                The pick event that was fired (note that the selected
                artist can be accessed through ``event.artist``).
            `label` : string or None
                The legend label of the selected artist.
            `ind` : list of ints or None
                If the artist has "subitems" (e.g. points in a scatter or
                line plot), this will be a list of the item(s) that were
                clicked on.  If the artist does not have "subitems", this
                will be None. Note that this is always a list, even when
                a single item is selected.
        Some selected artists may supply additional keyword arguments that
        are not always present, for example:
            `z` : number
                The "z" (usually color or array) value, if present. For an
                ``AxesImage`` (as created by ``imshow``), this will be the
                uninterpolated array value at the point clicked. For a
                ``PathCollection`` (as created by ``scatter``) this will be the
                "c" value if an array was passed to "c".
            `i`, `j` : ints
                The row, column indicies of the selected point for an
                ``AxesImage`` (as created by ``imshow``)
            `s` : number
                The size of the selected item in a ``PathCollection`` if a size
                array is specified.
            `c` : number
                The array value displayed as color for a ``PathCollection``
                if a "c" array is specified (identical to "z").
            `point_label` : list
                If `point_labels` is given when the data cursor is initialized
                and the artist has "subitems", this will be a list of the items
                of `point_labels` that correspond to the selected artists.
                Note that this is always a list, even when a single artist is
                selected.
            `width`, `height`, `top`, `bottom` : numbers
                The parameters for ``Rectangle`` artists (e.g. bar plots).
    point_labels : sequence or dict, optional
        For artists with "subitems" (e.g. Line2D's), the item(s) of
        `point_labels` corresponding to the selected "subitems" of the artist
        will be passed into the formatter function as the "point_label" kwarg.
        If a single sequence is given, it will be used for all artists with
        "subitems". Alternatively, a dict of artist:sequence pairs may be given
        to match an artist to the correct series of point labels.
    display : {"one-per-axes", "single", "multiple"}, optional
        Controls whether more than one annotation box will be shown.
        Default: "one-per-axes"
    draggable : boolean, optional
        Controls whether or not the annotation box will be interactively
        draggable to a new location after being displayed. Defaults to False.
    hover : boolean, optional
        If True, the datacursor will "pop up" when the mouse hovers over an
        artist.  Defaults to False.  Enabling hover also sets
        `display="single"` and `draggable=False`.
    props_override : function, optional
        If specified, this function customizes the parameters passed into the
        formatter function and the x, y location that the datacursor "pop up"
        "points" to.  This is often useful to make the annotation "point" to a
        specific side or corner of an artist, regardless of the position
        clicked. The function is passed the same kwargs as the `formatter`
        function and is expected to return a dict with at least the keys "x"
        and "y" (and probably several others).
        Expected call signature: `props_dict = props_override(**kwargs)`
    keybindings : boolean or dict, optional
        By default, the keys "d" and "t" will be bound to deleting/hiding all
        annotation boxes and toggling interactivity for datacursors,
        respectively.  If keybindings is False, the ability to hide/toggle
        datacursors interactively will be disabled. Alternatively, a dict of
        the form {'hide':'somekey', 'toggle':'somekey'} may specified to
        customize the keyboard shortcuts.
    date_format : string, optional
        The strftime-style formatting string for dates. Used only if the x or y
        axes have been set to display dates. Defaults to "%x %X".
    display_button: int, optional
        The mouse button that will triggers displaying an annotation box.
        Defaults to 1, for left-clicking. (Common options are 1:left-click,
        2:middle-click, 3:right-click)
    hide_button: int or None, optional
        The mouse button that triggers hiding the selected annotation box.
        Defaults to 3, for right-clicking. (Common options are 1:left-click,
        2:middle-click, 3:right-click, None:hiding disabled)
    **kwargs : additional keyword arguments, optional
        Additional keyword arguments are passed on to annotate.

    Returns
    -------
    dc : A ``mpldatacursor.DataCursor`` instance
    """
    def plotted_artists(ax):
        artists = (ax.lines + ax.patches + ax.collections
                   + ax.images + ax.containers)
        return artists

    # If no axes are specified, get all axes.
    if axes is None:
        managers = pylab_helpers.Gcf.get_all_fig_managers()
        figs = [manager.canvas.figure for manager in managers]
        axes = [ax for fig in figs for ax in fig.axes]

    if not cbook.iterable(axes):
        axes = [axes]

    # If no artists are specified, get all manually plotted artists in all of
    # the specified axes.
    if artists is None:
        artists = [artist for ax in axes for artist in plotted_artists(ax)]

    return DataCursor(artists, **kwargs)


