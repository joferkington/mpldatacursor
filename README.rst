mpldatacursor
============
``mpldatacursor`` provides interactive "data cursors" (clickable annotation
boxes) for matplotlib. 

Major Changes in Version 0.2
----------------------------

Version 0.2 introduces the ``datacursor`` convenience function, which is now
the recommended way of initializing ``DataCursor``'s.  Additionally, the
``ImageDataCursor`` class has been removed, and its functionality has been
incorporated into ``DataCursor``.

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

        HighlightingDataCursor(lines, formatter='{label}'.format)

        plt.show()

.. image:: http://joferkington.github.com/mpldatacursor/images/highlighting_example.png
    :align: center
    :target: https://github.com/joferkington/mpldatacursor/blob/master/examples/highlighting_example.py


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


Installation
------------
``mpldatacursor`` can be installed from PyPi using
``easy_install``/``pip``/etc. (e.g. ``pip install mpldatacursor``) or you may
download the source and install it directly with ``python setup.py install``.

