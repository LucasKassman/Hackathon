# Import Library
import tkinter as tk
from tkinter import ttk
from GraphTest.graphtest3 import *
from GraphTest.evaluator import *

class LB_Items(tk.Frame):
    def __init__(self, root, title, values, bSelectAll, side=tk.LEFT):
            super().__init__(root)
            self.lblabel = tk.Label(self,
			    text = title,
		    #	font = ("Times New Roman", 10),
			    padx = 10, pady = 10)
            self.lblabel.pack(side=tk.TOP)
        
            # for scrolling vertically
            self.yscrollbar = tk.Scrollbar(self)
            self.yscrollbar.pack(side = tk.RIGHT, fill = tk.Y)
            activeStyle = "dotbox" # dotbox, non, underline...
            sm = "extended" # single, browse, multiple, or extended
            self.list = tk.Listbox(self, selectmode = sm, activestyle=activeStyle,
			    yscrollcommand = self.yscrollbar.set)
            # Widget expands horizontally and
            # vertically by assigning both to
            # fill option
            self.list.pack(padx = 10, pady = 10,
	             expand = tk.YES, fill = "both", side=tk.LEFT)


                
            # Attach listbox to vertical scrollbar
            self.yscrollbar.config(command = self.list.yview)

            self.set(values, bSelectAll)
            #if bSelectAll:
            if False:
                for item in values:
	       	        self.list.insert(tk.END, item)
             #start with everthing selected
                self.list.select_set(0, tk.END)
            
            self.pack(fill="both", expand=True, side=side)
    
    def set(self, servers, bSelectAll):
        self.list.delete(0, tk.END)
        for s in servers:
            self.list.insert(tk.END, s)
        if bSelectAll:
            #start with everthing selected
            self.list.select_set(0, tk.END)

    #helper menthod
    def get(self,i):
        return self.list.get(i)
    #helper menthod
    def getAll(self):
        return self.list.get(0,tk.END)
 
#
# main window that is the launch point for options and creating graph sub-windows.
#  This is a sub-class of tk.Tk, which is often refered to as 'root' in various examples.
class MainWindow(tk.Tk):

    # constructor
    def __init__(self, title="MainWindow()"):
        super().__init__()
        print("in MainWindow  __init__")
        self.title(title)
        self.geometry("600x400")
        self.subWindows=[] # a list of all the child windows we have

 
    def selectedServers(self):
        return self.selected_display.getAll()
            
    # Add the option buttons to this window.  Could be modified to add more complex widgets
    def AddButtons(self):
        f1 = tk.Frame(self, height=60) # frame for the two top buttons
        f2 = tk.Frame(self, height=60) # frame for the three bottom buttons.
        
        tk.Button(f1, text="Measure ALL Servers", command=self.measure_all_servers).place(relx=0.25, rely=0.5, anchor=tk.CENTER)
        tk.Button(f1, text="Measure SELECTED Servers", command=self.measure_selected_servers).place(relx=0.75, rely=0.5, anchor=tk.CENTER)
        tk.Button(f2, text="Refresh Server List", command=self.refresh_server_list).place(relx=0.2, rely=0.5, anchor=tk.CENTER)
        tk.Button(f2, text="Show", command=self.show).place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        tk.Button(f2, text="Hide", command=self.hide).place(relx=0.8, rely=0.5, anchor=tk.CENTER)

        f1.pack(expand=False, fill=tk.BOTH)
        f2.pack(expand=False, fill=tk.BOTH, side=tk.BOTTOM)

        fullServerList = getServers()
        self.server_selector   = LB_Items(self,"Select from these Servers", fullServerList, True)
        self.selected_display  = LB_Items(self, "Selected Servers", fullServerList, False, tk.RIGHT)

        def on_select(evt):
            if (evt.widget.curselection()):
                self.selected_display.list.delete(0, tk.END)
                for i in self.server_selector.list.curselection():
                    self.selected_display.list.insert(tk.END, self.server_selector.list.get(i))

        self.server_selector.list.bind('<<ListboxSelect>>', on_select)

    def refresh_server_list(self):
        fullServerList = getServers()
        self.server_selector.set(servers=fullServerList,bSelectAll=True)
        self.selected_display.set(servers=fullServerList,bSelectAll=False)

    
    def measure_selected_servers(self):
        self.measure_servers(self.selectedServers())
        
    def measure_all_servers(self):
        self.measure_servers(self.server_selector.list.get(0,tk.END))
        
    def measure_servers(self,sl):
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
class ChildWindow(tk.Toplevel):
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
