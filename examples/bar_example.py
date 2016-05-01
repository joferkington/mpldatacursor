"""
A bar plot where each bar's height and name will be displayed above the top of
the bar when it is moused over.  This serves as an example of overriding the
x,y position of the "popup" annotation using the `props_override` option.
"""
import string
import matplotlib.pyplot as plt
from mpldatacursor import datacursor

fig, ax = plt.subplots()
ax.bar(range(9), range(1, 10), align='center')
labels = string.ascii_uppercase[:9]
ax.set(xticks=range(9), xticklabels=labels, title='Hover over a bar')

# By default, the "popup" annotation will appear at the mouse's position.
# Instead, you might want it to appear centered at the top of the rectangle in
# the bar plot. By changing the x and y values using the "props_override"
# option, we can customize where the "popup" appears.
def override(**kwargs):
    kwargs['x'] = kwargs['xcenter']
    kwargs['y'] = kwargs['top']
    kwargs['label'] = labels[int(kwargs['x'])]
    return kwargs

datacursor(hover=True, xytext=(0, 20), props_override=override,
           formatter='{label}: {height}'.format)

plt.show()
