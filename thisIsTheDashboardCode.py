__author__ = "seamonsters"

from tkinter import *
from tkinter import ttk
import hashlib
from tkinter import filedialog
from tkinter import messagebox
import colorsys
from networktables import NetworkTables
import random


TEST_MODE = False

class RobotConnection:

    def __init__(self):
        NetworkTables.initialize(server="10.26.5.2")
        self.table = NetworkTables.getTable('dashboard')
        self.commandTable = NetworkTables.getTable('commands')

    def isConnected(self):
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

    def sendCommand(self, command):
        lastId = self.commandTable.getNumber('id')
        newId = lastId
        while newId == lastId:
            newId = random.randrange(1, 65536)
        print(lastId, newId)
        self.commandTable.putString('command', command)
        self.commandTable.putNumber('id', newId)
        print(self.commandTable.getString('command'))


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
        return {'': "Dashboard in Demo Mode!",
                'Drive mode': "Position",
                'Field oriented': "Disabled",
                'Drive current': "0.625",
                'Gear': "No gear",
                'Climber lock mode': "On!",
                'Climber status': "Locked!",
                'Flywheel speed': "0",
                'Flywheel mode': "Speed",
                'Rotation offset': "-0.02304",
                'Strafe alignment': "0.08555"
                #,'Test number': str(self.testNumber),
                }

    def sendSwitchData(self, switches):
        print(switches)

    def sendCommand(self, command):
        print("Command:", command)


class ThisIsTheDashboardApp:

    LOG_STATE_TITLE_FONT = ("Segoe UI", 24)
    LOG_STATE_FONT = ("Segoe UI Light", 24)
    IMPORTANT_LOG_STATE_FONT = ("Segoe UI", 24, "bold underline")
    PROGRESS_MAX = 110

    def __init__(self, root, switchFileName):
        self.robotConnection = None
        self.switchFileName = switchFileName

        style = ttk.Style()
        style.configure('logo.TLabel', font=('System', 60),
                        foreground="#00BB00")
        style.configure('switch.TCheckbutton', font=('Segoe UI', 12))
        style.configure('dashboard.TButton', font=('Segoe UI', 12))

        self._buildUI(root)
        self._updateSwitches()

    def _buildUI(self, root):
        self.root = root
        root.title("Seamonsters Dashboard! (1187/1188)")
        
        frame = ttk.Frame(root)
        frame.pack(fill=BOTH, expand=True)

        leftFrame = ttk.Frame(frame)
        leftFrame.pack(side=LEFT, fill=Y)

        ttk.Label(leftFrame, text="2605", style='logo.TLabel').pack(side=TOP)

        self.switchFrame = ttk.Frame(leftFrame, borderwidth=3, relief=GROOVE,
                                     padding=8)
        self.switchFrame.pack(side=TOP, fill=X)

        self.switchVars = { }

        self.progressVar = IntVar()
        self.progress = ttk.Progressbar(leftFrame, mode='determinate',
            var=self.progressVar, maximum=ThisIsTheDashboardApp.PROGRESS_MAX)
        self.progress.pack(side=TOP, fill=X)

        connectFrame = ttk.Frame(leftFrame)
        connectFrame.pack(side=TOP, fill=X)

        self.connectButton = ttk.Button(connectFrame, text="Connect",
            style='dashboard.TButton', command=self._connectButtonPressed,
            padding=5)
        self.connectButton.pack(side=LEFT, fill=X, expand=True)
        self.disconnectButton = ttk.Button(connectFrame, text="Disconnect",
            style='dashboard.TButton', state=DISABLED, padding=5,
            command=self._disconnectButtonPressed)
        self.disconnectButton.pack(side=LEFT, fill=X, expand=True)

        self.commandEntry = ttk.Entry(leftFrame)
        self.commandEntry.pack(side=TOP, fill=X)
        self.commandEntry.focus()

        self.commandButton = ttk.Button(leftFrame, text="Run command",
            style='dashboard.TButton', command=self._commandButtonPressed,
            padding=5, state=DISABLED)
        self.commandButton.pack(side=TOP, fill=X)

        resetButton = ttk.Button(leftFrame, text="Reset", padding=5,
            style='dashboard.TButton', command=self._resetButtonPressed)
        resetButton.pack(side=TOP, fill=X)

        self.logFrame = ttk.Frame(frame, padding=(50, 0, 0, 0))
        self.logFrame.pack(side=TOP, fill=X, expand=True, anchor=N)
        
        self.logStateLabels = { }


    def _connectButtonPressed(self):
        global TEST_MODE

        messagebox.showerror("Warning!!", "Make sure battery is strapped in!")

        try:
            if TEST_MODE:
                self.robotConnection = TestRobotConnection()
            else:
                self.robotConnection = RobotConnection()
            self._waiting()
            self.waitCount = 0
            self._waitForConnection()
        except BaseException as e:
            print("Exception:", e)
            self.robotConnection.disconnect()
            self._disconnectedError()

    def _waitForConnection(self):
        if self.waitCount > 10:
            self.robotConnection.disconnect()
            self._disconnectedError()
            return
        self.waitCount += 1
        try:
            if self.robotConnection.isConnected():
                self._sendSwitchData()
                self._connected()
                self._updateLogStates()
            else:
                self.root.after(500, self._waitForConnection)
        except BaseException as e:
            print("Exception:", e)
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
        self._disconnected()
        self._resetButtonPressed()

    def _resetButtonPressed(self):
        self.logStateLabels = { }
        for child in self.logFrame.winfo_children():
            child.destroy()
        self._updateSwitches()

    def _connected(self):
        self.connectButton.config(state=DISABLED)
        self.disconnectButton.config(state=NORMAL)
        self.commandButton.config(state=NORMAL)
        self.progress.stop()
        self.progressVar.set(maximum=ThisIsTheDashboardApp.PROGRESS_MAX)

    def _waiting(self):
        self.connectButton.config(state=DISABLED)
        self.disconnectButton.config(state=DISABLED)
        self.commandButton.config(state=DISABLED)
        self.progressVar.set(0)
        self.progress.start()

    def _disconnected(self):
        self.robotConnection = None
        self.connectButton.config(state=NORMAL)
        self.disconnectButton.config(state=DISABLED)
        self.commandButton.config(state=DISABLED)
        self.progress.stop()
        self.progressVar.set(0)

    def _disconnectedError(self):
        self._disconnected()
        messagebox.showerror("Dashboard Error", "Connection Failed!")


    def _updateSwitches(self):
        with open(self.switchFileName) as f:
            switches = readSwitchConfig(f)

        for child in self.switchFrame.winfo_children():
            child.destroy()
        self.switchVars = { }
        for switch, enabled in switches.items():
            var = IntVar()
            self.switchVars[switch] = var

            checkbuttonFrame = ttk.Frame(self.switchFrame)
            checkbuttonFrame.pack(side=TOP, fill=X)

            checkbutton = ttk.Checkbutton(checkbuttonFrame, text=switch,
                variable=var, command=self._sendSwitchData,
                style='switch.TCheckbutton')
            if enabled:
                var.set(1)
            checkbutton.pack(side=LEFT)

    def _sendSwitchData(self):
        if self.robotConnection == None:
            return
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
        color = _getLogStateColor(name)

        stateFrame = Frame(self.logFrame, bg=color,
                           borderwidth=3, relief=RAISED)
        stateFrame.pack(side=TOP, fill=X)
        
        titleLabel = ttk.Label(stateFrame, text=name + ": ",
                               font=ThisIsTheDashboardApp.LOG_STATE_TITLE_FONT,
                               background=color)
        titleLabel.pack(side=LEFT)
        valueLabel = ttk.Label(stateFrame, text="None",
                               font=ThisIsTheDashboardApp.LOG_STATE_FONT,
                               background=color)
        valueLabel.pack(side=LEFT)

        self.logStateLabels[name] = valueLabel

    def _commandButtonPressed(self):
        self.robotConnection.sendCommand(self.commandEntry.get())

def _getLogStateColor(title):
    titleHash = hashlib.sha256()
    titleHash.update(title.encode('utf-8'))
    hashValue = titleHash.digest()
    hue = hashValue[0]
    r,g,b = colorsys.hsv_to_rgb(float(hue)/256.0, 0.6, 1.0)
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
    filename = filedialog.askopenfilename(title="Choose a switches file...",
                                          filetypes=[('Text Files', '*.txt'),
                                                     ('All Files', '*')])
    if filename == '':
        exit()

    root.geometry("+112+0")
    app = ThisIsTheDashboardApp(root, switchFileName=filename)
    root.mainloop()
