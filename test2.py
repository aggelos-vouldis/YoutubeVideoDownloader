# Import the Tkinter library
from tkinter import *
# Create an instance of Tkinter frame
win = Tk()
# Define the geometry
win.geometry("750x250")


def callback(var):
    content = var.get()
    Label(win, text=content).pack()


# Create an variable to store the user-input
var = StringVar()
var.trace("w", lambda name, index, mode, var=var: callback(var))
# Create an Entry widget
e = Entry(win, textvariable=var)
e.pack()
win.mainloop()
