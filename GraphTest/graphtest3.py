import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class Grapher(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.parent = parent
        self.btn = tk.Label(parent, text='Best Servers')
        self.btn.grid(row=0, column=0, padx=20, pady=10)

        self.lfr = tk.LabelFrame(parent)
        self.lfr.grid(row=1, column=0)
        self.fig = plt.figure(figsize=(8, 5))
        self.ax = self.fig.add_subplot(111)
        self.server_checks = {}
        self.var = {}
        self.plot = {}


    def addData(self, server, times, pings):
        if not server in self.server_checks:
            self.var[server] = tk.IntVar()
            self.server_checks[server] = tk.Checkbutton(self.lfr, text=server, variable=self.var[server], command=self.checkbutton_changed)
            self.server_checks[server].grid(column=0, row=len(self.server_checks))
            self.server_checks[server].select()

        
        self.plot[server] = self.ax.plot(times, pings, label=server)[0]
        self.plot[server].set_visible(self.var[server].get())
        
        plt.legend()
        #plt.gca().invert_yaxis()

        #plt.xticks(times, rotation=60)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=2, column=0, ipadx=40, ipady=20)

    def checkbutton_changed2(self):
        self.plot_y.set_visible(self.var_y.get())
        self.plot_z.set_visible(self.var_z.get())

        self.ax.figure.canvas.draw()

    def checkbutton_changed(self):
        print('---')
        handles = []
        labels = []

        for s in self.var:
            self.plot[s].set_visible(self.var[s].get())
            if self.var[s].get():
                handles.append(self.plot[s])
                labels.append(s)
        
        plt.legend(handles, labels)

        self.ax.figure.canvas.draw()


def plotIt(mydata):
    root = tk.Tk()
    g = Grapher(root)

    
    for server in mydata:
        g.addData(server, mydata[server]['timestamps'],mydata[server]['goodness'])

    def on_closing():
        print("in on_closing")
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            print("bye...")
            root.destroy()
            root.quit()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
    

            
if __name__ == '__main__':
    root = tk.Tk()
    def on_closing():
        print("in on_closing")
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            print("bye...")
            root.destroy()
            root.quit()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    g = Grapher(root)
    g.addData("server_name", [1, 2, 3, 4, 5], [10, 20, 13, 25, 20])
    g.addData("server_name2", [1, 2, 3, 3.5,4.5,5], [20, 30, 33, 25, 30, 17])
    root.mainloop()
