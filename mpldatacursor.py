from matplotlib import cbook
from matplotlib import offsetbox
import matplotlib.transforms as mtransforms
import matplotlib.pyplot as plt
import copy

from matplotlib.image import AxesImage
from matplotlib.collections import PathCollection

def datacursor(artists=None, ax=None, **kwargs):
    if ax is None:
        ax = plt.gca()
    if artists is None:
        artists = ax.lines + ax.patches + ax.collections + ax.containers + \
                  ax.images
    return DataCursor(artists, **kwargs)

class DataCursor(object):
    """A simple data cursor widget that displays the x,y location of a
    matplotlib artist in an annotation box when the artist is clicked on."""
    def __init__(self, artists, tolerance=5, offsets=(-5, 5), 
                 template='x:{x:0.2f}\ny:{y:0.2f}', formatter=None, 
                 display='one-per-axes', draggable=False, **kwargs):
        """Create the data cursor and connect it to the relevant figure.

        Parameters:
        -----------
            artists: a matplotlib artist or sequence of artists.
                The artists to make selectable and display information for.
            tolerance: number, optional
                The radius (in points) that the mouse click must be within to
                select the artist.
            offsets: sequence of two numbers, optional
                A tuple of (x,y) offsets in points from the selected point to
                the displayed annotation box.
            template: string, optional
                The format string to be used. Note: this uses "new-style"
                string formatting. This will be ignored if a *formatter*
                function is specified. This will be called as
                ``template.format(x=x, y=y, label=label, event=event)``, where
                x & y are the data coordinates of the pick event, "label" is
                the label of the artist (as displayed in the legend), and
                "event" is the pick event object.
            formatter: function, optional
                A function that accepts the pick event and returns a string
                that will be displayed with annotate. Note that the picked
                artist can be accessed with ``event.artist`` and the x and y
                coords can be accessed with ``event.mouseevent.x``, etc.
            display: string, optional
                Controls whether more than one annotation box will be shown.
                Valid values are "single", "one-per-axes", or "mutiple".
            draggable: boolean, optional
                Controls whether or not the annotation box will be
                interactively draggable to a new location after being
                displayed. Defaults to False.

        Additional keyword arguments are passed on to annotate.
        """
        self.template = template
        self.offsets = offsets

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
        def default_func(event):
            return {}
        registry = {
                AxesImage : image_props,
                PathCollection : scatter_props,
                }
        x, y = event.mouseevent.xdata, event.mouseevent.ydata
        props = dict(x=x, y=y, label=event.artist.get_label(),
                     z=None, s=None, c=None)
        func = registry.get(type(event.artist), default_func)
        props.update(func(event))
        return props

    def _formatter(self, event, x, y, z=None, s=None, label=None):
        """Default formatter function, if no `formatter` kwarg is specified.
        Takes a pick event and returns the text string to be displayed."""
        output = []
        for axis in [event.artist.
        for key, val in dict(z=z, s=s).iteritems():
            if val is not None:
                output.append('{key}: {val:0.2f}'.format(key=key, val=val))

        if label is not None and not label.startswith('_'):
            output.append('Label: {}'.format(label))

        return '\n'.join(output)

    default_annotation_kwargs = dict(xy=(0, 0), ha='right', 
                textcoords='offset points', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    def annotate(self, ax, **kwargs):
        """
        Draws the annotation box for the given axis *ax*. Additional kwargs
        are passed on to ``annotate``.
        """
        for key in self.default_annotation_kwargs:
            if key not in kwargs:
                kwargs[key] = self.default_annotation_kwargs[key]
        kwargs['xytext'] = self.offsets

        annotation = ax.annotate(self.template, **kwargs)

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
        print event.ind
        # Ignore pick events for the annotation box itself (otherwise, 
        # draggable annotation boxes won't work)
        if event.artist in self.annotations.values():
            return

        # Get the pre-created annotation box for the axes or create a new one.
        if self.display != 'multiple':
            annotation = self.annotations[event.artist.axes]
        else:
            annotation = self.annotate(event.artist.axes, 
                                       **self._annotation_kwargs)
            self.annotations[event.artist.axes] = annotation

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

        # Show or create a highlight for the current event
        if event.artist in self.highlights:
            self.highlights[event.artist].set_visible(True)
        else:
            self.highlights[event.artist] = self.create_highlight(event.artist)

        DataCursor.update(self, event, annotation)
    
    def create_highlight(self, artist):
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
            A dict with keys: x, y, z, i, j
    """
    x, y = event.mouseevent.xdata, event.mouseevent.ydata
    i, j = _coords2index(event.artist, x, y)
    z = event.artist.get_array()[j,i]
    return dict(z=z, i=i, j=j)

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
    arr = event.artist.get_array()
    if len(arr) == 1:
        z = None
    else:
        z = arr[event.ind]

    sizes = event.artist.get_sizes()
    if len(sizes) == 1:
        s = None
    else:
        s = sizes[event.ind]
    return dict(z=z, s=s, c=z)

