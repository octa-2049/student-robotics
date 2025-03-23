import math
from sr.robot3 import *


class MyRobot(Robot):
    def __init__(self):
        super().__init__()

        self.PAUSE = 0.5 #Tme in seconds for sleep time
        self.SPEED = 0.5
        self.ANGLE_OUT = 0.3
        self.SPEED_MULTIPLIER = 0.96482070964
        self.DIAMETER = 90  # Diameter of wheel
        self.WIDTH = 397  # Length of robot from wheel to wheel
        self.MOTOR1 = "SR0REB"  # For wheels
        self.MOTOR2 = "SR0TDC"  # For scissor lift

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
        self.targetID = None
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
        self.targetID = None
        self.targetFace = []  # Specific face of certain marker
        self.targetRoll = None  # Will be -90, 0, 90 or 180 degrees

        # Booleans
        self.hasTarget = False
        self.targetFound = False
        self.reachedTarget = False
        self.linedUp = False
        self.isTurning = False
        self.isMoving = False
        self.scissorLiftUp = False
        self.grabbed = False

    def stop(self):
        self.LEFT_MOTOR.power = 0
        self.RIGHT_MOTOR.power = 0
        self.isMoving = False
        self.isTurning = False

    def getMotorPositions(self): #returns right and left motor positions
        leftPos = float(self.arduino.command("n"))
        rightPos = float(self.arduino.command("y"))
        return leftPos, rightPos

    def getUltrasoundDistance(self):
        distance_mm = self.arduino.ultrasound_measure(self.US_TRIGGER, self.US_ECHO)
        return distance_mm

    def move(self, speed, distance=None):
        if distance == None:  # if no distance to move is provided move until stopped
            self.LEFT_MOTOR.power = speed
            self.RIGHT_MOTOR.power = speed * self.SPEED_MULTIPLIER
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
                self.LEFT_MOTOR.power = speed
                self.RIGHT_MOTOR.power = speed * self.SPEED_MULTIPLIER
            self.stop()

    def turn(self, speed=0.2, angle=None):
        # When speed positive robot turns clockwise
        if angle == None:
            self.LEFT_MOTOR.power = speed
            self.RIGHT_MOTOR.power = -speed * self.SPEED_MULTIPLIER
            self.isTurning = True

        else:
            angleToTurn = angle * self.WIDTH / self.DIAMETER
            #angleToTurn in arbitrary units 1 = 1 complete revolution of wheel
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
                self.LEFT_MOTOR.power = speed
                self.RIGHT_MOTOR.power = -speed * self.SPEED_MULTIPLIER
            self.stop()

    def look(self, targetIDs=None):
        #returns SINGLE MARKER NOT LIST
        self.sleep(self.PAUSE)
        self.stop()
        #print("Stopped")
        self.sleep(self.PAUSE)
        #print("Started")
        markers = self.camera.see()
        self.targetFound = False
        if markers != None:
            if targetIDs == None:  # If no target but just want to
                return markers  # see if any markers visible
            for mark in markers:
                if mark.id in targetIDs:
                    self.targetFound = True
                    return mark
        return [] #returns either [] or first marker seen

    def lookAll(self, targetIDs=None):
        #returns LIST
        self.sleep(self.PAUSE)
        self.stop()
        #print("Stopped")
        self.sleep(self.PAUSE)
        #print("Started")
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
                    #return mark
        return targetInfos #returns either [] or all markers seen

    def findFace(self, targetId, targetRoll):
        # To check if correct face side is seen (using roll)
        targetId = [targetId]
        targetInfos = self.lookAll(targetId)
        self.faceFound = False
        if targetInfos != []:
            for marker in targetInfos:
                accRoll = self.roundRollDeg(marker.orientation.roll)
                if accRoll == targetRoll:
                    self.faceFound = True
                    return marker  # Only one marker returned
        return []

    def printMarkerInfo(self, marker):
        # Id, size
        print("Id: ", marker.id)
        print("Size: ", marker.size)

        # Pixel centre, pixel_corners (
        print("Pixel centre: ", marker.pixel_centre.x, marker.pixel_centre.y)
        print("Pixel corners: ", marker.pixel_corners)

        # (Position.) Distance, horiztontal_angle, vertical_angle
        print("Distance: ", marker.position.distance)
        print("Horiz angle: ", marker.position.horizontal_angle)
        print("Vert angle:  ", marker.position.vertical_angle)

        # (Orientation) yaw, pitch, roll
        print("Yaw: ", marker.orientation.yaw)
        print("Pitch: ", marker.orientation.pitch)
        print("Roll ", marker.orientation.roll)
        print("Actual yaw: " + str(self.getYawRad(marker)))

    def triangulate(self):
        #Find position relative to centre

        return

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
        self.targetID = bestMarker.id
        self.targetFace = bestMarker
        return bestMarker

    def lineUp(self, targetID):
        # Lines up on specific face,if marker goes out of vision breaks loop
        self.linedUp = False
        while not self.linedUp:
            markerInfo = self.look(targetID)
            if markerInfo != []:
                angleOut = markerInfo.position.horizontal_angle
                if abs(angleOut) < self.ANGLE_OUT:
                    self.linedUp = True
                    self.stop()
                else:
                    if angleOut < 0:
                        self.turn(-self.MAX_SPEED, abs(angleOut / 4))
                    else:
                        self.turn(self.MAX_SPEED, angleOut / 4)
            else:
                self.linedUp = False
                return None

    def lineUpWithoutEncoders(self, targetID):
        print("lining up without encoders")
        self.linedUp = False
        while not self.linedUp:
            markerInfo = self.look(targetID)
            if markerInfo != []:
                angleOut = markerInfo.position.horizontal_angle
                if abs(angleOut) < self.ANGLE_OUT:
                    print("lined up")
                    self.linedUp = True
                    self.stop()
                elif angleOut < 0:
                    self.turn(-self.MAX_SPEED)
                else:
                    self.turn(self.MAX_SPEED)
            else:
                self.linedUp = False
                return None

    def findBestMarker(self):
        timesTurned = 0 #Times turned in a row
        # Finds next marker to go towards (either box or high rise)
        if self.isTargetBox:  # To choose whether target box or high rise
            targetIDs = self.palletIDs
        else:
            targetIDs = self.outerHighriseIDs
        while not self.hasTarget:
            markers = self.look(targetIDs)
            if markers == []:
                # WAY TO EXIT IF NO MARKER FOUND:
                if timesTurned > self.TURN_FRACTION:
                    self.randomMovement()
                    timesTurned = 0
                self.turn(self.MAX_SPEED, self.angleTurn)
                timesTurned += 1
            else:
                self.stop()
                self.targetFace = self.chooseBestMarker(markers)
                self.hasTarget = True

    def goToBoxLong(self, targetInfo):
        targetID = targetInfo.id
        #targetRoll = self.getRoll(targetInfo)
        speed = 0.2
        targetReached = False
        self.linedUp = False
        timesTurned = 0 #Times turned in a row without seeing a box
        #If this exceeds self.fractionTurned then we have turned full
        #360 degrees without finding a box and need to perform evasive manoeuvres
        #If box still not found then assumes box is lost and break loop
        randomMovementDone = False
        while not targetReached:
            markerInfo = self.look([targetID])
            if not self.targetFound:  # If face not seen, turns on the spot
                if timesTurned > self.TURN_FRACTION:
                    if randomMovementDone:
                        self.resetVariables() # If box lost, reset variables
                        return None
                    self.randomMovement()
                    randomMovementDone = True
                    timesTurned = 0
                self.turn(self.MAX_SPEED, self.ANGLE_TURN)  # NEEDS WAY TO EXIT LOOP AFTER TURNED 360 degrees and nothing seen
                timesTurned += 1
            else:
                self.stop()
                if self.linedUp:
                    yaw = self.getYawRad(markerInfo)
                    if yaw > 0:
                        speed = -speed
                    yaw = abs(yaw)
                    distance = markerInfo.position.distance
                    distanceAway = math.cos(yaw) * distance
                    self.turn(speed, yaw)
                    speed = abs(speed)  # To make sure robot goes forward/turns 90 degrees clockwise
                    self.move(speed, distanceAway)
                    self.turn(-speed, math.pi / 2)
                    self.goToBoxShort(targetInfo)
                    targetReached = True
                else:
                    self.lineUp(targetID)

    def goToBoxShort(self, targetInfo):
        markerID = targetInfo.id
        print("Looking for " + str(markerID))
        roll = self.getRoll(targetInfo)
        targetReached = False
        while not targetReached:
            #markerInfo = self.findFace(markerID, roll)
            markerInfo = self.look([markerID])
            if markerInfo == []:
                print("no marker found")
                self.turn(self.SPEED, math.pi /40)  # NEEDS WAY TO EXIT IF NOT FOUND
                # If box lost, set targetFace to [] again
                # markerInfo = self.lineUp(markerID)
            else:
                #markerInfo = markerInfo[0]
                angleOut = markerInfo.position.horizontal_angle
                print("Found marker")
                if abs(angleOut) < self.ANGLE_OUT:
                    print("Moving straight")
                    distance = markerInfo.position.distance
                    self.move(self.SPEED)#, distance - 25)
                    self.sleep(0.5)
                    if distance < 400:
                        #NEED TO IMPLEMENT ULTRASOUND
                        self.stop()
                        print("Box reached")
                        targetReached = True
                elif angleOut < 0:
                    self.turn(-1 * self.SPEED, abs(angleOut/4))
                else:
                    self.turn(self.SPEED, abs(angleOut/4))

                    #markerInfo = self.lineUp(markerID, roll)

    def goToBoxWithoutEncoders(self, targetInfo):
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
                angleOut = markerInfo.position.horizontal_angle
                print("Found marker")
                if abs(angleOut) < 0.02:
                    print("linedUp")
                    distance = markerInfo.position.distance
                    if distance < 300:
                        targetReached = True
                        self.stop()
                    else:
                        self.move(0.2)
                elif angleOut < 0:
                        self.turn(-self.SPEED)
                else:
                    self.turn(self.SPEED)
                    #markerInfo = self.lineUpWithoutEncoders(markerID, roll)

    def grab(self):
        angle = -1
        interval = 0.05
        grabbed = False
        while not grabbed:
            print(angle)
            microswitchL = self.arduino.pins[10].digital_read()
            microswitchR = self.arduino.pins[11].digital_read()
            if angle > 1:
                print("no box grabbed")
                #self.kch.leds[LED_A].colour = Colour.RED
                break
            if not microswitchL and not microswitchR:
                #self.kch.leds[LED_A].colour = Colour.GREEN
                grabbed = True
            self.servo_board.servos[0].position = angle
            angle += interval
            self.sleep(0.25)

    def release(self): #doesn't work
        self.servo_board.servos[0].position = -1

    def scissorLift(self, height, lift_speed = 0.1):
        target_height = height
        current_height = 0
        multiplier = 300  # to be confirmed
        while current_height != target_height:
            motor2position = self.arduino.command("b")
            motor3position = self.arduino.command("c")
            average_position = (motor2position * motor3position) / 2
            current_height = average_position * multiplier
            if current_height > target_height:
                self.motor_boards["SR0TDC"].motors[0].power = -lift_speed
                self.motor_boards["SR0TDC"].motors[1].power = -lift_speed
            else:
                self.motor_boards["SR0TDC"].motors[0].power = lift_speed
                self.motor_boards["SR0TDC"].motors[1].power = lift_speed
        self.motor_boards["SR0TDC"].motors[0].power = 0
        self.motor_boards["SR0TDC"].motors[1].power = 0
