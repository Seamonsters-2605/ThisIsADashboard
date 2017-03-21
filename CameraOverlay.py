__author__ = "seamonsters"
from tkinter import *
import tkinter as tk
master = Tk()
w = Canvas(master, width=510, height=500)
w.pack()


master.resizable(width=False, height=False)

x=0
y=0
w.create_line(240+x,142+y,240+x,105+y,width=3,fill="deep pink")
w.create_line(240+x,105+y,225+x,85+y,width=3,fill="deep pink")
w.create_line(240+x,142+y,290+x,132+y,width=3,fill="deep pink")
w.create_line(290+x,132+y,287+x,103+y,width=3,fill="deep pink")
w.create_line(287+x,103+y,300+x,80+y,width=3,fill="deep pink")
w.create_line(232+x,360+y,232+x,266+y,width=3,fill="deep pink")
w.create_line(174+x,313+y,290+x,313+y,width=3,fill="deep pink")
w.create_rectangle(192+x,298+y,272+x,328+y,width=3,outline="deep pink")
mainloop()
