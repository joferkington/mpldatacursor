"""
This example demonstrates both draggable annotation boxes and using the
``display="multiple"`` option.
"""
import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import DataCursor

data = np.outer(range(10), range(1, 5))

fig, ax = plt.subplots()
ax.set_title('Try dragging the annotation boxes')
lines = ax.plot(data)

DataCursor(lines, display='multiple', draggable=True)

plt.show()
