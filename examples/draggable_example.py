"""
This example demonstrates both draggable annotation boxes and using the
``display="multiple"`` option.
"""
import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import datacursor

data = np.outer(range(10), range(1, 5))

fig, ax = plt.subplots()
ax.set_title('Try dragging the annotation boxes')
ax.plot(data)

datacursor(display='multiple', draggable=True)

plt.show()
