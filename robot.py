from myrobot import MyRobot
robot = MyRobot()

ARDUINO_SN = ""


def test(myRobot):
    while True:
        markers = myRobot.look()
        bestMarker = myRobot.chooseBestFace(markers)
        myRobot.goToBoxShort(bestMarker)

def compCode(myRobot): #Code for actual robot
    while True:
        if myRobot.targetFace == []:
            myRobot.findBestMarker()
        elif not myRobot.reachedTarget:
            myRobot.goToBoxShort(myRobot.targetFace)
        else:
            if myRobot.isTargetBox:
                myRobot.grab()
                myRobot.scissorUp(130) #Lifts box height of one box
            else: #If target is a high rise
                myRobot.scissorUp(135) #Slightly higher than actual high rise for clearance
                myRobot.release()
                #need to remove id from target ids after being placed (maybe)
                myRobot.reset() #Start loop again to look for next box


def extra():
    global ARDUINO_SN
    while True:
        robot.raw_serial_devices[ARDUINO_SN].write(b"0")
        robot.sleep(1)
        robot.raw_serial_devices[ARDUINO_SN].write(b"150")
        robot.sleep(1)

test(robot)
compCode(robot)