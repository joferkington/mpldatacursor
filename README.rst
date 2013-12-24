mpldatacursor
============
``mpldatacursor`` provides interactive "data cursors" (clickable annotation
boxes) for matplotlib. 

v0.4.2
------
Version 0.4.2 adds a workaround for a bug in the OSX backend that would
otherwise cause a segfault.

v0.4.1
------
Version 0.4.1 fixes a bug that prevented compatibility with matplotlib-1.3.

Major Changes in v0.4
---------------------
Version 0.4 adds:

* The ``point_labels`` kwarg.
  For displaying a separate label for each sub-artist of "indexed" artists
  (e.g. each point of a scatter plot). See:
  ``examples/labeled_points_example.py``

* Hiding and disabling functionality.
  The methods ``datacursor.enable``, ``datacursor.disable``, and
  ``datacursor.hide`` now respectively enable and disable interactivity and
  hide all visible datacursor "popups".

* Major bug-fixes for images.
  Non-square images previously had the wrong values displayed in many cases.
  Additionally, masked and non-scalar (e.g. R,G,B) images are now properly
  supported.

* Rate-limit on re-drawing the figure.
  This avoids the "animation effect" when multiple artists are selected. Many
  thanks to Ehsan Azar for the implementation.

Basic Usage
-----------
``mpldatacursor`` offers a few different styles of interaction through the 
``datacursor`` function. 

As an example, this displays the x, y coordinates of the selected artist in an
annotation box::

        import matplotlib.pyplot as plt
        import numpy as np
        from mpldatacursor import datacursor

        data = np.outer(range(10), range(1, 5))

        fig, ax = plt.subplots()
        lines = ax.plot(data)
        ax.set_title('Click somewhere on a line')

        datacursor(lines)

        plt.show()

.. image:: http://joferkington.github.com/mpldatacursor/images/basic.png
    :align: center
    :target: https://github.com/joferkington/mpldatacursor/blob/master/examples/basic.py

If no artist or sequence of artists is specified, all manually plotted artists
in all axes in all figures will be activated. (This can be limited to only
certain axes by passing in an axes object or a sequence of axes to the ``axes``
kwarg.)

As an example (the output is identical to the first example)::

        import matplotlib.pyplot as plt
        import numpy as np
        from mpldatacursor import datacursor

        data = np.outer(range(10), range(1, 5))

        plt.plot(data)
        plt.title('Click somewhere on a line')

        datacursor()

        plt.show()

Controlling the Displayed Text
------------------------------
The displayed text can be controlled either by using the ``formatter`` kwarg, 
which expects a function that accepts an arbitrary sequence of kwargs and
returns the string to be displayed. Often, it's convenient to pass in the
``format`` method of a template string (e.g. 
``formatter="longitude:{x:.2f}\nlatitude{y:.2f}".format``).

As an example of using the ``formatter`` kwarg to display only the label of the
artist instead of the x, y coordinates::

        import numpy as np
        import matplotlib.pyplot as plt
        from mpldatacursor import datacursor

        x = np.linspace(0, 10, 100)

        fig, ax = plt.subplots()
        ax.set_title('Click on a line to display its label')

        # Plot a series of lines with increasing slopes...
        for i in range(1, 20):
            ax.plot(x, i * x, label='$y = {}x$'.format(i))

        # Use a DataCursor to interactively display the label for a selected line...
        datacursor(formatter='{label}'.format)

        plt.show()

.. image:: http://joferkington.github.com/mpldatacursor/images/show_artist_labels.png
    :align: center
    :target: https://github.com/joferkington/mpldatacursor/blob/master/examples/show_artist_labels.py

Working with Images
-------------------
``datacursor`` will also display the array value at the selected point in an
image. This example also demonstrates using the ``display="single"`` option to
display only one data cursor instead of one-per-axes.::

        import matplotlib.pyplot as plt
        import numpy as np
        from mpldatacursor import datacursor

        data = np.arange(100).reshape((10,10))

        fig, axes = plt.subplots(ncols=2)
        axes[0].imshow(data, interpolation='nearest', origin='lower')
        axes[1].imshow(data, interpolation='nearest', origin='upper',
                             extent=[200, 300, 400, 500])
        datacursor(display='single')

        fig.suptitle('Click anywhere on the image')

        plt.show()

.. image:: http://joferkington.github.com/mpldatacursor/images/image_example.png
    :align: center
    :target: https://github.com/joferkington/mpldatacursor/blob/master/examples/image_example.py

Draggable Boxes
---------------
If ``draggable=True`` is specified, the annotation box can be interactively
dragged to a new position after creation.

As an example (This also demonstrates using the ``display='multiple'`` kwarg)::

        import matplotlib.pyplot as plt
        import numpy as np
        from mpldatacursor import datacursor

        data = np.outer(range(10), range(1, 5))

        fig, ax = plt.subplots()
        ax.set_title('Try dragging the annotation boxes')
        ax.plot(data)

        datacursor(display='multiple', draggable=True)

        plt.show()

.. image:: http://joferkington.github.com/mpldatacursor/images/draggable_example.png
    :align: center
    :target: https://github.com/joferkington/mpldatacursor/blob/master/examples/draggable_example.py

Further Customization
---------------------
Additional keyword arguments to ``datacursor`` are passed on to ``annotate``.
This allows one to control the appearance and location of the "popup box",
arrow, etc.  As a basic example::

        import matplotlib.pyplot as plt
        import numpy as np
        from mpldatacursor import datacursor

        fig, axes = plt.subplots(ncols=2)

        left_artist = axes[0].plot(range(11))
        axes[0].set(title='No box, different position', aspect=1.0)

        right_artist = axes[1].imshow(np.arange(100).reshape(10,10))
        axes[1].set(title='Fancy white background')

        # Make the text pop up "underneath" the line and remove the box...
        dc1 = datacursor(left_artist, xytext=(15, -15), bbox=None)

        # Make the box have a white background with a fancier connecting arrow
        dc2 = datacursor(right_artist, 
                     arrowprops=dict(arrowstyle='simple', fc='white', alpha=0.5),
                     bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.5))

        plt.show()

.. image:: http://joferkington.github.com/mpldatacursor/images/change_popup_color.png
    :align: center
    :target: https://github.com/joferkington/mpldatacursor/blob/master/examples/change_popup_color.py

Highlighting Selected Lines
---------------------------
``HighlightingDataCursor`` highlights a ``Line2D`` artist in addition to
displaying the selected coordinates.::

        import numpy as np
        import matplotlib.pyplot as plt
        from mpldatacursor import HighlightingDataCursor

        x = np.linspace(0, 10, 100)

        fig, ax = plt.subplots()

        # Plot a series of lines with increasing slopes...
        lines = []
        for i in range(1, 20):
            line, = ax.plot(x, i * x, label='$y = {}x$'.format(i))
            lines.append(line)

        HighlightingDataCursor(lines)

        plt.show()

.. image:: http://joferkington.github.com/mpldatacursor/images/highlighting_example.png
    :align: center
    :target: https://github.com/joferkington/mpldatacursor/blob/master/examples/highlighting_example.py

Installation
------------
``mpldatacursor`` can be installed from PyPi using
``easy_install``/``pip``/etc. (e.g. ``pip install mpldatacursor``) or you may
download the source and install it directly with ``python setup.py install``.

