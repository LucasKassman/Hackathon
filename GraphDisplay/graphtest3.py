import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Grapher(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        titleFont = tk.font.Font(family='Helvetica', size=12, weight='bold')
        self.parent = parent
        #self.btn = tk.Label(parent, text='Best Servers', font=titleFont)
        #self.btn = tk.Label(parent)
        #self.btn.grid(row=0, column=0, padx=20, pady=10)
        self.lfr = tk.LabelFrame(parent, text="Best Servers", padx=20, pady=20, font=titleFont)
        self.lfr.pack(pady=20, padx=10)
      
        #self.lfr.grid(row=1, column=0)
        self.fig = plt.figure(figsize=(10, 8))

        self.ax = self.fig.add_subplot(111)
        self.server_checks = {}
        self.servers = {}
        self.bFirstItem = True
        #self.lfr.pack_forget()
        #self.lfr.grid_forget()
    #
    # internal class to hold data for and perform functions for individual servers
    class server_data():
        def __init__(self, parent):
            self.parent = parent # cheat way to access all the Grapher class' data
   
        #
        # Plot the data and the horizontal line
        #   o  Creates a checkbox selector
        #   o  Creates a plot of the pings vs time
        #   o  Optionally creates a horizontal line representing the input average
        def makePlot(self, server, ave, times, pings, bVisible, bPlotHLine=True):
            
            #
            # Create a checkbutton

            stext = server+(" (%.2f)"%ave) # append the average to the displayed name
            buttonFont = tk.font.Font(family='Helvetica', size=12, weight='bold')  # make the font larger and bold instead of default
            self.var = tk.IntVar() # variable to track the selected state
            self.check= tk.Checkbutton(self.parent.lfr, text=stext, variable=self.var, command=self.parent.checkbutton_changed, font=buttonFont, width=50, anchor="w")
            self.check.pack()
            # set the initial selection mode
            if bVisible:
                self.check.select()
            else:
                self.check.deselect()
       
            #
            # Create a plot of the data      
            self.plot=self.parent.ax.plot(times, pings, label=server)[0]
        
            #
            # Optionally create the horizontal line
            if bPlotHLine:
                self.hline = self.parent.ax.hlines(ave, xmin=min(times), xmax=max(times),colors=[self.plot.get_color()])
            else:
                self.hline = None
            
            # update based on the visibility
            self.setVisibility()

        #
        # update the visibility base on the current 'var'
        def setVisibility(self):
            self.plot.set_visible(self.var.get())
            if self.hline != None:
                self.hline.set_visible(self.var.get())

    def addData(self, server, ave, times, pings):
        
        if not server in self.servers:
            self.servers[server] = Grapher.server_data(self)
            self.servers[server].makePlot(server, ave, times, pings, self.bFirstItem)
        
        if self.bFirstItem:
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)

        self.bFirstItem = False

        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.checkbutton_changed() # update the legend

    def checkbutton_changed(self):
        print('---')
        handles = []
        labels = []

        for s in self.servers:
            self.servers[s].setVisibility()
            if self.servers[s].var.get():
                handles.append(self.servers[s].plot)
                labels.append(s)
        
        plt.legend(handles, labels)

        self.ax.figure.canvas.draw()

# for test purposes, get stand-alone Grapher object
#  -- i.e. clients don't need to know about tk...
def getGrapher():
    return Grapher(tk.Tk())

# for test purpose, call root's main event loop to process events while window is presented
def waitGrapher(g):
    def on_closing():
        print("bye...")
        g.parent.destroy()
        g.parent.quit()
    g.parent.protocol("WM_DELETE_WINDOW", on_closing)
    g.parent.mainloop()


if __name__ == '__main__':
    g = getGrapher()
    # just some test data
    g.addData("server_name", 21, [1, 2, 3, 4, 5], [10, 20, 13, 25, 20])
    g.addData("server_name2", 22, [1, 2, 3, 3.5,4.5,5], [20, 30, 33, 25, 30, 17])
    waitGrapher(g)
