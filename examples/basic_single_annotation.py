"""An example demonstrating displaying only a single annotation box cursor for
multiple subplots."""
import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import datacursor

plt.figure()

plt.subplot(2,1,1)
plt.title('Note that only one cursor will be displayed for display="single"')
plt.plot(range(10), 'ro-')

plt.subplot(2,1,2)
dat = np.arange(100).reshape((10,10))
plt.plot(range(10), 'bo')

datacursor(display='single')

plt.show()
