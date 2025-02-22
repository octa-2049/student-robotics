import math

from myrobot import MyRobot

myRobot = MyRobot()

while True:

        else:


def test(myRobot):
    while True:
        # myRobot.turn(0.2)
        # myRobot.targetIDs = myRobot.palletIDs
        # myRobot.look(80)
        # print(myRobot.markerInfo)
        #myRobot.goToBoxLong(80)
        mark = (myRobot.look(myRobot.palletIDs))
        if mark != None:
            print(mark.id)
            roll = mark.orientation.roll
            roll = myRobot.roundRollDeg(roll)
            print(mark.orientation.roll)
            print(mark.orientation.yaw)
            print(mark.orientation.pitch)

strat1(myRobot)
test(myRobot)