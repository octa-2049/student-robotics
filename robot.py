import math

from myrobot import MyRobot

SPEED = 0.2

roboxer = MyRobot()

def strat1(myRobot):
    while True:
        if myRobot.targetFace != []:
            myRobot.findBestMarker()

        elif not myRobot.linedUp:
            myRobot.lineUp(myRobot.targetFace.id, myRobot.getRoll(myRobot.targetFace))

        elif not myRobot.reachedTarget:
            myRobot.goToBoxShort()


def extra():
    global ARDUINO_SN
    while True:
        robot.raw_serial_devices[ARDUINO_SN].write(b"0")
        robot.sleep(1)
        robot.raw_serial_devices[ARDUINO_SN].write(b"150")
        robot.sleep(1)

def test(myRobot):
    myRobot.goToBoxShort(100)
    # while True:
    #     # myRobot.turn(0.2)
    #     # myRobot.targetIDs = myRobot.palletIDs
    #     # myRobot.look(80)
    #     # print(myRobot.markerInfo)
    #     #myRobot.goToBoxLong(80)
    #     mark = (myRobot.look(myRobot.palletIDs))
    #     if mark != None:
    #         print(mark.id)
    #         roll = mark.orientation.roll
    #         roll = myRobot.roundRollDeg(roll)
    #         print(mark.orientation.roll)
    #         print(mark.orientation.yaw)
    #         print(mark.orientation.pitch)

#strat1(roboxer)
test(roboxer)
