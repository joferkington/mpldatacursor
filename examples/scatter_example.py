import numpy as np
import matplotlib.pyplot as plt
import mpldatacursor

x, y, z = np.random.random((3, 10))
fig, ax = plt.subplots()
artist = ax.scatter(x, y, c=z, s=100)
mpldatacursor.ScatterDataCursor(artist)
plt.show()
