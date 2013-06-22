"""
Illustrates "point label" functionality.
"""
import matplotlib.pyplot as plt
from mpldatacursor import datacursor

labels = ['a', 'b', 'c', 'd', 'e', 'f']
x = [0, 0.05, 1, 2, 3, 4]

# All points on this figure will point labels.
fig, ax = plt.subplots()
ax.plot(x, x, 'ro')
ax.margins(0.1)
datacursor(axes=ax, point_labels=labels)

# Only the blue points will have point labels on this figure.
fig, ax = plt.subplots()
line, = ax.plot(x, range(6), 'bo')
ax.plot(range(5), 'go')
ax.margins(0.1)
datacursor(axes=ax, point_labels={line:labels})

plt.show()

