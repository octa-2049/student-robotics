from myrobot import MyRobot
robot = MyRobot()

ARDUINO_SN = ""


def test(myRobot):
    while True:
        myRobot.goToBoxShort(100)

def compCode(myRobot): #Code for actual robot
    while True:
        if myRobot.targetFace != []:
            myRobot.findBestMarker()

        elif not myRobot.linedUp:
            myRobot.lineUp(myRobot.targetFace.id, myRobot.getRoll(myRobot.targetFace))

        elif not myRobot.reachedTarget:
            myRobot.goToBoxShort(myRobot.targetFace)

def extra():
    global ARDUINO_SN
    while True:
        robot.raw_serial_devices[ARDUINO_SN].write(b"0")
        robot.sleep(1)
        robot.raw_serial_devices[ARDUINO_SN].write(b"150")
        robot.sleep(1)

test(robot)
compCode(robot)