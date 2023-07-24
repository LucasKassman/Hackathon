#
# Testing mechanism to display a graph of points
# requires matplotlib ("pip install -U matplotlib" from within your pythen env)

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons, CheckButtons

#import tkinter as tk

current_color = 0
colors_list = ['red','green','blue','purple','black',
                   'tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan'
                ]

class Server():
    def __init__(self, ax, label, ave, times, pings, color=None, bFirst=True, bPlotHLine=True):
        global current_color
        if color == None:
            color = colors_list[current_color]
            current_color = (current_color+1) % (len(colors_list))
            p, = ax.plot(times,pings)
            color = p.get_color()
        else:
            p, = ax.plot(times,pings,color)
        p.set_visible(bFirst)
            
        #
        # Optionally create the horizontal line
        if bPlotHLine:
            hline = ax.hlines(ave, xmin=min(times), xmax=max(times),colors=[color])
            hline.set_visible(bFirst)
        else:
            hline = None

        self.label = label
        self.plot  = p
        self.bActivated = bFirst
        self.color = color
        self.hline = hline
        self.ylimits = [min(pings), max(pings)]

        #temp for debug
        self.pings=pings
        self.times=times
        
class Grapher():
    def __init__(self, title):
        super().__init__()
        #root = tk.Tk()
        self.fig = plt.figure(title, figsize=(12,10))
        self.ax = self.fig.subplots()
        self.bFirstItem = True
        self.servers = {}
        #plt.subplots_adjust(right = 0.7, top = 0.75)
        plt.subplots_adjust(top = 0.84)
        self.yminmax = (float('inf'), 0.0)

    # the y axis will always have a minimum of at least limits[0], and a maximum of limits[1]
    def setYminmax(self, limits):
        self.yminmax = limits



    def cleanData(self, times, pings):
        
        newtimes = []
        newpings = []
        j=0
        for p in pings:
            if p != None:
                newtimes.append(times[j])
                newpings.append(p)
            j = j+1
                
        return newtimes, newpings



    def addData(self, server_name, ave, times, pings, color=None):
        server = server_name+(" (%.2f)"%ave) # append the average to the displayed name

        times, pings = self.cleanData(times, pings)

        if not server in self.servers:
            self.servers[server] = Server(label=server, ax=self.ax, ave=ave, times=times, pings=pings, color=color, bFirst=self.bFirstItem)

        self.bFirstItem = False

    # fudge  = % of max y axis limits to increase +/-
    def setYLimits(self, fudge=0.02):
        # set the y axis based on min/max Y for visible servers
        miny = float('inf')
        maxy = 0

        for s in self.servers:
            if self.servers[s].plot.get_visible():
                ylims = self.servers[s].ylimits
                miny = min([miny, ylims[0], self.yminmax[0]])
                maxy = max([maxy, ylims[1], self.yminmax[1]]) 


        if (miny != float('inf')):
            self.ax.set_ylim(miny*(1.0-fudge), maxy*(1.0+fudge))
            plt.draw()

    # handle plot_button clicks by toggling the visibility of the specific server
    def select_plot(self,label):
        print(label)
        if label in self.servers:
            bVisible = not self.servers[label].plot.get_visible();
            self.servers[label].plot.set_visible(bVisible)
            if self.servers[label].hline != None:
                self.servers[label].hline.set_visible(bVisible)
        
        self.setYLimits()
        self.fig.canvas.draw()


    def Draw(self):
        i = 0
        handles=[]
        labels=[]
        activated=[]
        line_colors=[]
        for s in self.servers:
            print(s, i)
            print(self.servers[s].label)
            handles.append(self.servers[s].plot)
            labels.append(self.servers[s].label)
            activated.append(self.servers[s].bActivated)
            line_colors.append(self.servers[s].color)
            i = i+1

        #ax_check = plt.axes([0.75, 0.40, 0.15, 0.3])
        ax_check = plt.axes([0.2, 0.85, 0.6, 0.15])

        self.plot_button = CheckButtons(
            ax=ax_check,
            labels=labels,
            actives=activated
            ,
            label_props={'color':line_colors},
            frame_props={'edgecolor':line_colors},
            check_props={'facecolor':line_colors}
            )


        # link above fn to "on_clicked" action
        self.plot_button.on_clicked(self.select_plot)
        print("set up on_clicked!")
        
        self.setYLimits()
       #plt.legend(handles, labels)
        plt.show()

# plot the dictionary of servers along with timestamps and measurements
def plotIt(mydata):

    g = Grapher()

    i = 0
    for server in mydata:
        # ttk:  need to add AVE
        g.addData(server, ave=0, times=mydata[server]['timestamps'], pings=mydata[server]['goodness'],color=colors_list[i%len(colors_list)])
        i = i+1

    
    g.Draw()


def testPlotIt():

    mydata = {"server1":{"timestamps":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "goodness":[2.3, 2.4, 2.3, 2.4, 2.5, 2.3, 2.8, 2.0, 2.3, 2.3]},
          "server2":{"timestamps":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "goodness":[2.0, 3.4, 1.3, 5.4, 3.5, 2.3, 4.8, 4.0, 3.3, 2.3]},
          "server3":{"timestamps":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "goodness":[5.3, 5.4, 5.3, 5.4, 5.5, 5.3, 5.8, 5.0, 5.3, 5.3]},
          "server4":{"timestamps":[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], "goodness":[1.3, 1.4, 1.3, 1.4, 1.5, 1.3, 1.8, 1.0, 1.3, 1.3]}}

    plotIt(mydata)
    print("done...")


if __name__ == '__main__':
    testPlotIt()