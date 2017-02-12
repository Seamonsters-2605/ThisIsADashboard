__author__ = "jacobvanthoog"

from tkinter import *
import hashlib
from tkinter import filedialog
import colorsys
from networktables import NetworkTables

TEST_MODE = False

class RobotConnection:

    def __init__(self):
        NetworkTables.initialize(server="roborio-2605-frc.local")
        self.table = NetworkTables.getTable('dashboard')

    def isConnected(self):
        # TODO: test this!
        return NetworkTables.isConnected()

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


class TestRobotConnection:

    def __init__(self):
        print("Initialized test connection")
        print("You're not actually connected to the robot!")
        self.testNumber = 0

    def isConnected(self):
        return True

    def disconnect(self):
        print("Test connection: Disconnect")

    def getLogStates(self):
        self.testNumber += 1
        return {'Test number': str(self.testNumber),
                'abc': "123",
                'This is a long key name': "This is a long value",
                'Key': "This value is important!"}

    def sendSwitchData(self, switches):
        print(switches)


class ThisIsTheDashboardApp:

    DISCONNECTED_COLOR = "#AAAAAA"
    CONNECTED_COLOR = "#55FF55"
    ERROR_COLOR = "#FF0000"

    LOG_STATE_FONT = ("Helvetica", 24)
    IMPORTANT_LOG_STATE_FONT = ("Helvetica", 24, "bold underline")

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

        for switch, enabled in switches.items():
            var = IntVar()
            self.switchVars[switch] = var

            checkbuttonFrame = Frame(switchFrame)
            checkbuttonFrame.pack(side=TOP, fill=X)
            
            checkbutton = Checkbutton(checkbuttonFrame, text=switch,
                                      font=("Helvetica", 16),
                                      variable=var,
                                      command=self._sendSwitchData)
            if enabled:
                checkbutton.select()
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
        global TEST_MODE
        try:
            if TEST_MODE:
                self.robotConnection = TestRobotConnection()
            else:
                self.robotConnection = RobotConnection()
            if self.robotConnection.isConnected():
                self._sendSwitchData()
                self._connected()
                self._updateLogStates()
            else:
                self.robotConnection.disconnect()
                self._disconnectedError()
        except BaseException as e:
            print(e)
            self.robotConnection.disconnect()
            self._disconnectedError()

    def _disconnectButtonPressed(self):
        if self.robotConnection is None:
            return
        if not self.robotConnection.isConnected():
            self.robotConnection.disconnect()
            self._disconnectedError()
            return
        self.robotConnection.disconnect()
        self._disconnectedSuccess()

    def _connected(self):
        self.connectButton.config(bg=ThisIsTheDashboardApp.CONNECTED_COLOR,
                                  state=DISABLED)
        self.disconnectButton.config(state=NORMAL)

    def _disconnectedSuccess(self):
        self.robotConnection = None
        self.connectButton.config(bg=ThisIsTheDashboardApp.DISCONNECTED_COLOR,
                                  state=NORMAL)
        self.disconnectButton.config(state=DISABLED)

    def _disconnectedError(self):
        self.robotConnection = None
        self.connectButton.config(bg=ThisIsTheDashboardApp.ERROR_COLOR,
                                  state=NORMAL)
        self.disconnectButton.config(state=DISABLED)
        for i in range(0, 3):
            self.connectButton.flash()

    def _sendSwitchData(self):
        switches = { }
        for name, var in self.switchVars.items():
            switches[name] = var.get() == 1
        self.robotConnection.sendSwitchData(switches)

    def _updateLogStates(self):
        if self.robotConnection is None:
            return
        if not self.robotConnection.isConnected():
            self.robotConnection.disconnect()
            self._disconnectedError()
            return
        logStates = self.robotConnection.getLogStates()
        for name, value in logStates.items():
            if name not in self.logStateLabels:
                self._addLogStateLabel(name)
            label = self.logStateLabels[name]
            label.config(text=value)
            if value.endswith('!'):
                label.config(
                    font=ThisIsTheDashboardApp.IMPORTANT_LOG_STATE_FONT)
            else:
                label.config(font=ThisIsTheDashboardApp.LOG_STATE_FONT)
        self.root.after(100, self._updateLogStates)

    def _addLogStateLabel(self, name):
        color = self._getLogStateColor(name)
        
        stateFrame = Frame(self.logFrame, bg=color,
                           borderwidth=3, relief=GROOVE)
        stateFrame.pack(side=TOP, fill=X)
        
        titleLabel = Label(stateFrame, text=name + ":",
                           font=ThisIsTheDashboardApp.LOG_STATE_FONT, bg=color)
        titleLabel.pack(side=LEFT)
        valueLabel = Label(stateFrame, text="None",
                           font=ThisIsTheDashboardApp.LOG_STATE_FONT, bg=color)
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

def readSwitchConfig(file):
    content = file.readlines()
    switchNames = {}
    for line in content:
        line = line.strip()
        if len(line) == 0:
            continue
        switchName = line[1:]
        firstCharacter = line[0]

        if firstCharacter == "+":
            switchEnabled = True
        elif firstCharacter == "-":
            switchEnabled = False
        else:
            switchName = line
            print("Switch", switchName, "doesn't have enabled state!")
            switchEnabled = False

        switchNames[switchName] = switchEnabled
    return switchNames

if __name__ == "__main__":
    root = Tk()
    file = filedialog.askopenfile()
    if file == None:
        exit()
    switches = readSwitchConfig(file)
    app = ThisIsTheDashboardApp(root, switches = switches)
    root.mainloop()
