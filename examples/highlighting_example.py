"""
An example of using a HighlightingDataCursor along with a custom formatter
formatter function to highlight the selected artist and display its label.
"""
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
