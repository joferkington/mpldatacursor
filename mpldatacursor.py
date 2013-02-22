from matplotlib import cbook
from matplotlib import offsetbox
import matplotlib.transforms as mtransforms
import copy

class DataCursor(object):
    """A simple data cursor widget that displays the x,y location of a
    matplotlib artist in an annotation box when the artist is clicked on."""

    default_annotation_kwargs = dict(xy=(0, 0), ha='right', 
                textcoords='offset points', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    def __init__(self, artists, tolerance=5, offsets=(-5, 5), 
                 template='x:{x:0.2f}\ny:{y:0.2f}', formatter=None, 
                 display='one-per-axes', **kwargs):
        """Create the data cursor and connect it to the relevant figure.

        Parameters:
        -----------
        *artists*: a matplotlib artist or sequence of artists.
            The artists to make selectable and display information for.
        *tolerance*: number
            The radius (in points) that the mouse click must be within to
            select the artist.
        *offsets*: sequence of two numbers
            A tuple of (x,y) offsets in points from the selected point to the
            displayed annotation box.
        *template*: string
            The format string to be used. Note: this uses "new-style" string
            formatting. This will be ignored if a *formatter* function is
            specified. This will be called as 
            ``template.format(x=x, y=y, label=label, event=event)``, where x &
            y are the data coordinates of the pick event, "label" is the label
            of the artist (as displayed in the legend), and "event" is the pick
            event object.
        *formatter*: function
            A function that accepts the pick event and returns a string that
            will be displayed with annotate. Note that the picked artist can be
            accessed with ``event.artist`` and the x and y coords can be
            accessed with ``event.mouseevent.x``, etc.
        *display*: string
            Controls whether more than one annotation box will be shown.
            Valid values are "single", "one-per-axes", or "mutiple".

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

    def _formatter(self, event):
        """Default formatter function, if no `formatter` kwarg is specified.
        Takes a pick event and returns the text string to be displayed."""
        x, y = event.mouseevent.xdata, event.mouseevent.ydata
        label = event.artist.get_label()
        return self.template.format(x=x, y=y, label=label, event=event)

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
        return annotation

    def _update(self, event, annotation):
        """Update the specified annotation."""
        # Rather than trying to interpolate, just display the clicked coords
        # This will only be called if it's within "tolerance", anyway.
        x, y = event.mouseevent.xdata, event.mouseevent.ydata
        annotation.xy = x, y

        # Update the text using the specified formatter function 
        annotation.set_text(self.formatter(event))

        # In case it's been hidden earlier...
        annotation.set_visible(True)

        event.canvas.draw()

    def __call__(self, event):
        """Create or update annotations for the given event. (This is intended
        to be a callback connected to "pick_event".)"""
        if self.display is not 'multiple':
            annotation = self.annotations[event.artist.axes]
        else:
            annotation = self.annotate(event.artist.axes, 
                                       **self._annotation_kwargs)
            self.annotations[event] = annotation

        if self.display is 'single':
            # Hide any other annotation boxes...
            for ann in self.annotations.values():
                ann.set_visible(False)

        self._update(event, annotation)

class HighlightingDataCursor(DataCursor):
    """A data cursor that highlights the selected Line2D artist."""
    def __init__(self, *args, **kwargs):
        self.highlight_color = kwargs.pop('highlight_color', 'yellow')
        self.highlight_width = kwargs.pop('highlight_width', 3)
        DataCursor.__init__(self, *args, **kwargs)
        self.highlights = {}

    def _update(self, event, annotation):
        for artist in self.highlights.values():
            artist.set_visible(False)
        if event.artist in self.highlights:
            self.highlights[event.artist].set_visible(True)
        else:
            self.highlights[event.artist] = self.highlight(event)
        DataCursor._update(self, event, annotation)
    
    def highlight(self, event):
        highlight = copy.copy(event.artist)
        highlight.set(color=self.highlight_color, lw=self.highlight_width)
        event.artist.axes.add_artist(highlight)
        return highlight

class DraggableDataCursor(DataCursor):
    """
    A data cursor whose annotation box can be dragged to a new position after
    creation.
    """
    def __call__(self, event):
        if event.artist not in self.annotations.values():
            DataCursor.__call__(self, event)
    def annotate(self, ax, **kwargs):
        annotation = DataCursor.annotate(self, ax, **kwargs)
        offsetbox.DraggableAnnotation(annotation)
        return annotation

class ImageDataCursor(DataCursor):
    """
    A data cursor for images displayed with ``imshow``. Displays x, y, and z
    values for a clicked point.  "Z" values are displayed without interpolation.
    """
    def __init__(self, artists, **kwargs):
        default_template = 'x:{x:0.2f}\ny:{y:0.2f}\nz:{z:0.2f}'
        kwargs['template'] = kwargs.pop('template', default_template)
        DataCursor.__init__(self, artists, **kwargs)
    __init__.__doc__ = DataCursor.__init__.__doc__

    def _coords2index(self, im, x, y):
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

    def _formatter(self, event):
        """Default formatter function, if no `formatter` kwarg is specified.
        Takes a pick event and returns the text string to be displayed."""
        x, y = event.mouseevent.xdata, event.mouseevent.ydata
        label = event.artist.get_label()
        i, j = self._coords2index(event.artist, x, y)
        z = event.artist.get_array()[j,i]
        return self.template.format(x=x, y=y, z=z, label=label, event=event)
