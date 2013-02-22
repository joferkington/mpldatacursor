mpldatacursor
============
``mpldatacursor`` provides interactive "data cursors" (clickable annotation boxes) for matplotlib.

Basic Usage
-----------
``mpldatacursor`` offers a few different styles of interaction. The basic
``DataCursor`` displays the x, y coordinates of the selected artist in an
annotation box.  ``DraggableDataCursor`` allows the annotation box to be
dragged to a new position after creation, and ``HighlightingDataCursor``
highlights a ``Line2D`` artist in addition to displaying the selected
coordinates. Selected image values can be displayed using ``ImageDataCursor``. 

As an example::

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
