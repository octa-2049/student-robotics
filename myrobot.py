import math
from sr.robot3 import *

class MyRobot(Robot):
    def __init__(self):
        super().__init__()

        self.SPEED = 0.2
        self.DIAMETER = 90
        self.WIDTH = 397
        self.MOTOR1 = "MOT"#"SR0REB"

        #Variables
        self.leftMotor = self.motor_boards[self.MOTOR1].motors[0]
        self.rightMotor = self.motor_boards[self.MOTOR1].motors[1]

        localMarkerIDs = [[i for i in range(100, 120)],
                          [i for i in range(120, 140)],
                          [i for i in range(140, 160)],
                          [i for i in range(160, 180)]]
        self.palletIDs = localMarkerIDs[self.zone]
        self.outerHighriseIDs = [i for i in range(195, 198)]
        self.innerHighriseID = [199]

        #Booleans
        self.isTargetBox = True #start by looking for box
        self.targetFound = False
        self.reachedTarget = False
        self.linedUp = False
        self.isTurning = False
        self.isMoving = False
        self.scissorLiftUp = False
        self.grabbed = False


    def stop(self):
        self.leftMotor.power = 0
        self.rightMotor.power = 0
        self.isMoving = False
        self.isTurning = False

    def move(self, speed, distance = None):
        if distance == None:
            self.leftMotor.power = speed
            self.rightMotor.power = speed
            self.isMoving = True
        else:
            distanceMoved = 0
            startLeftPos = float(self.arduino.command("n"))
            startRightPos = float(self.arduino.command("y"))
            while distanceMoved <= distance:
                currentLeftPos = float(self.arduino.command("n"))
                currentRightPos = float(self.arduino.command("y"))
                leftDiff = abs(startLeftPos - currentLeftPos)
                rightDiff = abs(startLeftPos - currentRightPos)
                leftDiff = rightDiff  # Needs to be deleted when right encoder works
                avgDiff = (leftDiff + rightDiff) / 2
                distanceMoved = avgDiff * self.DIAMETER * math.pi
                distanceMoved = round(distanceMoved, -2)
                self.leftMotor.power = speed
                self.rightMotor.power = speed
            self.stop()

    def turn(self, speed: float, angle = None):
        if angle == None:
            self.leftMotor.power = speed
            self.rightMotor.power = -speed
            self.isTurning = True

        else:
            angleToTurn = angle * self.WIDTH / self.DIAMETER
            angleTurned = 0
            startLeftPos = float(self.arduino.command("n"))
            startRightPos = float(self.arduino.command("y"))
            while angleTurned <= angle:
                currentLeftPos = float(self.arduino.command("n"))
                currentRightPos = float(self.arduino.command("y"))
                leftDiff = abs(startLeftPos - currentLeftPos)
                rightDiff = abs(startLeftPos - currentRightPos)
                leftDiff = rightDiff  # Needs to be deleted when right encoder works
                avgDiff = (leftDiff + rightDiff) / 2
                currentAngle = (avgDiff * 2 * math.pi)
                self.leftMotor.power = speed
                self.rightMotor.power = -speed
            self.stop()

    def look(self, targetIDs = None, targetRoll = None):
        targetInfos = [] #Multiple faces of same target stored here
        markers = None
        markers = self.camera.see()
        self.targetFound = False
        if markers != None:
            if targetIDs == None: #If no target but just want to
                return markers    #see if any markers visible
            for mark in markers:
                if mark.id in targetIDs:
                    targetInfos.append(mark)
                    self.targetFound = True

    def findFace(self, targetId, targetRoll):
        #To check if correct face side is seen (using roll)
        targetInfos = self.look(targetId)
        for marker in targetInfos:
            accRoll = self.roundRollDeg(marker.orientation.roll)
            if accRoll == targetRoll:
                return marker

    def roundRollDeg(self, roll): #Check which orientation side is
        #Side either -180, 90, 0, 90, 180 degrees
        rollDeg = math.degrees(roll)
        rollDeg = int(90 * round(float(roll) / 90))
        if rollDeg == -180:
            rollDeg = 180
        return rollDeg

    def getYawRad(self, markerInfo):
        #Pitch/yaw switch when box rotated 90 degrees so use roll to calculate actual yaw
        roll_cache = self.roundRollDeg(markerInfo.orientation.roll)
        if roll_cache < 0 or roll_cache == 180:
            is_roll_negative = -1
        else: #If yaw/pitch are switched
            is_roll_negative = 1
        if roll_cache == 0 or roll_cache == 180: #use yaw if "right" way up
            return is_roll_negative * markerInfo.orientation.yaw
        else: #use pitch if box is on its "side"
            return is_roll_negative * markerInfo.orientation.pitch

    def chooseBestSide(self, markers):
        #based on which side closest to being square on
        bestSide = markers[0]
        for mark in markers:
            if self.getYawRad(bestSide) > self.getYawRad(mark):
                bestSide = mark

        return bestSide

    def lineUp(self, targetID):
        while not self.linedUp:
            markerInfo = self.look(targetID)
            if self.targetFound:
                angleOut = markerInfo.position.horizontal_angle
                if -0.05 < angleOut < 0.05:
                    self.linedUp = True
                    self.stop()
                    return markerInfo
                else:
                    if angleOut < 0:
                        self.turn(-self.SPEED, abs(angleOut))
                    else:
                        self.turn(self.SPEED, angleOut)
            else:
                self.turn(0.2)
                self.look(targetID)

    def roundRollDeg(self, roll):
        rollDeg = math.degrees(roll)
        rollDeg = int(90 * round(float(roll) / 90))
        if rollDeg == -180:
            rollDeg = 180
        return rollDeg

    def getYawRad(self, markerInfo):
        roll_cache = self.roundRollDeg(markerInfo.orientation.roll)
        if roll_cache < 0 or roll_cache == 180:
            is_roll_negative = -1
        else:
            is_roll_negative = 1
        if roll_cache == 0 or roll_cache == 180: # or roll_cache == -180:
            return is_roll_negative * markerInfo.orientation.yaw
        else:
            return is_roll_negative * markerInfo.orientation.pitch

    def goToBoxLong(self, targetID):
        speed = 0.2
        targetReached = False
        markerInfo = None
        while not targetReached:
            if markerInfo == None:
                markerInfo = self.lineUp(targetID)
            else:
                yaw = self.getYawRad(markerInfo)
                if yaw < 0:
                    speed = -speed
                    yaw = abs(yaw)
                distance = markerInfo.orientation.yaw
                distanceAway = math.cos(yaw) * distance
                distanceTowards = math.sin(yaw) * distance
                self.turn(speed, yaw)
                self.move(speed, distanceAway)
                self.turn(speed, math.pi/2)
                self.move(self.SPEED, distanceTowards)
                targetReached = True

    def goToBoxShort(self, markerID):

        targetReached = False
        markerInfo = None
        while not targetReached:
            if markerInfo == None:
                markerInfo = self.lineUp(markerID)
            else:
                distance = markerInfo.position.distance
                self.move(0.2, distance-25)
                targetReached = True


    def moveGrabber(self, grab: bool):



        return


    def scissorUp(self, height):


        return

    def scissorDown(self):
        return
