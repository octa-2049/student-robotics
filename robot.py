from myrobot import MyRobot

robot = MyRobot()


def test(myRobot):
    while True:
        if not myRobot.hasTarget:
            print("FINDING TARGET")
            myRobot.findBestPallet()
        elif not myRobot.reachedTarget:
            print("GOING TO BOX")
            myRobot.goToBoxLong(myRobot.targetID)
        elif not myRobot.isHoldingBox():
            print("GRABBING BOX")
            myRobot.grab()
        else:
            myRobot.move(-myRobot.MAX_SPEED, 300)
            return None


def compCode(myRobot):  # Code for actual robot
    while True:
        if not myRobot.hasTarget:
            if myRobot.isTargetBox:
                myRobot.findBestPallet()
            else:
                myRobot.goToHighRise(myRobot.targetID)
        elif not myRobot.reachedTarget:
            myRobot.goToBoxStraight(myRobot.targetID)
        else:
            if myRobot.isTargetBox:
                myRobot.grab()
                myRobot.scissorLift(130)  # Lifts box height of one box
            else:  # If target is a high rise
                myRobot.scissorLift(135)  # Slightly higher than actual high rise for clearance
                myRobot.release()
                myRobot.move(-myRobot.MAX_SPEED, 200)
                myRobot.scissorLift(0)
                # need to remove id from target ids after being placed (maybe)
                myRobot.resetVariables()  # Start loop again to look for next box


def planB(myRobot):
    myRobot.palletIDs = [100, 101, 103]
    myRobot.outerHighriseIDs = [102]
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
                print("Grabbing pallet")
                myRobot.grab()
                palletID = myRobot.targetID
            else:
                print("Going to high rise")
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
                print("Releasing box")
                myRobot.release()
                myRobot.palletIDs.remove(palletID)
                print("Pallet ids:", myRobot.palletIDs)
                myRobot.move(-myRobot.MAX_SPEED, 500)
                myRobot.isTargetBox = True
                print("Going to next box")
                myRobot.resetVariables()  # Start loop again to look for next box

def planC(myRobot):
    #NEED TO USE NO RANDOM MOVEMENT IF NOT GRABBING
    myRobot.palletIDs = [100, 101, 103]
    myRobot.outerHighriseIDs = [102]
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
                #myRobot.palletIDs.remove(palletID)
                print("Pallet ids:", myRobot.palletIDs)
                myRobot.move(-myRobot.MAX_SPEED, 500)
                myRobot.isTargetBox = True
                print("Going to next box")
                myRobot.resetVariables()  # Start loop again to look for next box



def testEncoders(robot):
    my_motor_board = robot.motor_board
    total_speed0 = 0
    total_speed1 = 0
    count = 0
    for i in range(5000):
        my_motor_board.motors[0].power = 0.5
        my_motor_board.motors[1].power = 0.96482070964 * 0.5
        speed0 = float(robot.arduino.command("m"))
        speed1 = float(robot.arduino.command("x"))
        total_speed0 += speed0
        total_speed1 += speed1
        count += 1
    print("Average speed Motor 0:", total_speed0 / count)
    print("Average speed Motor 1:", total_speed1 / count)


def scissorLift(height, lift_speed_down, lift_speed_up):
    target_height = float(height)
    current_height = 0.00
    print("Not in loop")
    print(current_height != target_height)
    print(current_height)
    print(target_height)
    tolerance = 0.01
    # multiplier = 2140 #to be confirmed
    while current_height != target_height:
        print("in loop")
        motor2position = robot.arduino.command("b")
        # motor3position = robot.arduino.command("c")
        # print(motor2position, motor3position)
        # average_position = (float(abs(motor2position)) + float(abs(motor3position))) / 2
        current_height = abs(float(motor2position))
        print("Current height is: ", current_height)
        if current_height > target_height:
            robot.motor_boards["SR0TDC"].motors[0].power = lift_speed_down
            # robot.motor_boards["SR0TDC"].motors[1].power = lift_speed_down
        else:
            robot.motor_boards["SR0TDC"].motors[0].power = lift_speed_up
            # robot.motor_boards["SR0TDC"].motors[1].power = lift_speed_up
    robot.motor_boards["SR0TDC"].motors[0].power = 0
    # robot.motor_boards["SR0TDC"].motors[1].power = 0


def motors(robot):
    robot.motor_boards["SR0TDC"].motors[0].power = 1.0
    robot.sleep(10)
    robot.motor_boards["SR0TDC"].motors[0].power = -0.7
    robot.sleep(10)


# test(robot)
# motors(robot)

#planB(robot)
#robot.grab()
planC(robot)