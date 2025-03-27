import math
from sr.robot3 import *


class MyRobot(Robot):
    def __init__(self):
        super().__init__()

        self.PAUSE = 0.4  # Tme in seconds for sleep time
        self.MAX_SPEED = 0.22
        self.ANGLE_OUT = 0.15
        self.TURN_FRACTION = 20
        self.ANGLE_TURN = math.pi / self.TURN_FRACTION
        self.VALID_YAW = math.pi / 4  # How much angle we allow before not considering face
        self.SPEED_MULTIPLIER = 0.96482070964
        self.DIAMETER = 90  # Diameter of wheel
        self.WIDTH = 397  # Length of robot from wheel to wheel
        self.MOTOR1 = "SR0REB"  # For wheels
        self.LEFT_MOTOR = self.motor_boards[self.MOTOR1].motors[0]
        self.RIGHT_MOTOR = self.motor_boards[self.MOTOR1].motors[1]
        # self.MOTOR2 = "SR0TDC"  # For scissor lift
        # self.SCISSOR = self.motor_boards[self.MOTOR2].motors[0].power
        self.US_TRIGGER = 12  # Trigger pin for ultrasound
        self.US_ECHO = 13  # Echo pin for ultrasound
        self.GRAB_SERVO = self.servo_board.servos[0]
        self.GRAB_SERVO.set_duty_limits(700, 1600)
        self.SWITCH_LEFT = self.arduino.pins[10]  # Left microswitch
        self.SWITCH_RIGHT = self.arduino.pins[11]  # Right microswitch

        # Variables
        localMarkerIDs = [[i for i in range(100, 120)],
                          [i for i in range(120, 140)],
                          [i for i in range(140, 160)],
                          [i for i in range(160, 180)]]
        self.palletIDs = localMarkerIDs[self.zone]
        self.outerHighriseIDs = [i for i in range(195, 198)]
        self.innerHighriseID = [199]
        self.arenaMarkers = [i for i in range(0, 28)]

        # self.targetInfos = [] #All faces of id marker
        self.targetID = None
        self.targetFace = []  # Specific face of certain marker
        self.targetRoll = None  # Will be -90, 0, 90 or 180 degrees

        # Booleans
        self.hasTarget = False
        self.isTargetBox = True  # start by looking for box
        self.targetFound = False
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
        self.targetFace = []
        self.targetRoll = None
        self.hasTarget = False
        self.targetFound = False
        self.reachedTarget = False
        self.linedUp = False
        self.isTurning = False
        self.isMoving = False
        self.scissorLiftUp = False
        self.grabbed = False

    def printMarkerInfo(self, marker):
        # ID, size
        print("Id: ", marker.id)
        print("Size: ", marker.size)

        # Pixel centre, pixel_corners (
        print("Pixel centre: ", marker.pixel_centre.x, marker.pixel_centre.y)
        print("Pixel corners: ", marker.pixel_corners)

        # (Position.) Distance, horizontal_angle, vertical_angle
        print("Distance: ", marker.position.distance)
        print("Hor angle: ", marker.position.horizontal_angle)
        print("Vert angle:  ", marker.position.vertical_angle)

        # (Orientation) yaw, pitch, roll
        print("Yaw: ", marker.orientation.yaw)
        print("Pitch: ", marker.orientation.pitch)
        print("Roll ", marker.orientation.roll)
        print("Actual yaw: " + str(self.getYawRad(marker)))

    def stop(self):
        self.LEFT_MOTOR.power = 0
        self.RIGHT_MOTOR.power = 0
        self.isMoving = False
        self.isTurning = False

    def getWheelPositions(self):  # returns right and left motor positions
        leftPos = float(self.arduino.command("n"))
        rightPos = float(self.arduino.command("y"))
        return leftPos, rightPos

    def getUltrasoundDistance(self):
        distance_mm = self.arduino.ultrasound_measure(self.US_TRIGGER, self.US_ECHO)
        return distance_mm

    def getCos(self, angle):
        return round(1 - ((angle ** 2) / 2) + ((angle ** 4) / 24), 2)

    def getRollDeg(self, marker):  # Check which orientation side is
        # Side either -180, 90, 0, 90, 180 degrees
        roll = marker.orientation.roll
        rollDeg = math.degrees(roll)
        rollDeg = int(90 * round(float(rollDeg) / 90))
        if rollDeg == -180:
            rollDeg = 180
        return rollDeg

    def getYawRad(self, markerInfo):
        # Pitch/yaw switch when box rotated 90 degrees so use roll to calculate actual yaw
        roll_cache = self.getRollDeg(markerInfo)
        if roll_cache < 0 or roll_cache == 180:
            is_roll_negative = -1
        else:  # If yaw/pitch are switched
            is_roll_negative = 1
        if roll_cache == 0 or roll_cache == 180:  # use yaw if "right" way up
            return is_roll_negative * markerInfo.orientation.yaw
        else:  # use pitch if box is on its "side"
            return is_roll_negative * markerInfo.orientation.pitch

    def isHoldingBox(self):  # NEED TO CHECK IF RIGHT WAY ROUND
        # When being pressed, variables are false
        microSwitchLeft = not self.SWITCH_LEFT.digital_read()
        microSwitchRight = not self.SWITCH_RIGHT.digital_read()
        return microSwitchLeft or microSwitchRight

    def isGoodFace(self, marker):
        return abs(self.getYawRad(marker)) < self.VALID_YAW

    def chooseBestFace(self, markers):
        # based on which side closest to being square on
        if len(markers) == 0:
            return []
        bestFace = markers[0]
        for mark in markers:
            if abs(self.getYawRad(bestFace)) > abs(self.getYawRad(mark)):
                bestFace = mark
        return bestFace

    def chooseBestMarker(self, markers):
        bestMarker = markers[0]
        for marker in markers:
            bestDistance = bestMarker.position.distance
            markerDistance = marker.position.distance
            if markerDistance < bestDistance:
                bestMarker = marker
        return bestMarker

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
                # leftDiff = rightDiff  # Needs to be deleted when right encoder works
                avgDiff = (leftDiff + rightDiff) / 2
                distanceMoved = avgDiff * self.DIAMETER * math.pi
                distanceMoved = round(distanceMoved, -2)
                self.LEFT_MOTOR.power = speed
                self.RIGHT_MOTOR.power = speed * self.SPEED_MULTIPLIER
            self.stop()

    def turn(self, speed, angle=None):
        # When speed positive robot turns ANTIclockwise
        if angle == None:
            self.LEFT_MOTOR.power = -speed
            self.RIGHT_MOTOR.power = speed * self.SPEED_MULTIPLIER
            self.isTurning = True

        else:
            angleToTurn = angle * self.WIDTH / self.DIAMETER
            # angleToTurn in arbitrary units 1 = 1 complete revolution of wheel
            angleTurned = 0
            startLeftPos = float(self.arduino.command("n"))
            startRightPos = float(self.arduino.command("y"))
            while angleTurned <= angleToTurn:
                currentLeftPos = float(self.arduino.command("n"))
                currentRightPos = float(self.arduino.command("y"))
                leftDiff = abs(startLeftPos - currentLeftPos)
                rightDiff = abs(startRightPos - currentRightPos)
                # leftDiff = rightDiff  # Needs to be deleted when right encoder works
                avgDiff = (leftDiff + rightDiff) / 2
                angleTurned = (avgDiff * 2 * math.pi)
                self.LEFT_MOTOR.power = speed
                self.RIGHT_MOTOR.power = -speed * self.SPEED_MULTIPLIER
            self.stop()

    def randomMovement1(self):  # Unfinished
        self.move(self.MAX_SPEED, 200)
        self.turn(self.MAX_SPEED, math.pi / 4)
        self.move(-self.MAX_SPEED, 200)

    def findOne(self, targetIDs=None):
        # returns SINGLE MARKER NOT LIST
        self.sleep(self.PAUSE)
        self.stop()
        # print("Stopped")
        self.sleep(self.PAUSE)
        # print("Started")
        markers = self.camera.see()
        targetInfos = []
        self.targetFound = False
        if markers != None:
            if targetIDs == None:  # If no target but just want to
                return markers  # see if any markers visible
            for mark in markers:
                if mark.id in targetIDs and self.isGoodFace(mark):
                    self.targetFound = True
                    targetInfos.append(mark)
                    # return mark
        singleFace = self.chooseBestFace(targetInfos)
        return singleFace  # returns either [] or first marker seen

    def findAll(self, targetIDs):
        # returns LIST
        self.sleep(self.PAUSE)
        self.stop()
        # print("Stopped")
        self.sleep(self.PAUSE)
        # print("Started")
        targetInfos = []  # Multiple faces of same target stored here
        markers = self.camera.see()
        self.targetFound = False
        if markers != None:
            for mark in markers:
                if mark.id in targetIDs and self.isGoodFace(mark):
                    targetInfos.append(mark)
                    self.targetFound = True
        return targetInfos  # returns either [] or all markers seen

    def findFace(self, targetId, targetRoll):  # DO NOT USE
        # To check if correct face side is seen (using roll)
        targetId = [targetId]
        targetInfos = self.findAll(targetId)
        self.faceFound = False
        if targetInfos != []:
            for marker in targetInfos:
                accRoll = self.roundRollDeg(marker.orientation.roll)
                if accRoll == targetRoll:
                    self.faceFound = True
                    return marker  # Only one marker returned
        return []

    def lineUp(self, targetID):
        # Lines up on specific face,if marker goes out of vision breaks loop
        self.linedUp = False
        while not self.linedUp:
            markerInfo = self.findOne([targetID])
            if markerInfo != []:
                angleOut = markerInfo.position.horizontal_angle
                if -self.ANGLE_OUT < angleOut < self.ANGLE_OUT:
                    self.linedUp = True
                    self.stop()
                else:
                    if angleOut < 0:  # MORE POSITIVE THAN NEGATIVE
                        self.turn(self.MAX_SPEED, -angleOut / 2)
                    else:
                        self.turn(-self.MAX_SPEED, angleOut / 2)
            else:
                self.linedUp = False
                return None

    def lineUpWithoutEncoders(self, targetID):
        print("lining up without encoders")
        self.linedUp = False
        while not self.linedUp:
            markerInfo = self.findOne([targetID])
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
        if self.isTargetBox:
            targetIDs = self.palletIDs
        else:
            targetIDs = self.outerHighriseIDs
        timesTurned = 0  # Times turned in a row

        while not self.hasTarget:
            markers = self.findAll(targetIDs)
            # NEEDS TO USE FIND ALL NOT FIND ONE OTHERWISE CANNOT CHOOSE WHICH
            # MARKER BEST ONE
            if markers == []:
                # DO SOMETHING IF NO MARKER FOUND:
                if timesTurned > self.TURN_FRACTION:
                    self.randomMovement1()
                    timesTurned = 0
                self.turn(self.MAX_SPEED, self.ANGLE_TURN)
                timesTurned += 1
            else:
                self.stop()
                self.targetFace = self.chooseBestMarker(markers)
                self.targetID = self.targetFace.id
                self.hasTarget = True

    def goToBoxStraight(self, markerID):
        print("Looking for " + str(markerID))
        targetReached = False
        timesTurned = 0
        while not targetReached:
            markerInfo = self.findOne([markerID])
            if not self.targetFound:
                if timesTurned > self.TURN_FRACTION:
                    self.resetVariables()
                    # If box lost, reset variables
                    return None
                print("no marker found")
                self.turn(self.MAX_SPEED, self.ANGLE_TURN)  # NEEDS WAY TO EXIT IF NOT FOUND
                timesTurned += 1
            else:
                timesTurned = 0
                print("Found marker")
                if self.linedUp:
                    print("Moving straight")
                    distance = markerInfo.position.distance
                    self.move(self.MAX_SPEED, distance / 2)
                    # May try to variate speed depending on distance to marker
                    self.sleep(0.5)
                    if distance < 600:  # NEEDS TO BE TESTED
                        self.move(self.MAX_SPEED, distance * 1.05)
                        self.reachedTarget = True
                        return None
                        # targetReached = self.goToMarkerUltrasound(50)
                else:
                    self.lineUp(markerID)

    def goToMarkerUltrasound(self, distanceAway):
        start = self.time()
        end = self.time()
        self.move(self.MAX_SPEED)
        while (start - end) < 5:
            distance = self.getUltrasoundDistance()
            if distance < distanceAway:
                self.stop()
                print("Marker reached")
                return True
        return False

    def goToBoxWithoutEncoders(self, markerID):
        targetReached = False
        start = self.time()
        while not targetReached:
            markerInfo = self.findOne(markerID)
            if markerInfo == None:
                self.turn(self.MAX_SPEED)  # NEEDS WAY TO EXIT IF NOT FOUND
                if (start - self.time()) > 10:  # NEED TO BE TESTED
                    self.resetVariables()
                    return None
            else:
                start = self.time()
                angleOut = markerInfo.position.horizontal_angle
                print("Found marker")
                if self.linedUp:
                    print("linedUp")
                    distance = markerInfo.position.distance
                    if distance < 300:
                        targetReached = True
                        self.stop()
                    else:
                        self.move(self.MAX_SPEED)
                else:
                    self.lineUpWithoutEncoders(markerID)

    def getSquareOn(self, targetID):
        # Allows for only ID
        speed = 0.2
        squareOn = False
        self.linedUp = False
        timesTurned = 0  # Times turned in a row without seeing a box
        # If this exceeds self.fractionTurned then we have turned full
        # If box still not found then assumes box is lost and break loop
        while not squareOn:
            markerInfo = self.findOne([targetID])
            if not self.targetFound:  # If face not seen, turns on the spot
                if timesTurned > self.TURN_FRACTION:
                    self.resetVariables()  # If box lost, reset variables
                    return None
                self.turn(self.MAX_SPEED,
                          self.ANGLE_TURN)  # NEEDS WAY TO EXIT LOOP AFTER TURNED 360 degrees and nothing seen
                timesTurned += 1
            else:
                self.stop()
                if self.linedUp:
                    yaw = self.getYawRad(markerInfo)
                    distance = markerInfo.position.distance
                    if distance > 1500:
                        self.move(self.MAX_SPEED, distance - 1500)
                    elif yaw > 0:
                        distanceAway = self.getCos(yaw) * distance
                        print(distanceAway, self.getCos(yaw), distance)
                        self.turn(self.MAX_SPEED, yaw)
                        self.move(self.MAX_SPEED, distanceAway)
                        self.turn(-self.MAX_SPEED, math.pi / 2)
                    else:  # If yaw negative
                        distanceAway = self.getCos(-yaw) * distance
                        print(distanceAway, self.getCos(-yaw), distance)
                        self.turn(-self.MAX_SPEED, -yaw)
                        self.move(self.MAX_SPEED, distanceAway)
                        self.turn(self.MAX_SPEED, math.pi / 2)
                    squareOn = True
                else:
                    self.lineUp(targetID)

    def goToBoxLong(self, targetID):
        self.getSquareOn(targetID)
        self.goToBoxStraight(targetID)

    def goToHighRise(self, markerID):
        print("Looking for " + str(markerID))
        targetReached = False
        timesTurned = 0
        while not targetReached:
            markerInfo = self.findOne([markerID])
            if not self.targetFound:
                if timesTurned > self.TURN_FRACTION:
                    self.randomMovement1()
                    timesTurned = 0
                print("no marker found")
                self.turn(self.MAX_SPEED, self.ANGLE_TURN)  # NEEDS WAY TO EXIT IF NOT FOUND
                timesTurned += 1
            else:
                timesTurned = 0
                print("Found marker")
                if self.linedUp:
                    print("Moving straight")
                    distance = markerInfo.position.distance
                    self.move(self.MAX_SPEED, distance / 4)
                    # May try to variate speed depending on distance to marker
                    self.sleep(0.5)
                    if distance < 800:  # NEEDS TO BE TESTED
                        self.move(self.MAX_SPEED, distance - 300)
                        self.reachedTarget = True
                        targetReached = True
                        # targetReached = self.goToMarkerUltrasound(140) #NEEDS TO BE TEST
                else:
                    self.lineUp(markerID)

    def grab(self):
        angle = -1
        interval = 0.05
        grabbed = False
        while not grabbed:
            print(angle)
            microSwitchLeft = self.SWITCH_LEFT.digital_read()
            microSwitchRight = self.SWITCH_RIGHT.digital_read()
            if angle >= 1:
                print("no box grabbed")
                self.grabbed = False
                self.reachedTarget = False
                self.release()
                self.resetVariables()
                break
            if not microSwitchLeft or not microSwitchRight:
                print("grabbing")
                self.grabbed = True
                grabbed = True
            self.GRAB_SERVO.position = angle
            angle += interval
            self.sleep(0.1)

    def release(self):
        self.GRAB_SERVO.position = -1

    def scissorLift(self, height, lift_speed=0.1):
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

