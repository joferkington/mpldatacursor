"""
Display an artist's label instead of x,y coordinates. An example of using the
"formatter" kwarg to DataCursor.
"""
import numpy as np
import matplotlib.pyplot as plt
from mpldatacursor import DataCursor

x = np.linspace(0, 10, 100)

fig, ax = plt.subplots()

# Plot a series of lines with increasing slopes...
lines = []
for i in range(1, 20):
    line, = ax.plot(x, i * x, label='$y = {}x$'.format(i))
    lines.append(line)

# Use a DataCursor to interactively display the label for a selected line...
DataCursor(lines, template='{label}')

plt.show()
