"""
This example demonstrates draggable annotation boxes, using the
``display="multiple"`` option and ``magnetic="True"`` option.
Magnetic option will cause pointer to stick to nearest datapoint
instead of anywhere on the line.
"""
import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import datacursor

data = np.outer(range(10), range(1, 5))

fig, ax = plt.subplots()
ax.set_title('Try clicking in between data points')
ax.plot(data, 'o-')

datacursor(display='multiple', draggable=True, magnetic=True)

plt.show()
