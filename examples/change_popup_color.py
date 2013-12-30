import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import datacursor

fig, axes = plt.subplots(ncols=2)

left_artist = axes[0].plot(range(11))
axes[0].set(title='No box, different position', aspect=1.0)

right_artist = axes[1].imshow(np.arange(100).reshape(10,10))
axes[1].set(title='Fancy white background')

# Make the text pop up "underneath" the line and remove the box...
dc1 = datacursor(left_artist, xytext=(15, -15), bbox=None)

# Make the box have a white background with a fancier connecting arrow
dc2 = datacursor(right_artist, bbox=dict(fc='white'),
                 arrowprops=dict(arrowstyle='simple', fc='white', alpha=0.5))

plt.show()
