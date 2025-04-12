from myrobot import MyRobot
robot = MyRobot()

def planB(myRobot):

    palletID = 0  # Stored until box released next to
    start = myRobot.time
    end = myRobot.time
    while True:
        myRobot.getBatteryStatus()
        if myRobot.isTargetBox:
            if not myRobot.hasTarget:
                print("Finding pallet marker")
                myRobot.findBestMarker(myRobot.palletIDs)
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

        elif myRobot.boxesPlaced == 3:
            if not myRobot.hasTarget:
                print("Finding best outer district marker")
                myRobot.findBestMarker(myRobot.outerDistricts[0])
            elif not myRobot.reachedTarget:
                print("Going to outer district")
                myRobot.goToOuterDistrict(myRobot.targetID)
            else:
                if palletID in myRobot.palletIDs:
                    myRobot.palletIDs.remove(palletID)
                    myRobot.boxesPlaced += 1
                print("Pallet ids:", myRobot.palletIDs)
                myRobot.move(-myRobot.MAX_SPEED, 500)
                myRobot.isTargetBox = True
                print("Going to next box")
                myRobot.resetVariables()

        elif myRobot.boxesPlaced == 4:
            if not myRobot.hasTarget:
                print("Finding best inner high rise marker")
                myRobot.findBestMarker(myRobot.innerHighriseID)
            elif not myRobot.reachedTarget:
                print("Going to outer district")
                myRobot.goToOuterDistrict(myRobot.targetID)
            else:
                if palletID in myRobot.palletIDs:
                    myRobot.palletIDs.remove(palletID)
                    myRobot.boxesPlaced += 1
                print("Pallet ids:", myRobot.palletIDs)
                myRobot.move(-myRobot.MAX_SPEED, 500)
                myRobot.isTargetBox = True
                print("Going to next box")
                myRobot.resetVariables()

        else:  # If target is a high rise
            if not myRobot.hasTarget:
                print("Finding high rise marker")
                myRobot.findBestMarker(myRobot.outerHighriseIDs)
            elif not myRobot.reachedTarget:
                print("Going to high rise", myRobot.targetID)
                myRobot.goToHighRise(myRobot.targetID)
            else:
                myRobot.release()
                print("Deposited box", palletID)
                if palletID in myRobot.palletIDs:
                    myRobot.palletIDs.remove(palletID)
                    myRobot.boxesPlaced += 1
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
                myRobot.findBestMarker(myRobot.palletIDs)
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

        elif myRobot.boxesPlaced > 2:
            if not myRobot.hasTarget:
                print("Finding best outer district marker")
                myRobot.findBestMarker(myRobot.outerDistricts[0])
            elif not myRobot.reachedTarget:
                print("Going to outer district")
                myRobot.goToOuterDistrict(myRobot.targetID)
            else:
                if palletID in myRobot.palletIDs:
                    myRobot.palletIDs.remove(palletID)
                    myRobot.boxesPlaced += 1
                print("Pallet ids:", myRobot.palletIDs)
                myRobot.move(-myRobot.MAX_SPEED, 500)
                myRobot.isTargetBox = True
                print("Going to next box")
                myRobot.resetVariables()  # Start loop again to look for next box

        else:  # If target is a high rise
            if not myRobot.hasTarget:
                print("Finding high rise marker")
                myRobot.findBestMarker(myRobot.outerHighriseIDs)
            elif not myRobot.reachedTarget:
                print("Going to high rise")
                myRobot.goToHighRise(myRobot.targetID)
            else:
                if palletID in myRobot.palletIDs:
                    myRobot.palletIDs.remove(palletID)
                    myRobot.boxesPlaced += 1
                print("Pallet ids:", myRobot.palletIDs)
                myRobot.move(-myRobot.MAX_SPEED, 500)
                myRobot.isTargetBox = True
                print("Going to next box")
                myRobot.resetVariables()  # Start loop again to look for next box

def testCurrent(myRobot):
    leftCurrent, rightCurrent = myRobot.getWheelCurrent()
    while leftCurrent < myRobot.MAX_CURRENT and rightCurrent < myRobot.MAX_CURRENT:
        #print("Nothing running: ")
        #myRobot.getBatteryStatus()
        myRobot.getWheelCurrent()
        #print("Moving straight: ")
        myRobot.move(myRobot.MAX_SPEED)
        # myRobot.getBatteryStatus()
        # myRobot.getWheelCurrent()
        # myRobot.sleep(5)
        # myRobot.stop()
        # myRobot.sleep(5)
        # print("Turning: ")
        # myRobot.turn(myRobot.MAX_SPEED)
        # myRobot.getBatteryStatus()
        # myRobot.getWheelCurrent()
        # myRobot.sleep(5)
        # robot.stop()
        # myRobot.sleep(5)
        leftCurrent, rightCurrent = myRobot.getWheelCurrent()

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

def testDutyLimits(myRobot):
    while True:
        myRobot.release()
        print("1700")
        myRobot.GRAB_SERVO.set_duty_limits(700, 1700)
        myRobot.grab()
        myRobot.release()
        print("1750")
        myRobot.GRAB_SERVO.set_duty_limits(700, 1750)
        myRobot.grab()
        myRobot.release()
        print("1800")
        myRobot.GRAB_SERVO.set_duty_limits(700, 1800)
        myRobot.grab()
        myRobot.release()
        print("1850")
        myRobot.GRAB_SERVO.set_duty_limits(700, 1850)
        myRobot.grab()
        myRobot.release()
        print("1900")
        myRobot.GRAB_SERVO.set_duty_limits(700, 1900)

def testGrabbing(myRobot):
    while True:
        if myRobot.isHoldingBox():
            myRobot.stop()
            return True
        elif myRobot.isBoxNear():
            myRobot.stop()
            myRobot.grab()
        else:
            myRobot.move(0.2)
            myRobot.sleep(1)

def test(myRobot):
    start = myRobot.time()
    myRobot.sleep(5)
    end = myRobot.time()
    print(start-end)

# robot.palletIDs = [100, 101, 103,104]
# robot.outerHighriseIDs = [102]
# zone = 2
# robot.PALLETS = robot.localMarkerIDs[zone]
# robot.palletIDs = robot.localMarkerIDs[zone]


planB(robot)
#planC(robot)
#testCurrent(robot)
#testGoToDistrict(robot)
#testDutyLimits(robot)

#robot.getSquareOn(26)
#testGrabbing(robot)
#test(robot)
