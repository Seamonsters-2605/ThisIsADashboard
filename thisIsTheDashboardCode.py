__author__ = "jacobvanthoog"

from tkinter import *
import hashlib
import colorsys
from networktables import NetworkTables

class RobotConnection:

    def __init__(self):
        NetworkTables.initialize(server="roborio-2605-frc.local")
        self.table = NetworkTables.getTable('dashboard')

    def isConnected(self):
        # TODO
        return True

    def disconnect(self):
        NetworkTables.shutdown()

    def getLogStates(self):
        try:
            logStateNames = self.table.getStringArray('logstatenames')
            logStateValues = self.table.getStringArray('logstatevalues')
            logStates = { }
            for i in range(0, len(logStateNames)):
                logStates[logStateNames[i]] = logStateValues[i]
            return logStates
        except BaseException:
            return { }

    def sendSwitchData(self, switches):
        print(switches)
        switchNames = [name for name, value in switches.items()]
        switchValues = [value for name, value in switches.items()]
        self.table.putStringArray('switchnames', switchNames)
        self.table.putBooleanArray('switchvalues', switchValues)

class ThisIsTheDashboardApp:

    DISCONNECTED_COLOR = "#AAAAAA"
    CONNECTED_COLOR = "#55FF55"
    ERROR_COLOR = "#FF0000"

    def __init__(self, root, switches):
        self.robotConnection = None
        self._buildUI(root, switches)

    def _buildUI(self, root, switches):
        self.root = root
        root.title("Seamonsters Dashboard!")
        
        frame = Frame(root)
        frame.pack(fill=BOTH, expand=True)

        leftFrame = Frame(frame)
        leftFrame.pack(side=LEFT)

        switchFrame = Frame(leftFrame, borderwidth=3, relief=SUNKEN,
                            padx=5, pady=5)
        switchFrame.pack(side=TOP, fill=X)

        self.switchVars = { }

        for switch in switches:
            var = IntVar()
            self.switchVars[switch] = var

            checkbuttonFrame = Frame(switchFrame)
            checkbuttonFrame.pack(side=TOP, fill=X)
            
            checkbutton = Checkbutton(checkbuttonFrame, text=switch,
                                      font=("Helvetica", 16),
                                      variable=var)
            checkbutton.pack(side=LEFT)

        self.connectButton = Button(leftFrame, height=2, text="Connect",
                               font=("Helvetica", 16),
                               command = self._connectButtonPressed,
                               bg=ThisIsTheDashboardApp.DISCONNECTED_COLOR)
        self.connectButton.pack(side=TOP, fill=X)
        self.disconnectButton = Button(leftFrame, height=2, text="Disconnect",
                                    font=("Helvetica", 16), state=DISABLED,
                                    command = self._disconnectButtonPressed)
        self.disconnectButton.pack(side=TOP, fill=X)

        separator = Frame(frame, width=12)
        separator.pack(side=LEFT)

        self.logFrame = Frame(frame, borderwidth=3, relief=SUNKEN)
        self.logFrame.pack(side=LEFT, fill=X, expand=True)
        
        self.logStateLabels = { }

    def _connectButtonPressed(self):
        try:
            self.robotConnection = RobotConnection()
            if self.robotConnection.isConnected():
                switches = { }
                for name, var in self.switchVars.items():
                    switches[name] = var.get() == 1
                self.robotConnection.sendSwitchData(switches)
                self._connected()
                self._updateLogStates()
            else:
                self._disconnectedError()
        except BaseException as e:
            print(e)
            self._disconnectedError()

    def _disconnectButtonPressed(self):
        if self.robotConnection is None:
            return
        if not self.robotConnection.isConnected():
            self._disconnectedError()
            return
        self.robotConnection.disconnect()
        self._disconnectedSuccess()

    def _connected(self):
        self.connectButton.config(bg=ThisIsTheDashboardApp.CONNECTED_COLOR)
        self.connectButton.config(state=DISABLED)
        self.disconnectButton.config(state=NORMAL)

    def _disconnectedSuccess(self):
        self.connectButton.config(bg=ThisIsTheDashboardApp.DISCONNECTED_COLOR)
        self.robotConnection = None
        self.connectButton.config(state=NORMAL)
        self.disconnectButton.config(state=DISABLED)

    def _disconnectedError(self):
        self.connectButton.config(bg=ThisIsTheDashboardApp.ERROR_COLOR)
        self.robotConnection = None
        self.connectButton.config(state=NORMAL)
        self.disconnectButton.config(state=DISABLED)
        for i in range(0, 3):
            self.connectButton.flash()

    def _updateLogStates(self):
        if self.robotConnection is None:
            return
        if not self.robotConnection.isConnected():
            self._disconnectedError()
            return
        logStates = self.robotConnection.getLogStates()
        for name, value in logStates.items():
            if name not in self.logStateLabels:
                self._addLogStateLabel(name)
            self.logStateLabels[name].config(text=value)
        self.root.after(100, self._updateLogStates)

    def _addLogStateLabel(self, name):
        color = self._getLogStateColor(name)
        
        stateFrame = Frame(self.logFrame, bg=color,
                           borderwidth=3, relief=GROOVE)
        stateFrame.pack(side=TOP, fill=X)
        
        titleLabel = Label(stateFrame, text=name + ":",
                           font=("Helvetica", 24), bg=color)
        titleLabel.pack(side=LEFT)
        valueLabel = Label(stateFrame, text="None",
                           font=("Helvetica", 24), bg=color)
        valueLabel.pack(side=LEFT)

        self.logStateLabels[name] = valueLabel

    def _getLogStateColor(self, title):
        titleHash = hashlib.sha256()
        titleHash.update(title.encode('utf-8'))
        hashValue = titleHash.digest()
        hue = hashValue[0]
        r,g,b = colorsys.hsv_to_rgb(float(hue)/256.0, 0.7, 1.0)
        colorHex = '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
        return colorHex

root = Tk()
app = ThisIsTheDashboardApp(root, switches=['Start in Voltage',
                                            'Auto shoot enabled',
                                            'Do something',
                                            'This is a switch'])
root.mainloop()
