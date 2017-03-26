__author__ = "seamonsters"
from tkinter import *
from pywinauto import Application

def moveWindows():
    global wrap, master
    wrap.MoveWindow(x=1265, y=0, width=660, height=630)
    master.geometry("+1265+0")

def lowerWindow():
    global master
    master.lower()

def raiseWindow():
    global master
    master.lift()

app = Application()

#app.Connect(path = r"C:\Program Files\Mozilla Firefox\firefox.exe")
app.Start(r"C:\Program Files\Mozilla Firefox\firefox.exe file:///C:/Users/seamonsters/Documents/CompetitionBot2017/camerapage.html")
win = app.window()

wrap = win.WrapperObject()


master = Tk()
master.title("Overlay")

moveWindows()

w = Canvas(master, width=650, height=580)
w.pack(side=TOP)

buttonFrame = Frame(master)
buttonFrame.pack(side=TOP, fill=X, expand=True)

expandFrame = Frame(buttonFrame)
expandFrame.pack(side=LEFT, fill=X, expand=True)

resetButton = Button(buttonFrame, text="RESET WINDOWS", command=moveWindows, height=2)
resetButton.pack(side=LEFT)

lowerButton = Button(buttonFrame, text="v v  LOWER OVERLAY  v v", command=lowerWindow, height=2)
lowerButton.pack(side=LEFT)

raiseButton = Button(buttonFrame, text="^^ RAISE OVERLAY ^^", command=raiseWindow, height=2)
raiseButton.pack(side=LEFT)

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
