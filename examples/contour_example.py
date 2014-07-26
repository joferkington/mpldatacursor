import numpy as np
import matplotlib.pyplot as plt
from mpldatacursor import datacursor

fig, ax = plt.subplots()
cf = ax.contour(np.random.random((10,10)))
# For contours, you'll have to explicitly specify the ContourSet ("cf", in this
# case) for the z-values to be displayed. Filled contours aren't properly
# supported, as they only fire a pick even when their edges are selected.
datacursor(cf)
plt.show()
