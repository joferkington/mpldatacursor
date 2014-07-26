"""
An example of how to customize the keyboard shortcuts.
By default mpldatacursor will use "t" to toggle interactivity and "d" to
hide/delete annotation boxes.
"""
import matplotlib.pyplot as plt
from mpldatacursor import datacursor

fig, ax = plt.subplots()
ax.plot(range(10), 'bo-')
ax.set_title('Press "e" to enable/disable the datacursor\n'
             'Press "h" to hide any annotation boxes')

dc = datacursor(keybindings=dict(hide='h', toggle='e'))

plt.show()
