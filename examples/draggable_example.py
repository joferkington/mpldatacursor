import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import DraggableDataCursor

data = np.outer(range(10), range(1, 5))

fig, ax = plt.subplots()
ax.set_title('Try dragging the annotation boxes')
lines = ax.plot(data)

DraggableDataCursor(lines, display='multiple')

plt.show()
