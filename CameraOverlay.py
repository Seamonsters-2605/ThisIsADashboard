__author__ = "seamonsters"
from tkinter import *
from pywinauto import Application
app = Application()

#app.Connect(path = r"C:\Program Files\Mozilla Firefox\firefox.exe")
app.Start(r"C:\Program Files\Mozilla Firefox\firefox.exe http://10.26.5.2:1187")

win = app.window()

wrap = win.WrapperObject()

wrap.MoveWindow(x = 0, y = 0, width = 532, height = 500)

master = Tk()
master.geometry("+0+0")
w = Canvas(master, width=510, height=500)
w.pack()

master.attributes("-alpha", 0.25)

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
