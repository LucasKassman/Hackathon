#
# Testing mechanism to display a graph of points
# requires matplotlib ("pip install -U matplotlib" from within your pythen env)

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, CheckButtons


mydata = {"server1":{"timestamps":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "goodness":[2.3, 2.4, 2.3, 2.4, 2.5, 2.3, 2.8, 2.0, 2.3, 2.3]},
          "server2":{"timestamps":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "goodness":[2.0, 3.4, 1.3, 5.4, 3.5, 2.3, 4.8, 4.0, 3.3, 2.3]},
          "server3":{"timestamps":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "goodness":[5.3, 5.4, 5.3, 5.4, 5.5, 5.3, 5.8, 5.0, 5.3, 5.3]},
          "server4":{"timestamps":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "goodness":[1.3, 1.4, 1.3, 1.4, 1.5, 1.3, 1.8, 1.0, 1.3, 1.3]}}

colors_list = ['red','green','blue','purple','black'] # one color per server

fig = plt.figure()
ax = fig.subplots()

# the plots will be in the upper left section of the window, 30% reserved on right and 25% on bottom (I think!) 
plt.subplots_adjust(right = 0.7, bottom = 0.25)

i=0
plots=[]
labels=[]

# only make the first server visible by default
bVisible=True

for server in mydata:
    p, = ax.plot(mydata[server]['timestamps'],mydata[server]['goodness'],colors_list[i])
    p.set_visible(bVisible)
    labels.append(server)
    plots.append(p)
    bVisible=False  # all others will be hidden
    i = i + 1

activated = [True, False, False, False]

# [left/right, up/down, h, v size]
# played around with this until something looked okay.  TBD:  Vertical position and size should be calculated based on number of servers being displayed.
ax_check = plt.axes([0.75, 0.40, 0.15, 0.3])

plot_button = CheckButtons(ax_check, labels, activated)

# change the colors of the checkboxes to match the lines in the plots:
[rec.set_facecolor(colors_list[i]) for i, rec in enumerate(plot_button.rectangles)]

# handle plot_button clicks by toggling the visibility of the specific server
def select_plot(label):
    index = labels.index(label)
    plots[index].set_visible(not plots[index].get_visible())
    fig.canvas.draw()

# link above fn to "on_clicked" action
plot_button.on_clicked(select_plot)

# this is a blocking call, will return when user closes the window.  Played with show(blocked=False) but didn't draw right.  Will retry later.
plt.show()
