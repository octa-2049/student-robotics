from myrobot import MyRobot
robot = MyRobot()

def test():
    while True:
        print("Distance: ", robot.getUltrasoundDistance())
        print("Holding box: ", robot.isHoldingBox())
        print("Is box near: ", robot.isBoxNear())

        if robot.isBoxNear() and not robot.isHoldingBox():
            robot.grab()
        elif not robot.isBoxNear():
            # print("Releasing")
            robot.release()


def planB(myRobot):
    palletID = 0  # Stored until box released next to
    while True:
        if myRobot.isTargetBox:
            if not myRobot.hasTarget:
                print("Finding pallet marker")
                myRobot.findBestMarker()
            elif not myRobot.reachedTarget:
                print("Going to pallet", myRobot.targetID)
                myRobot.goToBoxStraight(myRobot.targetID)
            elif myRobot.isBoxNear() and not myRobot.isHoldingBox():
                myRobot.grab()
            else:
                palletID = myRobot.targetID
                print("Has box ", palletID, " going to high rise")
                myRobot.isTargetBox = False
                myRobot.resetVariables()

        elif not myRobot.isHoldingBox():
            if myRobot.isBoxNear():
                print("Box near but not grabbed")
                myRobot.release()
                myRobot.sleep(0.5)
                myRobot.move(-myRobot.MAX_SPEED, 50)
                myRobot.move(myRobot.MAX_SPEED, 100)
                myRobot.grab()
            else:
                print("Box lost")
                myRobot.isTargetBox = True
                myRobot.resetVariables()

        else:  # If target is a high rise
            if not myRobot.hasTarget:
                print("Finding high rise marker")
                myRobot.findBestMarker()
            elif not myRobot.reachedTarget:
                print("Going to high rise", myRobot.targetID)
                myRobot.goToHighRise(myRobot.targetID)
            else:
                myRobot.release()
                print("Deposited box", palletID)
                if palletID in myRobot.palletIDs:
                    myRobot.palletIDs.remove(palletID)
                print("Pallet ids left:", myRobot.palletIDs)
                myRobot.move(-myRobot.MAX_SPEED, 500)
                myRobot.isTargetBox = True
                print("Going to next box")
                myRobot.resetVariables()  # Start loop again to look for next box


def planC(myRobot):
    #NEED TO USE DIFFERENT RANDOM MOVEMENT IF NOT GRABBING
    palletID = 0  # Stored until box released
    while True:
        if myRobot.isTargetBox:
            if not myRobot.hasTarget:
                print("Finding pallet marker")
                myRobot.findBestMarker()
            elif not myRobot.reachedTarget:
                print("Going to pallet")
                myRobot.goToBoxStraight(myRobot.targetID)
            else:
                palletID = myRobot.targetID
                print("Got box", palletID, "going to highrise")
                myRobot.isTargetBox = False
                myRobot.resetVariables()

        elif not myRobot.isBoxNear():
            print("Box lost")
            myRobot.isTargetBox = True
            myRobot.resetVariables()

        else:  # If target is a high rise
            if not myRobot.hasTarget:
                print("Finding high rise marker")
                myRobot.findBestMarker()
            elif not myRobot.reachedTarget:
                print("Going to high rise")
                myRobot.goToHighRise(myRobot.targetID)
            else:
                if palletID in myRobot.palletIDs:
                    myRobot.palletIDs.remove(palletID)
                print("Pallet ids:", myRobot.palletIDs)
                myRobot.move(-myRobot.MAX_SPEED, 500)
                myRobot.isTargetBox = True
                print("Going to next box")
                myRobot.resetVariables()  # Start loop again to look for next box

def test(myRobot):
    while True:
        print("Nothing running: ")
        myRobot.getBatteryStatus()
        myRobot.getWheelCurrent()
        print("Moving straight: ")
        myRobot.move(myRobot.MAX_SPEED)
        myRobot.getBatteryStatus()
        myRobot.getWheelCurrent()
        myRobot.sleep(5)
        myRobot.stop()
        myRobot.sleep(5)
        print("Turning: ")
        myRobot.turn(myRobot.MAX_SPEED)
        myRobot.getBatteryStatus()
        myRobot.getWheelCurrent()
        myRobot.sleep(5)
        robot.stop()
        myRobot.sleep(5)

def testGoToDistrict(myRobot):
    while True:
        if not myRobot.hasTarget:
            print("Finding best outer district marker")
            myRobot.findBestMarker(myRobot.outerDistricts[0])
        elif not myRobot.reachedTarget:
            print("Going to outer district")
            myRobot.goToOuterDistrict(myRobot.targetID)
        else:
            print("Reached outer district")

robot.palletIDs = [100, 101, 103,104]
robot.outerHighriseIDs = [102]

#planB(robot)
#planC(robot)
#test(robot)


