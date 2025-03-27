from myrobot import MyRobot
robot = MyRobot()

def test():
    return None

def planB(myRobot):
    # NEED TO USE NO RANDOM MOVEMENT IF NOT GRABBING
    palletID = 0  # Stored until box released next to
    while True:
        if myRobot.isTargetBox:
            if not myRobot.hasTarget:
                print("Finding pallet marker")
                myRobot.findBestMarker()
            elif not myRobot.reachedTarget:
                print("Going to pallet")
                myRobot.goToBoxStraight(myRobot.targetID)
            elif not myRobot.isHoldingBox():
                myRobot.grab()
            else:
                print("Going to high rise")
                palletID = myRobot.targetID
                myRobot.isTargetBox = False
                myRobot.resetVariables()
        elif not myRobot.isHoldingBox:
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
                myRobot.release()
                if palletID in myRobot.palletIDs:
                    myRobot.palletIDs.remove(palletID)
                print("Pallet ids:", myRobot.palletIDs)
                myRobot.move(-myRobot.MAX_SPEED, 500)
                myRobot.isTargetBox = True
                print("Going to next box")
                myRobot.resetVariables()  # Start loop again to look for next box


def planC(myRobot):
    #NEED TO USE NO RANDOM MOVEMENT IF NOT GRABBING
    palletID = 0  # Stored until box released next to
    while True:
        if myRobot.isTargetBox:
            if not myRobot.hasTarget:
                print("Finding pallet marker")
                myRobot.findBestMarker()
            elif not myRobot.reachedTarget:
                print("Going to pallet")
                myRobot.goToBoxStraight(myRobot.targetID)
            else:
                print("Going to high rise")
                palletID = myRobot.targetID
                myRobot.isTargetBox = False
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

robot.palletIDs = [100, 101, 103,104]
robot.outerHighriseIDs = [102]

planB(robot)
#planC(robot)
