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
import copy
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cbook
from matplotlib import offsetbox

from matplotlib.contour import ContourSet
from matplotlib.image import AxesImage
from matplotlib.collections import PathCollection, LineCollection
from matplotlib.collections import PatchCollection, PolyCollection, QuadMesh
from matplotlib.container import Container
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib.dates as mdates

from . import pick_info

class DataCursor(object):
    """A simple data cursor widget that displays the x,y location of a
    matplotlib artist in an annotation box when the artist is clicked on."""

    default_annotation_kwargs = dict(xy=(0, 0), xytext=(-15, 15),
                textcoords='offset points', picker=True,
                bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5,
                          edgecolor='black'),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0',
                                edgecolor='black'),
                )

    default_keybindings = dict(hide='d', toggle='t')

    def __init__(self, artists, tolerance=5, formatter=None, point_labels=None,
                display='one-per-axes', draggable=False, hover=False,
                props_override=None, keybindings=True, date_format='%x %X',
		display_button=1, hide_button=3,
                **kwargs):
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
        hover : boolean, optional
            If True, the datacursor will "pop up" when the mouse hovers over an
            artist.  Defaults to False.  Enabling hover also sets
            `display="single"` and `draggable=False`.
        props_override : function, optional
            If specified, this function customizes the parameters passed into
            the formatter function and the x, y location that the datacursor
            "pop up" "points" to.  This is often useful to make the annotation
            "point" to a specific side or corner of an artist, regardless of
            the position clicked. The function is passed the same kwargs as the
            `formatter` function and is expected to return a dict with at least
            the keys "x" and "y" (and probably several others).
            Expected call signature: `props_dict = props_override(**kwargs)`
        keybindings : boolean or dict, optional
            By default, the keys "d" and "t" will be bound to deleting/hiding
            all annotation boxes and toggling interactivity for datacursors,
            respectively.  If keybindings is False, the ability to hide/toggle
            datacursors interactively will be disabled. Alternatively, a dict
            of the form {'hide':'somekey', 'toggle':'somekey'} may specified to
            customize the keyboard shortcuts.
        date_format : string, optional
            The strftime-style formatting string for dates. Used only if the x
            or y axes have been set to display dates. Defaults to "%x %X".
        display_button: int, optional
            The mouse button that will triggers displaying an annotation box.
            Defaults to 1, for left-clicking. (Common options are
            1:left-click, 2:middle-click, 3:right-click)
        hide_button: int or None, optional
            The mouse button that triggers hiding the selected annotation box.
            Defaults to 3, for right-clicking. (Common options are
            1:left-click, 2:middle-click, 3:right-click, None:hiding disabled)
        **kwargs : additional keyword arguments, optional
            Additional keyword arguments are passed on to annotate.
        """
        def filter_artists(artists):
            """Replace ContourSets, etc with their constituent artists."""
            output = []
            for item in artists:
                if isinstance(item, ContourSet):
                    output += item.collections
                elif isinstance(item, Container):
                    children = item.get_children()
                    for child in children:
                        child._mpldatacursor_label = item.get_label()
                    output += children
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
        self.hover = hover
        if self.hover:
            self.display = 'single'
            self.draggable = False

        self.tolerance = tolerance
        self.point_labels = point_labels
        self.draggable = draggable
        self.date_format = date_format
        self.props_override = props_override
        self.display_button = display_button
        self.hide_button = hide_button
        self.axes = tuple(set(art.axes for art in self.artists))
        self.figures = tuple(set(ax.figure for ax in self.axes))

        if formatter is None:
            self.formatter = self._formatter
        else:
            self.formatter = formatter

        self._annotation_kwargs = kwargs
        self.annotations = {}
        if self.display is not 'multiple':
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
            interval = 300 if self.hover else 100
            self.ax_timer[ax] = ax.figure.canvas.new_timer(interval=interval,
                                        callbacks=[(expire_func, [ax], {})])
            try:
                if plt.get_backend() != 'MacOSX':
                    # Single-shot timers on the OSX backend segfault!
                    self.ax_timer[ax].single_shot = True
            except AttributeError:
                # For mpl <= 1.3.1 with the wxAgg backend, setting the
                # timer to be single_shot will raise an error that can be
                # safely ignored.
                pass
            self.timer_expired[ax] = True

        if keybindings:
            if keybindings is True:
                self.keybindings = self.default_keybindings
            else:
                self.keybindings = keybindings
            for fig in self.figures:
                fig.canvas.mpl_connect('key_press_event', self._on_keypress)

        self.enable()

    def __call__(self, event):
        """Create or update annotations for the given event. (This is intended
        to be a callback connected to matplotlib's pick event.)"""
        # Hide the selected annotation box if it's clicked with "hide_button".
        if (event.artist in self.annotations.values() and
            event.mouseevent.button == self.hide_button):
            self._hide_box(event.artist)

        elif not self._event_ignored(event):
            # Otherwise, start a timer and show the annotation box
            self.timer_expired[event.artist.axes] = False
            self.ax_timer[event.artist.axes].start()
            self._show_annotation_box(event)

    def _event_ignored(self, event):
        """Decide whether or not to ignore a click/hover event."""
        # Ignore non-hiding pick events for the annotation box itself
        # (otherwise, draggable annotation boxes won't work) and pick
        # events not for the artists that this data cursor manages.
        if event.artist not in self.artists:
            return True

        if not self.hover:
            # Ignore pick events from other mouse buttons
            if event.mouseevent.button != self.display_button:
                return True

            # Return if multiple events are firing
            if not self.timer_expired[event.artist.axes]:
                return True
        return False

    def _show_annotation_box(self, event):
        """Update an existing box or create an annotation box for an event."""
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

    def event_info(self, event):
        """Get a dict of info for the artist selected by "event"."""
        def default_func(event):
            return {}
        registry = {
                AxesImage : [pick_info.image_props],
                PathCollection : [pick_info.scatter_props, self._contour_info,
                                  pick_info.collection_props],
                Line2D : [pick_info.line_props],
                LineCollection : [pick_info.collection_props,
                                  self._contour_info],
                PatchCollection : [pick_info.collection_props,
                                   self._contour_info],
                PolyCollection : [pick_info.collection_props,
                                  pick_info.scatter_props],
                QuadMesh : [pick_info.collection_props],
                Rectangle : [pick_info.rectangle_props],
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
        def is_date(axis):
            fmt = axis.get_major_formatter()
            return (isinstance(fmt, mdates.DateFormatter)
                 or isinstance(fmt, mdates.AutoDateFormatter))
        def format_date(num):
            return mdates.num2date(num).strftime(self.date_format)
        ax = kwargs['event'].mouseevent.inaxes
        if is_date(ax.xaxis):
            x = format_date(x)
        if is_date(ax.yaxis):
            y = format_date(y)

        output = []
        for key, val in zip(['x', 'y', 'z', 's'], [x, y, z, s]):
            if val is not None:
                try:
                    output.append(u'{key}: {val:0.3g}'.format(key=key, val=val))
                except ValueError:
                    # For masked arrays, etc, "z" value may be a string...
                    # Similarly, x or y will be strings if they are dates.
                    output.append(u'{key}: {val}'.format(key=key, val=val))

        # label may be None or an empty string (for an un-labeled AxesImage)...
        # Un-labeled Line2D's will have labels that start with an underscore
        if label and not label.startswith('_'):
            output.append(u'Label: {}'.format(label))

        if kwargs.get(u'point_label', None) is not None:
            output.append(u'Point: ' + u', '.join(kwargs['point_label']))

        return u'\n'.join(output)

    def annotate(self, ax, **kwargs):
        """
        Draws the annotation box for the given axis *ax*. Additional kwargs
        are passed on to ``annotate``.
        """
        def update_from_defaults(key, kwargs):
            if kwargs.get(key, None) is not None:
                new = copy.deepcopy(self.default_annotation_kwargs[key])
                new.update(kwargs[key])
                kwargs[key] = new
            return kwargs

        user_set_ha = 'ha' in kwargs or 'horizontalalignment' in kwargs
        user_set_va = 'va' in kwargs or 'verticalalignment' in kwargs

        # Ensure bbox and arrowstyle params passed in use the defaults for
        # DataCursor. This allows things like ``bbox=dict(alpha=1)`` to show a
        # yellow, rounded box, instead of the mpl default blue, square box.)
        kwargs = update_from_defaults('bbox', kwargs)
        kwargs = update_from_defaults('arrowstyle', kwargs)

        # Set defaults where approriate.
        for key in self.default_annotation_kwargs:
            if key not in kwargs:
                kwargs[key] = self.default_annotation_kwargs[key]

        # Make text alignment match the specified offsets (this allows easier
        # changing of relative position of text box...)
        dx, dy = kwargs['xytext']
        horizontal = {1:'left', 0:'center', -1:'right'}[np.sign(dx)]
        vertical = {1:'bottom', 0:'center', -1:'top'}[np.sign(dy)]
        if not user_set_ha:
            kwargs['ha'] = horizontal
        if not user_set_va:
            kwargs['va'] = vertical

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

    def _hide_box(self, annotation):
        """Hide a specific annotation box."""
        annotation.set_visible(False)
        annotation.figure.canvas.draw()

    def disable(self):
        """
        Disconnects all callbacks and disables interactivity. Any existing
        annotations will continue to be visible (and draggable, if applicable).
        This has no effect if the datacursor has not been enabled. Returns self
        to allow "chaining". (e.g. ``datacursor.hide().disable()``)
        """
        if self._enabled:
            for fig, cids in self._cids:
                for cid in cids:
                    fig.canvas.mpl_disconnect(cid)
            self._enabled = False
        return self

    def enable(self):
        """Connects callbacks and makes artists pickable. If the datacursor has
        already been enabled, this function has no effect."""
        def connect(fig):
            if self.hover:
                event = 'motion_notify_event'
            else:
                event = 'button_press_event'
            cids = [fig.canvas.mpl_connect(event, self._select)]
            cids.append(fig.canvas.mpl_connect('pick_event', self))

            # None of this should be necessary. Workaround for a bug in some
            # mpl versions
            try:
                proxy = fig.canvas.callbacks.BoundMethodProxy(self)
                fig.canvas.callbacks.callbacks[event][cids[-1]] = proxy
            except AttributeError:
                # In some versions of mpl, BoundMethodProxy doesn't exist...
                # See: https://github.com/joferkington/mpldatacursor/issues/2
                pass
            return cids

        if not getattr(self, '_enabled', False):
            self._cids = [(fig, connect(fig)) for fig in self.figures]
            for artist in self.artists:
                artist.set_picker(self.tolerance)
            for annotation in self.annotations.values():
                # Annotation boxes need to be pickable so we can hide them on
                # right-click (or whatever self.hide_button is).
                annotation.set_picker(self.tolerance)
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

        if self.props_override is not None:
            info = self.props_override(**info)

        # Update the xy position and text using the formatter function
        annotation.set_text(self.formatter(**info))
        annotation.xy = info['x'], info['y']

        # In case it's been hidden earlier...
        annotation.set_visible(True)

        event.canvas.draw()

    def _on_keypress(self, event):
        if event.key == self.keybindings['hide']:
            self.hide()
        if event.key == self.keybindings['toggle']:
            self.enabled = not self.enabled

    def _select(self, event):
        """This is basically a proxy to trigger a pick event.  This function is
        connected to either a mouse motion or mouse button event (see
        "self.enable") depending on "self.hover". If we're over a point, it
        fires a pick event.

        This probably seems bizarre, but it's required for hover mode (no mouse
        click) and otherwise it's a workaround for picking artists in twinned
        or overlapping axes.

        Even if we're not in hover mode, pick events won't work properly for
        twinned axes.  Therefore, we manually go through all artists managed by
        this datacursor and fire a pick event if the mouse is over an a managed
        artist."""
        for artist in self.artists:
            # We need to redefine event.xdata and event.ydata for twinned axes
            # to work correctly
            point = event.x, event.y
            x, y = artist.axes.transData.inverted().transform_point(point)
            event = copy.copy(event)
            event.xdata, event.ydata = x, y
            artist.pick(event)

        from itertools import chain
        all_artists = chain(self.artists, self.annotations.values())
        over_something = [x.contains(event)[0] for x in all_artists]

        if any(self.timer_expired.values()) and not self.draggable:
            # Not hovering over anything...
            if not any(over_something) and self.hover:
                self.hide()

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
