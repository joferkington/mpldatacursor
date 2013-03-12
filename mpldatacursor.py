import numpy as np
from matplotlib import cbook
from matplotlib import offsetbox
from matplotlib import _pylab_helpers as pylab_helpers
import matplotlib.transforms as mtransforms
import copy

from matplotlib.image import AxesImage
from matplotlib.collections import PathCollection
from matplotlib.lines import Line2D

def datacursor(artists=None, axes=None, **kwargs):
    """
    Create an interactive data cursor for the specified artists or specified 
    axes. The data cursor displays information about a selected artist in a
    "popup" annotation box.

    If a specific sequence of artists is given, only the specified artists will
    be interactively selectable.  Otherwise, all manually-plotted artists in 
    *axes* will be used (*axes* defaults to all axes in all figures).

    Parameters:
    -----------
        artists: a matplotlib artist or sequence of artists, optional
            The artists to make selectable and display information for. If this
            is not specified, then all manually plotted artists in *axes* will
            be used.
        axes: a matplotlib axes of sequence of axes, optional
            The axes to selected artists from if a sequence of artists is not
            specified.  If *axes* is not specified, then all available axes in
            all figures will be used.
        tolerance: number, optional
            The radius (in points) that the mouse click must be within to
            select the artist.
        formatter: callable, optional
            A function that accepts arbitrary kwargs and returns a string
            that will be displayed with annotate. Often, it is convienent to
            pass in the format method of a template string, e.g. 
            ``formatter="{label}".format``.
            Keyword arguments passed in to the *formatter* function:
                x, y: floats
                    The x and y data coordinates of the clicked point
                event: a matplotlib ``PickEvent``
                    The pick event that was fired (note that the selected 
                    artist can be accessed through ``event.artist``).
                label: string or None
                    The legend label of the selected artist.
            Some selected artists may supply additional keyword arguments that
            are not always present, for example:
                z: number
                    The "z" (usually color or array) value, if present. For an
                    ``AxesImage`` (as created by ``imshow``), this will be the 
                    uninterpolated array value at the point clicked. For a 
                    ``PathCollection`` (as created by ``scatter``) this will be
                    the "c" value if an array was passed to "c".
                i, j: ints
                    The row, column indicies of the selected point for an 
                s: number
                    The size of the selected item in a ``PathCollection`` if a
                    size array is specified.
                c: number
                    The array value displayed as color for a ``PathCollection``
                    if a "c" array is specified (identical to "z").
        display: string, optional
            Controls whether more than one annotation box will be shown.
            Valid values are "single", "one-per-axes", or "mutiple".
        draggable: boolean, optional
            Controls whether or not the annotation box will be
            interactively draggable to a new location after being
            displayed. Defaults to False.

    Additional keyword arguments are passed on to annotate.
    """
    def plotted_artists(ax):
        artists = ax.lines + ax.patches + ax.collections + ax.containers \
                + ax.images
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

class DataCursor(object):
    """A simple data cursor widget that displays the x,y location of a
    matplotlib artist in an annotation box when the artist is clicked on."""

    default_annotation_kwargs = dict(xy=(0, 0), xytext=(-5, 5), ha='right',  
                textcoords='offset points', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    def __init__(self, artists, tolerance=5, formatter=None, 
                 display='one-per-axes', draggable=False, **kwargs):
        """Create the data cursor and connect it to the relevant figure.

        Parameters:
        -----------
            artists: a matplotlib artist or sequence of artists.
                The artists to make selectable and display information for.
            tolerance: number, optional
                The radius (in points) that the mouse click must be within to
                select the artist.
            formatter: function, optional
                A function that accepts arbitrary kwargs and returns a string
                that will be displayed with annotate. The "x", "y", "event",
                and "label" kwargs will always be present. See the "datacursor"
                function docstring for more information.
            display: string, optional
                Controls whether more than one annotation box will be shown.
                Valid values are "single", "one-per-axes", or "mutiple".
            draggable: boolean, optional
                Controls whether or not the annotation box will be
                interactively draggable to a new location after being
                displayed. Defaults to False.

        Additional keyword arguments are passed on to annotate.
        """
        valid_display_options = ['single', 'one-per-axes', 'multiple']
        if display in valid_display_options:
            self.display = display
        else:
            raise ValueError('"display" must be one of the following: '\
                             ', '.join(valid_display_options))

        if not cbook.iterable(artists):
            artists = [artists]
        self.artists = artists
        self.draggable = draggable
        self.axes = tuple(set(art.axes for art in self.artists))
        self.figures = tuple(set(ax.figure for ax in self.axes))

        if formatter is None:
            self.formatter = self._formatter
        else:
            self.formatter = formatter

        self._annotation_kwargs = kwargs
        self.annotations = {}
        if display is not 'multiple':
            for ax in self.axes:
                self.annotations[ax] = self.annotate(ax, **kwargs)
                # Hide the annotation box until clicked...
                self.annotations[ax].set_visible(False)

        for artist in self.artists:
            artist.set_picker(tolerance)
        for fig in self.figures:
            fig.canvas.mpl_connect('pick_event', self)

    def event_info(self, event):
        """Get a dict of info for the artist selected by "event"."""
        def default_func(event):
            return {}
        registry = {
                AxesImage : image_props,
                PathCollection : scatter_props,
                Line2D : line_props,
                }
        x, y = event.mouseevent.xdata, event.mouseevent.ydata
        props = dict(x=x, y=y, label=event.artist.get_label())
        func = registry.get(type(event.artist), default_func)
        props.update(func(event))
        return props

    def _formatter(self, event=None, x=None, y=None, z=None, s=None, 
                   label=None, **kwargs):
        """
        Default formatter function, if no `formatter` kwarg is specified.Takes
        information about the pick event as a series of kwargs and returns the
        string to be displayed.
        """
        output = []
        for key, val in zip(['x', 'y', 'z', 's'], [x, y, z, s]):
            if val is not None:
                output.append('{key}: {val:0.3g}'.format(key=key, val=val))

        # label may be None or an empty string (for an un-labeled AxesImage)...
        # Un-labeled Line2D's will have labels that start with an underscore
        if label and not label.startswith('_'):
            output.append('Label: {}'.format(label))

        return '\n'.join(output)

    def annotate(self, ax, **kwargs):
        """
        Draws the annotation box for the given axis *ax*. Additional kwargs
        are passed on to ``annotate``.
        """
        for key in self.default_annotation_kwargs:
            if key not in kwargs:
                kwargs[key] = self.default_annotation_kwargs[key]

        annotation = ax.annotate('This text will be reset', **kwargs)

        # Place the annotation in the figure instead of the axes so that it 
        # doesn't get hidden behind other subplots (zorder won't fix that).
        ax.figure.texts.append(ax.texts.pop())

        # Create a draggable annotation box, if required.
        if self.draggable:
            offsetbox.DraggableAnnotation(annotation)

        return annotation

    def update(self, event, annotation):
        """Update the specified annotation."""
        # Rather than trying to interpolate, just display the clicked coords
        # This will only be called if it's within "tolerance", anyway.
        x, y = event.mouseevent.xdata, event.mouseevent.ydata
        annotation.xy = x, y

        # Update the text using the specified formatter function 
        annotation.set_text(self.formatter(**self.event_info(event)))

        # In case it's been hidden earlier...
        annotation.set_visible(True)

        event.canvas.draw()

    def __call__(self, event):
        """Create or update annotations for the given event. (This is intended
        to be a callback connected to "pick_event".)"""
        # Ignore pick events for the annotation box itself (otherwise, 
        # draggable annotation boxes won't work)
        if event.artist in self.annotations.values():
            return

        ax = event.artist.axes
        # Get the pre-created annotation box for the axes or create a new one.
        if self.display != 'multiple':
            annotation = self.annotations[ax]
        elif event.mouseevent in self.annotations:
            # Avoid creating multiple datacursors for the same click event
            # when several artists are selected.
            annotation = self.annotations[event.mouseevent]
        else:
            annotation = self.annotate(ax, **self._annotation_kwargs)
            self.annotations[event.mouseevent] = annotation

        if self.display == 'single':
            # Hide any other annotation boxes...
            for ann in self.annotations.values():
                ann.set_visible(False)

        self.update(event, annotation)

class HighlightingDataCursor(DataCursor):
    """A data cursor that highlights the selected Line2D artist."""
    def __init__(self, *args, **kwargs):
        """
        Accepts a series of artists to interactively highlight. 

        Arguments are identical to ``DataCursor`` except for the following
        keyword arguments:

        Parameters:
            artists: a matplotlib artist or sequence of artists.
                The artists to make selectable and display information for.
            highlight_color: a valid color specifier (string or tuple)
                The color to set the highlighted artist to
            highlight_width: 
                The width of the highlighted artist
        """
        self.highlight_color = kwargs.pop('highlight_color', 'yellow')
        self.highlight_width = kwargs.pop('highlight_width', 3)
        DataCursor.__init__(self, *args, **kwargs)
        self.highlights = {}

    def update(self, event, annotation):
        # Decide whether or not to hide previous highlights...
        for artist in self.highlights.values():
            if self.display == 'multiple':
                continue
            if self.display == 'one-per-axes':
                if event.mouseevent.inaxes is not artist.axes:
                    continue
            artist.set_visible(False)
        self.show_highlight(event.artist)
        DataCursor.update(self, event, annotation)

    def show_highlight(self, artist):
        """Show or create a highlight for a givent artist."""
        # This is a separate method to make subclassing easier.
        if artist in self.highlights:
            self.highlights[artist].set_visible(True)
        else:
            self.highlights[artist] = self.create_highlight(artist)
        return self.highlights[artist]
    
    def create_highlight(self, artist):
        """Create a new highlight for the given artist."""
        highlight = copy.copy(artist)
        highlight.set(color=self.highlight_color, mec=self.highlight_color,
                      lw=self.highlight_width, mew=self.highlight_width,
                      picker=None)
        artist.axes.add_artist(highlight)
        return highlight

#-- Artist-specific pick info functions --------------------------------------

def _coords2index(im, x, y):
    """
    Converts data coordinates to index coordinates of the array.

    Parameters:
    -----------
        im: A matplotlib image artist.
        x: The x-coordinate in data coordinates.
        y: The y-coordinate in data coordinates.

    Returns:
    --------
        i, j: Index coordinates of the array associated with the image.
    """
    xmin, xmax, ymin, ymax = im.get_extent()
    if im.origin == 'upper':
        ymin, ymax = ymax, ymin
    data_extent = mtransforms.Bbox([xmin, ymin, xmax, ymax])
    array_extent = mtransforms.Bbox([[0, 0], im.get_array().shape])
    trans = mtransforms.BboxTransformFrom(data_extent) +\
            mtransforms.BboxTransformTo(array_extent)
    return trans.transform_point([x,y]).astype(int)

def image_props(event):
    """
    Get information for a pick event on an ``AxesImage`` artist. Returns a dict
    of "i" & "j" index values of the image for the point clicked, and "z": the
    (uninterpolated) value of the image at i,j.
    
    Parameters:
    -----------
        event : PickEvent
            The pick event to process

    Returns:
    --------
        props : dict
            A dict with keys: z, i, j
    """
    x, y = event.mouseevent.xdata, event.mouseevent.ydata
    i, j = _coords2index(event.artist, x, y)
    z = event.artist.get_array()[j,i]
    return dict(z=z, i=i, j=j)

def line_props(event):
    """
    Get information for a pick event on a Line2D artist (as created with
    ``plot``.)

    This will yield x and y values that are interpolated between verticies 
    (instead of just being the position of the mouse) or snapped to the nearest
    vertex only the vertices are drawn.
 
    Parameters:
    -----------
        event : PickEvent
            The pick event to process

    Returns:
    --------
        props : dict
            A dict with keys: x & y
    """
    xclick, yclick = event.mouseevent.xdata, event.mouseevent.ydata
    i = event.ind[0]
    xorig, yorig = event.artist.get_xydata().T

    # For points-only lines, snap to the nearest point (or if we're at the last
    # point, don't bother interpolating and do the same thing.)
    if event.artist.get_linestyle() == 'none' or i == xorig.size - 1:
        return dict(x=xorig[i], y=yorig[i])

    # Interpolate between the indicies so that the x, y coords are precisely
    # on the line instead of at the point clicked.
    (x0, x1), (y0, y1) = xorig[[i, i+1]], yorig[[i, i+1]]
    vec1 = np.array([x1 - x0, y1 - y0])
    vec2 = np.array([xclick - x0, yclick - y0])
    dist_along = vec1.dot(vec2)
    x, y = np.array([x0, y0]) + dist_along * vec1

    return dict(x=x, y=y)

def scatter_props(event):
    """
    Get information for a pick event on a PathCollection artist (usually 
    created with ``scatter``). 
 
    Parameters:
    -----------
        event : PickEvent
            The pick event to process
    
    Returns:
    --------
        A dict with keys: 
            "c": The value of the color array at the point clicked.
            "s": The value of the size array at the point clicked.
            "z": Identical to "c". Specified for convenience (unified
                 ``template`` kwargs to ``DataCursor``).
        If constant values were specified to ``c`` or ``s`` when calling 
        ``scatter``, "c" and/or "z" will be ``None``.
    """
    # Use only the first item, if multiple items were selected
    ind = event.ind[0]

    arr = event.artist.get_array()
    # If a constant color/c/z was specified, don't return it
    if len(arr) == 1:
        z = None
    else:
        z = arr[ind]

    # If a constant size/s was specified, don't return it
    sizes = event.artist.get_sizes()
    if len(sizes) == 1:
        s = None
    else:
        s = sizes[ind]

    # Snap to the x, y of the point...
    xorig, yorig = event.artist.get_offsets().T
    x, y = xorig[ind], yorig[ind]

    return dict(x=x, y=y, z=z, s=s, c=z)
