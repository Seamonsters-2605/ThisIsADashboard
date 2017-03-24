__author__ = "seamonsters"
from tkinter import *
from pywinauto import Application
app = Application()

#app.Connect(path = r"C:\Program Files\Mozilla Firefox\firefox.exe")
app.Start(r"C:\Program Files\Mozilla Firefox\firefox.exe http://10.26.5.2:1187")
#kaz is lame from Jae-chan
win = app.window()

wrap = win.WrapperObject()

wrap.MoveWindow(x = 1265, y = 0, width = 660, height = 630)

master = Tk()
master.title("Overlay")
master.geometry("+1265+0")
w = Canvas(master, width=650, height=580)
w.pack()

master.attributes("-alpha", 0.25)

master.resizable(width=False, height=False)

x=0
y=0
#w.create_line(240+x,150+y,240+x,150+y,width=3,fill="deep pink")
#w.create_line(240+x,105+y,225+x,85+y,width=3,fill="deep pink")
#w.create_line(240+x,142+y,290+x,132+y,width=3,fill="deep pink")
#w.create_line(290+x,132+y,287+x,103+y,width=3,fill="deep pink")
#w.create_line(287+x,103+y,300+x,80+y,width=3,fill="deep pink")
#w.create_line(232+x,360+y,232+x,266+y,width=3,fill="deep pink")
#w.create_line(174+x,313+y,290+x,313+y,width=3,fill="deep pink")
w.create_line(250+x,195+y,400+x,195+y,width=6,fill="deep pink")
w.create_line(250+x,237+y,400+x,237+y,width=6,fill="deep pink")
w.create_line(325+x,195+y,325+x,237+y,width=6,fill="deep pink")
mainloop()
