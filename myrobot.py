import math
from sr.robot3 import *


class MyRobot(Robot):
    def __init__(self):
        super().__init__()

        self.SPEED = 0.2
        self.DIAMETER = 90  # Diameter of wheel
        self.WIDTH = 397  # Length of robot from wheel to wheel
        self.MOTOR1 = "SR0REB"  # For wheels
        self.MOTOR2 = ""  # For scissor lift

        # Variables

        self.leftMotor = self.motor_boards[self.MOTOR1].motors[0]
        self.rightMotor = self.motor_boards[self.MOTOR1].motors[1]

        localMarkerIDs = [[i for i in range(100, 120)],
                          [i for i in range(120, 140)],
                          [i for i in range(140, 160)],
                          [i for i in range(160, 180)]]
        self.palletIDs = localMarkerIDs[self.zone]
        self.outerHighriseIDs = [i for i in range(195, 198)]
        self.innerHighriseID = [199]

        # self.targetInfos = [] #All faces of id marker
        self.targetFace = []  # Specific face of certain marker
        self.targetRoll = None  # Will be -90, 0, 90 or 180 degrees

        # Booleans
        self.hasTarget = False
        self.isTargetBox = True  # start by looking for box
        self.targetFound = False
        self.targetLost = False  # When looking for target after certain time/turning 360 degrees
        # Exit loop and switch targetLost to true to go back to
        # Main code and find new target
        self.faceFound = False
        self.reachedTarget = False
        self.linedUp = False
        self.isTurning = False
        self.isMoving = False
        self.scissorLiftUp = False
        self.grabbed = False

    def resetVariables(self):
        # Once box deposited, reset so that it restarts
        self.targetFace = []  # Specific face of certain marker
        self.targetRoll = None  # Will be -90, 0, 90 or 180 degrees

        # Booleans
        self.hasTarget = False
        self.isTargetBox = True  # start by looking for box
        self.targetFound = False
        self.targetLost = False
        self.faceFound = False
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

    def move(self, speed, distance=None):
        if distance == None:  # if no distance to move is provided move until stopped
            self.leftMotor.power = speed
            self.rightMotor.power = speed
            self.isMoving = True
        else:
            distanceMoved = 0
            startLeftPos = float(self.arduino.command("n"))  # arbitrary value to move left wheel motor
            startRightPos = float(self.arduino.command("y"))  # arbitrary value to move right wheel motor
            while distanceMoved <= distance:
                currentLeftPos = float(self.arduino.command("n"))
                currentRightPos = float(self.arduino.command("y"))
                leftDiff = abs(startLeftPos - currentLeftPos)
                rightDiff = abs(startRightPos - currentRightPos)
                leftDiff = rightDiff  # Needs to be deleted when right encoder works
                avgDiff = (leftDiff + rightDiff) / 2
                distanceMoved = avgDiff * self.DIAMETER * math.pi
                distanceMoved = round(distanceMoved, -2)
                self.leftMotor.power = speed
                self.rightMotor.power = speed
            self.stop()

    def turn(self, speed=0.2, angle=None):
        # When speed positive robot turns clockwise
        if angle == None:
            self.leftMotor.power = speed
            self.rightMotor.power = -speed
            self.isTurning = True

        else:
            angleToTurn = angle * self.WIDTH / self.DIAMETER
            angleTurned = 0
            startLeftPos = float(self.arduino.command("n"))
            startRightPos = float(self.arduino.command("y"))
            while angleTurned <= angleToTurn:
                currentLeftPos = float(self.arduino.command("n"))
                currentRightPos = float(self.arduino.command("y"))
                leftDiff = abs(startLeftPos - currentLeftPos)
                rightDiff = abs(startRightPos - currentRightPos)
                leftDiff = rightDiff  # Needs to be deleted when right encoder works
                avgDiff = (leftDiff + rightDiff) / 2
                angleTurned = (avgDiff * 2 * math.pi)
                self.leftMotor.power = speed
                self.rightMotor.power = -speed
            self.stop()

    def look(self, targetIDs=None):
        targetInfos = []  # Multiple faces of same target stored here
        # markers = None
        markers = self.camera.see()
        self.targetFound = False
        if markers != None:
            if targetIDs == None:  # If no target but just want to
                return markers  # see if any markers visible
            for mark in markers:
                if mark.id in targetIDs:
                    targetInfos.append(mark)
                    self.targetFound = True
        if targetInfos != []:
            return targetInfos
        return None

    def findFace(self, targetId, targetRoll):
        # To check if correct face side is seen (using roll)
        targetId = [targetId]
        targetInfos = self.look(targetId)
        self.faceFound = False
        for marker in targetInfos:
            accRoll = self.roundRollDeg(marker.orientation.roll)
            if accRoll == targetRoll:
                self.faceFound = True
                return marker  # Only one marker returned
        return None

    def roundRollDeg(self, roll):  # Check which orientation side is
        # Side either -180, 90, 0, 90, 180 degrees
        rollDeg = math.degrees(roll)
        rollDeg = int(90 * round(float(rollDeg) / 90))
        if rollDeg == -180:
            rollDeg = 180
        return rollDeg

    def getRoll(self, marker):
        return self.roundRollDeg(marker.orientation.roll)

    def getYawRad(self, markerInfo):
        # Pitch/yaw switch when box rotated 90 degrees so use roll to calculate actual yaw
        roll_cache = self.roundRollDeg(markerInfo.orientation.roll)
        if roll_cache < 0 or roll_cache == 180:
            is_roll_negative = -1
        else:  # If yaw/pitch are switched
            is_roll_negative = 1
        if roll_cache == 0 or roll_cache == 180:  # use yaw if "right" way up
            return is_roll_negative * markerInfo.orientation.yaw
        else:  # use pitch if box is on its "side"
            return is_roll_negative * markerInfo.orientation.pitch

    def chooseBestFace(self, markers):
        # based on which side closest to being square on
        bestSide = markers[0]
        for mark in markers:
            if self.getYawRad(bestSide) > self.getYawRad(mark):
                bestSide = mark
        # unfinished
        return bestSide

    def chooseBestMarker(self, markers):
        bestMarker = markers[0]
        for marker in markers:
            if bestMarker.position.distance > marker.position.distance:
                bestMarker = marker
        return bestMarker

    def lineUp(self, targetID, targetRoll):
        # Lines up on specific face, continuous loop until lined up or marker goes out of vision
        self.linedUp = False
        while not self.linedUp:
            markerInfo = self.findFace(targetID, targetRoll)
            if markerInfo != None:
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
                self.linedUp = False
                return None

    def findBestMarker(self):
        # Finds next marker to go towards (either box or high rise)
        if self.isTargetBox:  # To choose whether target box or high rise
            targetIDs = self.palletIDs
        else:
            targetIDs = self.outerHighriseIDs
        while self.targetFace == []:
            markers = self.look(targetIDs)
            if markers == None:
                self.turn(self.SPEED)  # NEED WAY TO EXIT IF NO MARKER FOUND
            else:
                self.stop()
                self.targetFace = self.chooseBestMarker(markers)
                self.hasTarget = True
        # return self.targetFace

    def goToBoxLong(self, targetInfo):
        targetID = targetInfo.id
        targetRoll = self.getRoll(targetInfo)
        speed = 0.2
        targetReached = False
        self.linedUp = False
        while not targetReached:
            markerInfo = self.findFace(targetID, targetRoll)
            if markerInfo == None:  # If face not seen, turns on the spot
                self.turn(self.SPEED)  # NEEDS WAY TO EXIT LOOP AFTER TURNED 360 degrees and nothing seen
                # If box lost, set targetFace to [] again
            else:
                self.stop()
                if self.linedUp:
                    yaw = self.getYawRad(markerInfo)
                    if yaw < 0:
                        speed = -speed
                        yaw = abs(yaw)
                    distance = markerInfo.orientation.yaw
                    distanceAway = math.cos(yaw) * distance
                    distanceTowards = math.sin(yaw) * distance
                    self.turn(speed, yaw)
                    speed = abs(speed)  # To make sure robot goes forward/turns 90 degrees clockwise
                    self.move(speed, distanceAway)
                    self.turn(speed, math.pi / 2)
                    self.move(self.SPEED, distanceTowards)
                    targetReached = True
                else:
                    markerInfo = self.lineUp(targetID, targetRoll)

    def goToBoxShort(self, targetInfo):
        markerID = targetInfo.id
        roll = self.getRoll(targetInfo)
        targetReached = False
        while not targetReached:
            markerInfo = self.findFace(markerID, roll)
            if markerInfo == None:
                self.turn(self.SPEED)  # NEEDS WAY TO EXIT IF NOT FOUND
                # If box lost, set targetFace to [] again
                # markerInfo = self.lineUp(markerID)
            else:
                if self.linedUp:
                    distance = markerInfo.position.distance
                    self.move(0.2, distance - 25)
                    targetReached = True
                else:
                    markerInfo = self.lineUp(markerID, roll)

    def grab(self):
        return

    def release(self):
        return

    def scissorUp(self, height):
        return

    def scissorDown(self):
        return
