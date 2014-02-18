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
from matplotlib import cbook
from matplotlib import offsetbox
import copy

from matplotlib.contour import ContourSet
from matplotlib.image import AxesImage
from matplotlib.collections import PathCollection, LineCollection
from matplotlib.collections import PatchCollection, PolyCollection, QuadMesh
from matplotlib.lines import Line2D

import pick_info

class DataCursor(object):
    """A simple data cursor widget that displays the x,y location of a
    matplotlib artist in an annotation box when the artist is clicked on."""

    default_annotation_kwargs = dict(xy=(0, 0), xytext=(-15, 15), ha='right',  
                textcoords='offset points', va='bottom',
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    def __init__(self, artists, tolerance=5, formatter=None, point_labels=None,
                 display='one-per-axes', draggable=False,interpolate_pickpos=True, **kwargs):
        """Create the data cursor and connect it to the relevant figure.

        Parameters
        -----------
        artists : a matplotlib artist or sequence of artists.
            The artists to make selectable and display information for.
        tolerance : number, optional
            The radius (in points) that the mouse click must be within to
            select the artist.
        formatter : function, optional
            A function that accepts arbitrary kwargs and returns a string that
            will be displayed with annotate. The `x`, `y`, `event`, `ind`, and
            `label` kwargs will always be present. See the
            ``mpldatacursor.datacursor`` function docstring for more
            information.
        point_labels : sequence or dict, optional
            Labels for "subitems" of an artist, passed to the formatter
            function as the `point_label` kwarg.  May be either a single
            sequence (used for all artists) or a dict of artist:sequence pairs.
        display : {'one-per-axes', 'single', 'multiple'}, optional
            Controls whether more than one annotation box will be shown.        
        draggable : boolean, optional
            Controls whether or not the annotation box will be interactively
            draggable to a new location after being displayed. Default: False.
        interpolate_pickpos: boolean defines what kind of line pick function to use.
            If set to true the interpolated version will be used.
            If false the nearest point to the left will be picked.            
        **kwargs : additional keyword arguments, optional
            Additional keyword arguments are passed on to annotate.
        """
        #define which kind of line_props to use. 
        #line_props <- easy version
        #line_props_interpolated <- interpolated version
        if (interpolate_pickpos):
            self.line_props = pick_info.line_props_interpolated
        else:
            self.line_props = pick_info.line_props
                    
        def filter_artists(artists):
            """Replace ContourSets with their constituent artists."""
            output = []
            for item in artists:
                if isinstance(item, ContourSet):
                    output += item.collections
                else:
                    output.append(item)
            return output

        if not cbook.iterable(artists):
            artists = [artists]

        #-- Deal with contour sets... -------------------------------------
        # These are particularly difficult, as the original z-value array
        # is never associated with the ContourSet, and they're not "normal"
        # artists (they're not actually added to the axes). Not only that, but
        # the PatchCollections created by filled contours don't even fire a 
        # pick event for points inside them, only on their edges. At any rate,
        # this is a somewhat hackish way of handling contours, but it works.
        self.artists = filter_artists(artists)
        self.contour_levels = {}
        for cs in [x for x in artists if isinstance(x, ContourSet)]:
            for z, artist in zip(cs.levels, cs.collections):
                self.contour_levels[artist] = z

        valid_display_options = ['single', 'one-per-axes', 'multiple']
        if display in valid_display_options:
            self.display = display
        else:
            raise ValueError('"display" must be one of the following: '\
                             ', '.join(valid_display_options))

        self.tolerance = tolerance
        self.point_labels = point_labels
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

        # Timer to control call-rate. 
        def expire_func(ax, *args, **kwargs):
            self.timer_expired[ax] = True
            # Return True to keep callback
            return True

        self.timer_expired = {}
        self.ax_timer = {}
        for ax in self.axes:
            self.ax_timer[ax] = ax.figure.canvas.new_timer(interval=100, 
                                        callbacks=[(expire_func, [ax], {})])
            try:
                self.ax_timer[ax].single_shot = True
            except AttributeError:
                # For mpl <= 1.3.1 with the wxAgg backend, setting the timer to
                # be single_shot will raise an error that can be safely ignored.
                pass
            self.timer_expired[ax] = True
            
        self.enable()

    def event_info(self, event):
        """Get a dict of info for the artist selected by "event"."""
        def default_func(event):
            return {}
        registry = {
                AxesImage : [pick_info.image_props],
                PathCollection : [pick_info.scatter_props, self._contour_info, 
                                  pick_info.collection_props],
                Line2D : [self.line_props],
                LineCollection : [pick_info.collection_props, 
                                  self._contour_info],
                PatchCollection : [pick_info.collection_props, 
                                   self._contour_info],
                PolyCollection : [pick_info.collection_props, 
                                  pick_info.scatter_props],
                QuadMesh : [pick_info.collection_props],
                }
        x, y = event.mouseevent.xdata, event.mouseevent.ydata
        props = dict(x=x, y=y, label=event.artist.get_label(), event=event)
        props['ind'] = getattr(event, 'ind', None)
        props['point_label'] = self._point_label(event)

        funcs = registry.get(type(event.artist), [default_func])
        for func in funcs:
            props.update(func(event))
        return props

    def _point_label(self, event):
        ind = getattr(event, 'ind', None)
        try:
            return [self.point_labels[i] for i in ind]
        except KeyError:
            # Assume self.point_labels is a dict of artist, sequence
            if event.artist in self.point_labels:
                return [self.point_labels[event.artist][i] for i in ind]
        except:
            return None

    def _contour_info(self, event):
        """Get the z-value for a pick event on an artists in a contour set."""
        return {'z':self.contour_levels.get(event.artist, None)}

    def _formatter(self, x=None, y=None, z=None, s=None, label=None, **kwargs):
        """
        Default formatter function, if no `formatter` kwarg is specified. Takes
        information about the pick event as a series of kwargs and returns the
        string to be displayed.
        """
        output = []
        for key, val in zip(['x', 'y', 'z', 's'], [x, y, z, s]):
            if val is not None:
                try:
                    output.append('{key}: {val:0.3g}'.format(key=key, val=val))
                except ValueError:
                    # For masked arrays, etc, "z" value may be a string...
                    output.append('{key}: {val}'.format(key=key, val=val))

        # label may be None or an empty string (for an un-labeled AxesImage)...
        # Un-labeled Line2D's will have labels that start with an underscore
        if label and not label.startswith('_'):
            output.append('Label: {}'.format(label))

        if kwargs.get('point_label', None) is not None:
            output.append('Point: '+', '.join(kwargs['point_label']))

        return '\n'.join(output)

    def annotate(self, ax, **kwargs):
        """
        Draws the annotation box for the given axis *ax*. Additional kwargs
        are passed on to ``annotate``.
        """
        for key in self.default_annotation_kwargs:
            if key not in kwargs:
                kwargs[key] = self.default_annotation_kwargs[key]

        # Make text alignment match the specified offsets (this allows easier
        # changing of relative position of text box...)
        dx, dy = kwargs['xytext']
        horizontal = 'left' if dx > 0 else 'right'
        vertical = 'bottom' if dy > 0 else 'top'
        kwargs['ha'], kwargs['va'] = horizontal, vertical

        annotation = ax.annotate('This text will be reset', **kwargs)

        # Place the annotation in the figure instead of the axes so that it 
        # doesn't get hidden behind other subplots (zorder won't fix that).
        ax.figure.texts.append(ax.texts.pop())

        # Create a draggable annotation box, if required.
        if self.draggable:
            offsetbox.DraggableAnnotation(annotation)

        return annotation

    def hide(self):
        """Hides all annotation artists associated with the DataCursor. Returns
        self to allow "chaining". (e.g. ``datacursor.hide().disable()``)"""
        for artist in self.annotations.values():
            artist.set_visible(False)
        for fig in self.figures:
            fig.canvas.draw()
        return self

    def disable(self):
        """
        Disconnects all callbacks and disables interactivity. Any existing
        annotations will continue to be visible (and draggable, if applicable).
        This has no effect if the datacursor has not been enabled. Returns self
        to allow "chaining". (e.g. ``datacursor.hide().disable()``)
        """
        if self._enabled:
            for fig, cid in self._cids:
                fig.canvas.mpl_disconnect(cid)
            self._enabled = False
        return self

    def enable(self):
        """Connects callbacks and makes artists pickable. If the datacursor has
        already been enabled, this function has no effect."""
        def connect(fig):
            cid = fig.canvas.mpl_connect('pick_event', self)

            # None of this should be necessary. Workaround for a bug in some 
            # mpl versions
            try:
                proxy = fig.canvas.callbacks.BoundMethodProxy(self)
                fig.canvas.callbacks.callbacks['pick_event'][cid] = proxy
            except AttributeError:
                # In some versions of mpl, BoundMethodProxy doesn't exist...
                # See: https://github.com/joferkington/mpldatacursor/issues/2
                pass

            return cid

        if not getattr(self, '_enabled', False):
            self._cids = [(fig, connect(fig)) for fig in self.figures]
            for artist in self.artists:
                artist.set_picker(self.tolerance)
            self._enabled = True
        return self

    def _set_enabled(self, value):
        if value:
            self.enable()
        else:
            self.disable()
    enabled = property(lambda self: self._enabled, _set_enabled, 
                    doc="The interactive state of the datacursor")

    def update(self, event, annotation):
        """Update the specified annotation."""
        # Get artist-specific information about the pick event
        info = self.event_info(event)

        # Update the xy position and text using the formatter function 
        annotation.set_text(self.formatter(**info))
        annotation.xy = info['x'], info['y']

        # In case it's been hidden earlier...
        annotation.set_visible(True)

        event.canvas.draw()

    def __call__(self, event):
        """Create or update annotations for the given event. (This is intended
        to be a callback connected to matplotlib's pick event.)"""
        # Ignore pick events for the annotation box itself (otherwise, 
        # draggable annotation boxes won't work) and pick events not for the
        # artists that this particular data cursor manages.
        if event.artist not in self.artists:
            return

        # Return if multiple events are firing 
        ax = event.artist.axes
        if not self.timer_expired[ax]:
            return
        self.timer_expired[ax] = False
        self.ax_timer[ax].start()
        
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

        Parameters
        ----------
        highlight_color : a valid color specifier (string or tuple), optional
            The color to set the highlighted artist to. Default: yellow
        highlight_width : number, optional
            The width of the highlighted artist. Default: 3
        """
        self.highlight_color = kwargs.pop('highlight_color', 'yellow')
        self.highlight_width = kwargs.pop('highlight_width', 3)
        DataCursor.__init__(self, *args, **kwargs)
        self.highlights = {}

    def update(self, event, annotation):
        """Update the specified annotation."""
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
