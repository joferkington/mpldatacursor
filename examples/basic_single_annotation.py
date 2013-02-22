"""An example demonstrating displaying only a single annotation box cursor for 
multiple subplots."""
import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import DataCursor

plt.figure()

plt.subplot(2,1,1)
plt.title('Note that only one cursor will be displayed for display="single"')
line1, = plt.plot(range(10), 'ro-')

plt.subplot(2,1,2)
dat = np.arange(100).reshape((10,10))
line2, = plt.plot(range(10), 'bo')

DataCursor((line1, line2), display='single')

plt.show()
