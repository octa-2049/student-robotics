from myrobot import MyRobot
import math

ARDUINO_SN = "75230313833351313131"

# Set this to the baud rate that the device communicates with
SERIAL_BAUD_RATE = 115200

robot = MyRobot()
    # ignored_arduinos=[ARDUINO_SN],
    #raw_ports=[(ARDUINO_SN, SERIAL_BAUD_RATE)]

def test(myRobot):
    markers = myRobot.look()
    while True:
        markers = myRobot.look()
        if markers != []:
            myRobot.stop()
            bestMarker = myRobot.chooseBestFace(markers)
            return myRobot.goToBoxShort(bestMarker)

        else:
            myRobot.turn(myRobot.SPEED)


def compCode(myRobot):  # Code for actual robot
    while True:
        if myRobot.targetFace == []:
            myRobot.findBestMarker()
        elif not myRobot.reachedTarget:
            myRobot.goToBoxShort(myRobot.targetFace)
        else:
            if myRobot.isTargetBox:
                myRobot.grab()
                myRobot.scissorUp(130)  # Lifts box height of one box
            else:  # If target is a high rise
                myRobot.scissorUp(135)  # Slightly higher than actual high rise for clearance
                myRobot.release()
                # need to remove id from target ids after being placed (maybe)
                myRobot.reset()  # Start loop again to look for next box


def extra():
    global ARDUINO_SN
    while True:
        robot.raw_serial_devices[ARDUINO_SN].write(b"0")
        robot.sleep(1)
        robot.raw_serial_devices[ARDUINO_SN].write(b"150")
        robot.sleep(1)

def testEncoders(robot):
    my_motor_board = robot.motor_board

    total_speed0 = 0
    total_speed1 = 0
    count = 0

    for i in range(5000):
        my_motor_board.motors[0].power = 1
        my_motor_board.motors[1].power = 1
        speed0 = float(robot.arduino.command("m"))
        speed1 = float(robot.arduino.command("x"))
        total_speed0 += speed0
        total_speed1 += speed1
        count += 1

    print("Average speed Motor 0:", total_speed0 / count)
    print("Average speed Motor 1:", total_speed1 / count)

def grab():
    angle = 0
    interval = 5
    grabbed = False
    while not grabbed:
        microswitchL = robot.arduino.pins[7].digital_read()
        microswitchR = robot.arduino.pins[8].digital_read()
        if microswitchL and microswitchR:
            grabbed = True
        bytes_angle = str(angle).encode()
        robot.arduino[ARDUINO_SN].command("s")
        robot.raw_serial_devices[ARDUINO_SN].write(bytes_angle)
        robot.arduino[ARDUINO_SN].command("t")
        angle += interval


def release():
    robot.arduino[ARDUINO_SN].command("s")
    robot.raw_serial_devices[ARDUINO_SN].write(b"0")
    robot.arduino[ARDUINO_SN].command("t")


def back_and_forth():
    while True:
        robot.arduino.command("s")
        robot.raw_serial_devices[ARDUINO_SN].write(b"0")
        robot.arduino.command("t")
        robot.sleep(1)
        robot.arduino.command("s")
        robot.raw_serial_devices[ARDUINO_SN].write(b"150")
        robot.arduino.command("t")
        robot.sleep(1)


test(robot)

