__author__ = "jacobvanthoog"

from tkinter import *
import hashlib
from tkinter import filedialog
from tkinter import messagebox
import colorsys
from networktables import NetworkTables
import subprocess



TEST_MODE = False

class RobotConnection:

    def __init__(self):
        NetworkTables.initialize(server="roborio-2605-frc.local")
        self.contoursTable = NetworkTables.getTable('contours')
        self.table = NetworkTables.getTable('dashboard')

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

    def getContours(self):
        """
        A coordinate is a tuple of 2 values. A contour is a list of coordinates.
        This function returns a list of contours - so a list of lists of tuples.
        """
        try:
            return self._readContours(self.contoursTable.getNumberArray('x'),
                                       self.contoursTable.getNumberArray('y'))
        except BaseException:
            print("Vision connection error!")
            return [ ]

    def _readContours(self, xCoords, yCoords):
        # check data
        if len(xCoords) != len(yCoords):
            print("ERROR: Incorrect contour data! "
                  "len(xCoords) != len(yCoords)")
            return []
        numContours = xCoords.count(-1)
        if numContours != yCoords.count(-1):
            print("ERROR: Incorrect contour data! "
                  "xCoords.count(-1) != yCoords.count(-1)")
            return []

        contours = []
        currentContour = []
        for i in range(0, len(xCoords)):
            x = xCoords[i]
            y = yCoords[i]
            if x == -1:
                if len(currentContour) != 0:
                    contours.append(currentContour)
                currentContour = []
            else:
                currentContour.append((x, y))
        if len(currentContour) != 0:
            contours.append(currentContour)

        return contours

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

    def getContours(self):
        return [ [(30, 100), (30, 200), (70, 200)],
                 [(150, 100), (150, 200), (190, 200)] ]

    def sendSwitchData(self, switches):
        print(switches)


class ThisIsTheDashboardApp:

    DISCONNECTED_COLOR = "#AAAAAA"
    CONNECTED_COLOR = "#55FF55"
    ERROR_COLOR = "#FF0000"
    WAIT_COLOR = "#FFFF00"

    LOG_STATE_FONT = ("Helvetica", 24)
    IMPORTANT_LOG_STATE_FONT = ("Helvetica", 24, "bold underline")
    CONNECT_BUTTON_FONT = ("Helvetica", 16)

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
                               font=ThisIsTheDashboardApp.CONNECT_BUTTON_FONT,
                               command = self._connectButtonPressed,
                               bg=ThisIsTheDashboardApp.DISCONNECTED_COLOR)
        self.connectButton.pack(side=TOP, fill=X)
        self.disconnectButton = Button(leftFrame, height=2, text="Disconnect",
            font=ThisIsTheDashboardApp.CONNECT_BUTTON_FONT, state=DISABLED,
            command = self._disconnectButtonPressed)
        self.disconnectButton.pack(side=TOP, fill=X)

        self.shutdown = Button(leftFrame, height=2, text="Shut Down Pi",
                                font=ThisIsTheDashboardApp.CONNECT_BUTTON_FONT,
                                command = self.shutdownButtonPressed)
        self.shutdown.pack(side=TOP, fill= X)
        separator = Frame(frame, width=12)
        separator.pack(side=LEFT)

        self.logFrame = Frame(frame, borderwidth=3, relief=SUNKEN)
        self.logFrame.pack(side=LEFT, fill=X, expand=True)
        
        self.logStateLabels = { }


        self.canvas = Canvas(frame, width=640, height=480)
        self.canvas.pack()


    def _connectButtonPressed(self):
        global TEST_MODE
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

    def shutdownButtonPressed(self):
        try:
            subprocess.run("plink.exe -ssh pi@raspberrypi -pw sehome \"sudo shutdown -h now\"",
                           check=True, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            error = e.stderr
            if error == None:
                error = ""
            else:
                error = error.decode("utf-8")
            messagebox.showerror(
                "Error while shutting down",
                error
            )
        except BaseException as e:
            messagebox.showerror(
                "Unrecognized error while shutting down",
                str(e)
            )

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
        self._disconnectedSuccess()

    def _connected(self):
        self.connectButton.config(bg=ThisIsTheDashboardApp.CONNECTED_COLOR,
                                  state=DISABLED)
        self.disconnectButton.config(state=NORMAL)

    def _waiting(self):
        self.connectButton.config(bg=ThisIsTheDashboardApp.WAIT_COLOR,
                                  state=DISABLED)
        self.disconnectButton.config(state=DISABLED)

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

        # update contours
        self.canvas.delete("all")
        contours = self.robotConnection.getContours()
        for contourPoints in contours:
            if len(contourPoints) < 2:
                continue
            for i in range(0, len(contourPoints)):
                point = contourPoints[i]
                prevPoint = contourPoints[i - 1]
                self.canvas.create_line(point[0], point[1],
                                        prevPoint[0], prevPoint[1])

        self.root.after(100, self._updateLogStates)

    def _addLogStateLabel(self, name):
        color = _getLogStateColor(name)
        
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

def _getLogStateColor(title):
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
    file = filedialog.askopenfile(title="Choose a switches file...",
                                  filetypes=[('Text Files', '*.txt'),
                                             ('All Files', '*')])
    if file == None:
        exit()
    switches = readSwitchConfig(file)
    file.close()
    app = ThisIsTheDashboardApp(root, switches = switches)
    root.mainloop()
