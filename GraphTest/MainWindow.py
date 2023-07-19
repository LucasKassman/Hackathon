# Import Library
import tkinter
from tkinter import ttk
from graphtest3 import *
from evaluator import *

#import tkinter as tk
#from tkinter import *

#
# main window that is the launch point for options and creating graph sub-windows.
#  This is a sub-class of tk.Tk, which is often refered to as 'root' in various examples.
class MainWindow(tk.Tk):
    
    # constructor
    def __init__(self, title="MainWindow()"):
        super().__init__()
        print("in MainWindow  __init__")
        self.title(title)
        self.geometry("400x400")
        self.subWindows=[] # a list of all the child windows we have
    
    # Add the option buttons to this window.  Could be modified to add more complex widgets
    def AddButtons(self):
        tk.Button(mw, text="Measure Servers", command=self.launch).pack(pady=10)
        tk.Button(mw, text="Show", command=self.show).pack(pady=10) # just a test case for now
        tk.Button(mw, text="Hide", command=self.hide).pack(pady=10) # just a test case for now

    # launch the child window (i.e. graph)
    def launch(self):
        w = ChildWindow()
        w.title("Server Evaluation")
        w.geometry("1100x1000")
        self.subWindows.append(w)

    # show all child windows
    def show(self):
        # Because items can be removed from the list, go in reverse order,
        # that way we won't corrupt the list we're walking through
        for w in reversed(self.subWindows):
            # If the child window is closed using the 'x' in the upper right corner, it will become invalid
            # It will through an exception because w no longer contains a valid window.
            # If that happens remove it.
            try:
                w.deiconify()
            except:
                self.subWindows.remove(w)

        # If someone presses "show" and there's nothing to show, then launch a window for them!
        if len(self.subWindows) == 0:
            self.launch()                 
    
    # hide all child windows
    def hide(self):
        # see comments in 'show()'
        for w in reversed(self.subWindows):
            try:
                w.withdraw()
            except:
                self.subWindows.remove(w)
        
#
# Window containing the plot data
# This is a subclass of Toplevel which allows us to create indepent windows.
class ChildWindow(tkinter.Toplevel):
    def __init__(self):
        super().__init__()
        print("in ChildWindow __init__")
        self.g = Grapher(self)  # create a Grapher object with this Toplevel as the base
        sl = getServers() # get the list of servers
        plot_data = evaluate(sl) # evaluate them
        for server in plot_data: # add the data to the graph
            self.g.addData(server, plot_data[server]['average'], plot_data[server]['timestamps'],plot_data[server]['goodness'])



mw = MainWindow("Runescape Server Evaluation")
mw.AddButtons()

# method to clean up.
# Code appears to exit properly without this when run from the command line, but not when debugging in VS Code...
def on_closing():
    print("in on_closing")
    #if messagebox.askokcancel("Quit", "Do you want to quit?"):
    if True:
        print("bye...")
        mw.destroy()
        mw.quit()

mw.protocol("WM_DELETE_WINDOW", on_closing)

# Execute Tkinter
mw.mainloop()
