import matplotlib.pyplot as plt
import numpy as np
from mpldatacursor import datacursor

fig, axes = plt.subplots(ncols=2)

left_artist = axes[0].plot(range(10))
axes[0].set(title='Left datacursor will be to the lower'
                  '\nright and not have a background')

right_artist = axes[1].imshow(np.arange(100).reshape(10,10))
axes[1].set(title='Right datacursor will have\na fancy white background')

# Make the text pop up "underneath" the line and remove the box...
dc1 = datacursor(left_artist, xytext=(15, -15), bbox=None)

# Make the box have a white background with a fancier connecting arrow
dc2 = datacursor(right_artist, 
             arrowprops=dict(arrowstyle='simple', fc='white', alpha=0.5),
             bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.5))

plt.show()
