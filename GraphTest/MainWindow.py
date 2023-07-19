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
        self.geometry("400x800")
        self.subWindows=[] # a list of all the child windows we have
        self.fullServerList = getServers()
 
    # create a listbox
    def CreateListbox(self,title, values, bSelectAll):
        label = tk.Label(self,
			text = title,
		#	font = ("Times New Roman", 10),
			padx = 10, pady = 10)
        label.pack()
        
        # for scrolling vertically
        yscrollbar = tk.Scrollbar(self)
        yscrollbar.pack(side = tk.RIGHT, fill = tk.Y)
        activeStyle = "dotbox" # dotbox, non, underline...
        sm = "extended" # single, browse, multiple, or extended
        list = tk.Listbox(self, selectmode = sm, activestyle=activeStyle,
			yscrollcommand = yscrollbar.set)
        # Widget expands horizontally and
        # vertically by assigning both to
        # fill option
        list.pack(padx = 10, pady = 10,
	        expand = tk.YES, fill = "both")

        for item in values:
	       	list.insert(tk.END, item)
                
        # Attach listbox to vertical scrollbar
        yscrollbar.config(command = list.yview)

        if bSelectAll:
            #start with everthing selected
            list.select_set(0, tk.END)
        
        return list

    def selectedServers(self):
        return self.selected_display.get(0,tk.END)
            
    # Add the option buttons to this window.  Could be modified to add more complex widgets
    def AddButtons(self):
        tk.Button(self, text="Measure Servers", command=self.launch).pack(pady=10)
        tk.Button(self, text="Show", command=self.show).pack(pady=10) # just a test case for now
        tk.Button(self, text="Hide", command=self.hide).pack(pady=10) # just a test case for now

        self.server_selector   = self.CreateListbox("Select from these Servers", self.fullServerList, True)
        self.selected_display  = self.CreateListbox("Selected Servers", self.fullServerList, False)
        
        def on_select(evt):
            if (evt.widget.curselection()):
                self.selected_display.delete(0, tk.END)
                for i in self.server_selector.curselection():
                    self.selected_display.insert(tk.END, self.server_selector.get(i))

        self.server_selector.bind('<<ListboxSelect>>', on_select)


    # launch the child window (i.e. graph)
    def launch(self):
        sl = self.selectedServers()
        if len(sl) > 0:
            w = ChildWindow(sl)
            w.title("Server Evaluation")
            w.geometry("1100x1000")
            self.subWindows.append(w)
        else:
            print("no servers selected!!!")

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
    def __init__(self, sl):
        super().__init__()
        print("in ChildWindow __init__")
        self.g = Grapher(self)  # create a Grapher object with this Toplevel as the base
        #sl = getServers() # get the list of servers
        plot_data = evaluate(sl) # evaluate them
        for server in plot_data: # add the data to the graph
            self.g.addData(server, plot_data[server]['average'], plot_data[server]['timestamps'],plot_data[server]['goodness'])


if __name__ == '__main__':
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
