import wpilib
from networktables import NetworkTables

class DashboardTestRobot(wpilib.IterativeRobot):

    def robotInit(self):
        self.table = NetworkTables.getTable('dashboard')
        self.testNumber = 0

    def teleopInit(self):
        print(self.table.getStringArray('switchnames'))
        print(self.table.getBooleanArray('switchvalues'))

    def teleopPeriodic(self):
        self.table.putStringArray('logstatenames', ['abc','def','test'])
        self.table.putStringArray('logstatevalues', ['123','456',
                                                     str(self.testNumber)])
        self.testNumber += 1

if __name__ == "__main__":
    wpilib.run(DashboardTestRobot)
