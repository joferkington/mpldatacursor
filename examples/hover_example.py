"""A very basic exmaple of the hover functionality of mpldatacursor."""
import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import datacursor

x, y = np.random.random((2, 6))
labels = ['a', 'b', 'c', 'd', 'e', 'f']

fig, ax = plt.subplots()
ax.scatter(x, y, s=200)
ax.set_title('Mouse over a point')

datacursor(hover=True, point_labels=labels)

plt.show()
