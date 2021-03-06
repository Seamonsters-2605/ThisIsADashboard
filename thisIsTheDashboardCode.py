
__author__ = "seamonsters"

import hashlib
import colorsys
import random
import socket

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from networktables import NetworkTables

try:
    from PIL import Image
    from PIL import ImageTk
    import numpy as np
    import requests

    try:
        from cv2 import cv2  # idk
    except:
        import cv2
except:
    print("Camera support is not available! (numpy, opencv-python, pillow, requests required)")
from threading import Thread


class RobotConnection:

    def __init__(self, ip, cameraStreamLabel):
        print("Attempting to connect to", ip)
        NetworkTables.initialize(server=ip)
        self.table = NetworkTables.getTable('dashboard')
        self.commandTable = NetworkTables.getTable('commands')
        self.cam = None
        self.cameraStreamLabel = cameraStreamLabel

    def isConnected(self):
        return NetworkTables.isConnected()

    def disconnect(self):
        NetworkTables.shutdown()
        if self.cam:
            self.cam.stop()

    def getLogStates(self):
        self.updateCamera()
        logStateNames = self.table.getStringArray('logstatenames', [])
        logStateValues = self.table.getStringArray('logstatevalues', [])
        logStates = {}
        for i in range(0, len(logStateNames)):
            logStates[logStateNames[i]] = logStateValues[i]
        return logStates

    def updateCamera(self):
        url = self.table.getString('cam', '')
        if url == '':
            if self.cam != None:
                self.cam.stop()
                self.cam = None
        else:
            if self.cam != None and url != self.cam.url:
                self.cam.stop()
                self.cam = None
            if self.cam == None:
                try:
                    self.cam = CameraStream(url, self.cameraStreamLabel)
                    self.cam.start()
                except:
                    pass

    def sendSwitchData(self, switches):
        print(switches)
        switchNames = [name for name, value in switches.items()]
        switchValues = [value for name, value in switches.items()]
        self.table.putStringArray('switchnames', switchNames)
        self.table.putBooleanArray('switchvalues', switchValues)

    def sendNumData(self,Lpause, Rpause):
        p = {'leftpause':Lpause,'rightpause':Rpause}
        for k,v in p.items():
            try:
                self.table.putNumber(k,float(v))
                print(k, v)
            except ValueError:
                print('this ',k,'value',v,'is not a number!')
                self.table.putNumber(k,0)

    def sendCommand(self, command):
        lastId = self.commandTable.getNumber('id', None)
        if lastId == None:
            print("Robot won't accept commands!")
            return
        newId = lastId
        while newId == lastId:
            newId = random.randrange(1, 65536)
        print(lastId, newId)
        self.commandTable.putString('command', command)
        self.commandTable.putNumber('id', newId)
        print(self.commandTable.getString('command', 'NO COMMAND!'))


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
                # ,'Test number': str(self.testNumber),
                }

    def sendSwitchData(self, switches):
        print(switches)

    def sendNumData(self, Lpause, Rpause):
        print("Left pause", Lpause)
        print("Right pause", Rpause)

    def sendCommand(self, command):
        print("Command:", command)


# http://benhowell.github.io/guide/2015/03/09/opencv-and-web-cam-streaming
class CameraStream:

    def __init__(self, url, cameraStreamLabel):
        self.url = url
        self.thread = Thread(target=self.run)
        self.label = cameraStreamLabel
        print("Camera initialised")

    def start(self):
        self.thread.start()

    def isRunning(self):
        return self.thread.is_alive()

    def stop(self):
        self.stopThread = True

    def run(self):
        print("Starting camera stream...")
        try:
            stream = requests.get(self.url, stream=True)
        except:
            print("Couldn't connect to camera")
            return
        self.stopThread = False
        streamBytes = bytes()
        try:
            while not self.stopThread:
                streamBytes += stream.raw.read(256)
                a = streamBytes.find(b'\xff\xd8')
                b = streamBytes.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = streamBytes[a:b + 2]
                    streamBytes = streamBytes[b + 2:]
                    image = cv2.imdecode(
                        np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    image = Image.fromarray(image)
                    b, g, r = image.split()
                    image = Image.merge("RGB", (r, g, b))
                    image = image.resize((image.width * 2, image.height * 2))
                    image = ImageTk.PhotoImage(image)
                    self.label.config(image=image)
                    self.label.image = image
        finally:
            stream.close()
            print("Camera stream stopped")


class ThisIsTheDashboardApp:
    LOG_STATE_TITLE_FONT = ("Segoe UI", 18)
    LOG_STATE_FONT = ("Segoe UI Light", 18)
    IMPORTANT_LOG_STATE_FONT = ("Segoe UI", 18, "bold underline")
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
        root.title("Seamonsters")

        frame = ttk.Frame(root)
        frame.pack(fill=BOTH, expand=True)

        leftFrame = ttk.Frame(frame)
        leftFrame.pack(side=LEFT, fill=Y)

        subFrame = ttk.Frame(frame)
        subFrame.pack(side=LEFT, fill=Y)

        ttk.Label(leftFrame, text="2605", style='logo.TLabel').pack(side=TOP)

        resetButton = ttk.Button(leftFrame, text="Reset",
                                 style='dashboard.TButton', command=self._resetButtonPressed)
        resetButton.pack(side=TOP, fill=X)

        self.ipComboBoxVar = StringVar()
        ipComboBox = ttk.Combobox(leftFrame, textvariable=self.ipComboBoxVar,
                                  values=['10.26.5.2',
                                          socket.gethostbyname(socket.gethostname()),
                                          'roborio-2605-frc.local',
                                          'test'])
        ipComboBox.current(0)
        ipComboBox.pack(side=TOP, fill=X)

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

        commandFrame = ttk.Frame(leftFrame)
        commandFrame.pack(side=TOP, fill=X)

        self.commandEntry = ttk.Entry(commandFrame)
        self.commandEntry.pack(side=LEFT, fill=BOTH, expand=True)
        self.commandEntry.focus()

        self.commandButton = ttk.Button(commandFrame, text="Send", width=5,
                                        style='dashboard.TButton', command=self._commandButtonPressed,
                                        state=DISABLED)
        self.commandButton.pack(side=LEFT)

        self.switchFrame = ttk.Frame(leftFrame, borderwidth=3, relief=GROOVE,
                                     padding=8)
        self.switchFrame.pack(side=TOP, fill=X)

        self.switchVars = {}

        self.numFrame = ttk.Frame(leftFrame, borderwidth=3, relief=GROOVE,
                                  padding=8)
        self.numFrame.pack(side=BOTTOM, fill=X)
        Label(self.numFrame,text="Left Pause").grid(row=0,column=0)
        Label(self.numFrame,text="Right Pause").grid(row=1,column=0)

        self.Lpause = ttk.Entry(self.numFrame)
        self.Lpause.grid(row=0,column=1)

        self.Rpause = ttk.Entry(self.numFrame)
        self.Rpause.grid(row=1,column=1)

        self.enterButton = ttk.Button(self.numFrame, text='Enter',
                                 style='dashboard.TButton',
                                 command=self._enterButtonPressed)
        self.enterButton.grid(row=2,column=1)

        self.cameraStreamLabel = Label(frame)
        self.cameraStreamLabel.pack(side=LEFT, anchor=N)

        self.logFrame = ttk.Frame(frame, padding=(20, 0, 0, 0))
        self.logFrame.pack(side=LEFT, fill=X, expand=True, anchor=N)

        self.logStateLabels = {}

    def _connectButtonPressed(self):
        ip = self.ipComboBoxVar.get()
        try:
            if ip.strip().lower() == 'test':
                self.robotConnection = TestRobotConnection()
            else:
                self.robotConnection = RobotConnection(ip,
                                                       self.cameraStreamLabel)
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
    def _resetButtonPressed(self):
        self.logStateLabels = {}
        for child in self.logFrame.winfo_children():
            child.destroy()
        # taking this out for now, it resets all of the switch values which might be bad
        # self._updateSwitches()
        self.cameraStreamLabel.config(image='')
        self.cameraStreamLabel.image = None

    def _enterButtonPressed(self):
        self.robotConnection.sendNumData(self.Lpause.get(),self.Rpause.get())

    def _connected(self):
        self.connectButton.config(state=DISABLED)
        self.disconnectButton.config(state=NORMAL)
        self.commandButton.config(state=NORMAL)
        self.progress.stop()
        self.progressVar.set(ThisIsTheDashboardApp.PROGRESS_MAX)

        self._sendSwitchData()
        self._enterButtonPressed()

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
        self._resetButtonPressed()

    def _disconnectedError(self):
        self._disconnected()
        messagebox.showerror("Dashboard Error", "Connection Failed!")

    def _updateSwitches(self):
        with open(self.switchFileName) as f:
            switches, optionsets = readSwitchConfig(f)

        for child in self.switchFrame.winfo_children():
            child.destroy()
        self.switchVars = {}
        self.optionVars = {}
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
        for optionsetName, optionset in optionsets.items():
            ComboBox = ttk.Combobox(self.switchFrame,
                                    values =[k for k in optionset.keys()])
            ComboBox.bind("<<ComboboxSelected>>", self._sendSwitchData)
            ComboBox.current(0)
            ComboBox.pack(side=TOP, fill=X)
            for optionName, enabled in optionset.items():
                self.optionVars[optionName] = ComboBox

    def _sendSwitchData(self,event=None):
        if self.robotConnection == None:
            return
        switches = {}
        for name, var in self.switchVars.items():
            switches[name] = var.get() == 1

        for name, var in self.optionVars.items():
            if name == var.get():
                switches[name] = True
            else:
                switches[name] = False
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
    r, g, b = colorsys.hsv_to_rgb(float(hue) / 256.0, 0.6, 1.0)
    colorHex = '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))
    return colorHex


def readSwitchConfig(file):
    content = file.readlines()
    switchNames = {}
    optionSets = {}
    for line in content:
        line = line.strip()
        if len(line) == 0:
            continue
        firstCharacter = line[0]
        if firstCharacter == ':':
            options = line[1:].split(',')
            options = [o.strip() for o in options]
            optionSets[options[0]] = {}
            for i, op in enumerate(options):
                optionSets[options[0]][op] = True if i == 0 else False
        else:
            switchName = line[1:]
            if firstCharacter == "+":
                switchEnabled = True
            elif firstCharacter == "-":
                switchEnabled = False
            else:
                switchName = line
                print("Switch", switchName, "doesn't have enabled state!")
                switchEnabled = False

            switchNames[switchName] = switchEnabled
    return switchNames, optionSets


if __name__ == "__main__":
    root = Tk()
    filename = filedialog.askopenfilename(title="Choose a switches file...",
                                          filetypes=[('Text Files', '*.txt'),
                                                     ('All Files', '*')])
    if filename == '':
        exit()

    root.geometry("+0+0")
    app = ThisIsTheDashboardApp(root, switchFileName=filename)
    root.mainloop()
