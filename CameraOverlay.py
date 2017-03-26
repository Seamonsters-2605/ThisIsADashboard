__author__ = "seamonsters"
from tkinter import *
from pywinauto import Application
app = Application()

#app.Connect(path = r"C:\Program Files\Mozilla Firefox\firefox.exe")
app.Start(r"C:\Program Files\Mozilla Firefox\firefox.exe file:///C:/Users/seamonsters/Documents/CompetitionBot2017/camerapage.html")
win = app.window()

wrap = win.WrapperObject()

wrap.MoveWindow(x = 1265, y = 0, width = 660, height = 630)

master = Tk()
master.title("Overlay")
master.geometry("+1265+0")
w = Canvas(master, width=650, height=580)
w.pack()

master.attributes("-alpha", 0.35)

master.resizable(width=False, height=False)

x=0
y=1
Color = "green"
Width = 3

w.create_line(224+x,190+y,424+x,190+y,width=Width,fill=Color)
w.create_line(224+x,250+y,424+x,250+y,width=Width,fill=Color)
w.create_line(324+x,150+y,324+x,290+y,width=Width,fill=Color)
#w.create_line(265+x,200+y,330+x,340+y,width=Width,fill=Color)
mainloop()
