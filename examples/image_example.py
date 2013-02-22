"""A demonstration of using an ImageDataCursor to display image array values."""
import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import ImageDataCursor

data = np.arange(100).reshape((10,10))

fig, axes = plt.subplots(ncols=2)
im1 = axes[0].imshow(data, interpolation='nearest', origin='lower')
im2 = axes[1].imshow(data, interpolation='nearest', origin='upper',
                     extent=[200, 300, 400, 500])
ImageDataCursor([im1, im2], display='single')

plt.show()
