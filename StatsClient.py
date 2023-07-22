from GraphDisplay.MainWindow import *

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