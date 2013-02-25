mpldatacursor
============
``mpldatacursor`` provides interactive "data cursors" (clickable annotation
boxes) for matplotlib. 

Basic Usage
-----------
``mpldatacursor`` offers a few different styles of interaction. The basic
``DataCursor`` displays the x, y coordinates of the selected artist in an
annotation box.  

As an example::

        import matplotlib.pyplot as plt
        import numpy as np
        from mpldatacursor import DataCursor

        data = np.outer(range(10), range(1, 5))

        fig, ax = plt.subplots()
        lines = ax.plot(data)
        ax.set_title('Click somewhere on a line')

        DataCursor(lines)

        plt.show()

.. image:: http://joferkington.github.com/mpldatacursor/images/basic.png
    :align: center
    :target: https://github.com/joferkington/mpldatacursor/blob/master/examples/basic.py

The displayed text can be controlled either by using a template string (the
``template`` kwarg) or by passing a function that accepts a pick event and
returns the string to be displayed (the ``formatter`` kwarg).

As an example of using the ``template`` kwarg to display the label of the
artist instead of the x, y coordinates::

        import numpy as np
        import matplotlib.pyplot as plt
        from mpldatacursor import DataCursor

        x = np.linspace(0, 10, 100)

        fig, ax = plt.subplots()
        ax.set_title('Click on a line to display its label')

        # Plot a series of lines with increasing slopes...
        lines = []
        for i in range(1, 20):
            line, = ax.plot(x, i * x, label='$y = {}x$'.format(i))
            lines.append(line)

        # Use a DataCursor to interactively display the label for a selected line...
        DataCursor(lines, template='{label}')

        plt.show()

.. image:: http://joferkington.github.com/mpldatacursor/images/show_artist_labels.png
    :align: center
    :target: https://github.com/joferkington/mpldatacursor/blob/master/examples/show_artist_labels.py

``DraggableDataCursor`` allows the annotation box to be
dragged to a new position after creation.

As an example (This also demonstrates using the ``display='multiple'`` kwarg
that all data cursors accept.)::

        import matplotlib.pyplot as plt
        import numpy as np
        from mpldatacursor import DraggableDataCursor

        data = np.outer(range(10), range(1, 5))

        fig, ax = plt.subplots()
        ax.set_title('Try dragging the annotation boxes')
        lines = ax.plot(data)

        DraggableDataCursor(lines, display='multiple')

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

        HighlightingDataCursor(lines, template='{label}')

        plt.show()

.. image:: http://joferkington.github.com/mpldatacursor/images/highlighting_example.png
    :align: center
    :target: https://github.com/joferkington/mpldatacursor/blob/master/examples/highlighting_example.py


The array value at the selected point in an image can be displayed using
``ImageDataCursor``. This example also demonstrates using the
``display="single"`` option to display only one data cursor instead of
one-per-axes.::

        import matplotlib.pyplot as plt
        import numpy as np
        from mpldatacursor import ImageDataCursor

        data = np.arange(100).reshape((10,10))

        fig, axes = plt.subplots(ncols=2)
        im1 = axes[0].imshow(data, interpolation='nearest', origin='lower')
        im2 = axes[1].imshow(data, interpolation='nearest', origin='upper',
                             extent=[200, 300, 400, 500])
        ImageDataCursor([im1, im2], display='single')

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

