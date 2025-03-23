from myrobot import MyRobot
import math
robot = MyRobot()

ARDUINO_SN = ""


def test(myRobot):
    markers = myRobot.look()
    while True:
        markers = myRobot.look()
        if markers != []:
            myRobot.stop()
            return myRobot.goToBoxLong(myRobot.targetID)

        else:
            myRobot.turn(myRobot.MAX_SPEED)
            #robot.sleep(1)

def compCode(myRobot): #Code for actual robot
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
                myRobot.scissorLift(130) #Lifts box height of one box
            else: #If target is a high rise
                myRobot.scissorLift(135) #Slightly higher than actual high rise for clearance
                myRobot.release()
                myRobot.move(-myRobot.MAX_SPEED, 200)
                myRobot.scissorLift(0)
                #need to remove id from target ids after being placed (maybe)
                myRobot.resetVariables() #Start loop again to look for next box

def planB(myRobot):
    while True:
        if myRobot.isTargetBox:
            if not myRobot.hasTarget:
                myRobot.findBestPallet()
            elif not myRobot.reachedTarget:
                myRobot.goToBoxLong(myRobot.targetID)
            else:
                myRobot.grab()
        else: #If target is a high rise
            myRobot.goToHighRise()
            myRobot.release()
            myRobot.move(-myRobot.MAX_SPEED, 200)
            #need to remove id from target ids after being placed
            myRobot.resetVariables() #Start loop again to look for next box


def testEncoders(myRobot):
    my_motor_board = myRobot.motor_board

    total_speed0 = 0
    total_speed1 = 0
    count = 0
    for i in range(5000):
        my_motor_board.motors[0].power = 0.5
        my_motor_board.motors[1].power = 0.96482070964 * 0.5
        speed0 = float(myRobot.arduino.command("m"))
        speed1 = float(myRobot.arduino.command("x"))
        total_speed0 += speed0
        total_speed1 += speed1
        count += 1

    print("Average speed Motor 0:", total_speed0/count)
    print("Average speed Motor 1:", total_speed1/count)


#testEncoders(robot)
#test(robot)