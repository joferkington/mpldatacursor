"""
An example of how to set up toggling of interactivity.
"""
import matplotlib.pyplot as plt
from mpldatacursor import datacursor

fig, ax = plt.subplots()
ax.plot(range(10), 'bo-')
ax.set_title('Press "e" to enable/disable the datacursor\n'
             'Press "w" to hide any annotation boxes')

dc = datacursor()

def toggle(event):
    if event.key == 'e':
        dc.enabled = not dc.enabled
    if event.key == 'w':
        dc.hide()
fig.canvas.mpl_connect('key_press_event', toggle)

plt.show()
