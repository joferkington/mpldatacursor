import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mpldatacursor import datacursor

# Make an example plot...
t = mdates.drange(dt.datetime(2014, 1, 15), dt.datetime(2014, 2, 27),
                          dt.timedelta(hours=2))
y = np.sin(t)
fig, ax = plt.subplots()
ax.plot_date(t, y, 'b-')
fig.autofmt_xdate()

# Note that mpldatacursor will automatically display the x-values as dates.
datacursor()

# If we wanted to display only the day, we could do
# datacursor(date_format='%x') #<-- strftime format string

plt.show()
