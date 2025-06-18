from sr.robot3 import *
import math

robot = Robot()

my_motor_board = robot.motor_board
DIAMETER = 90
CIRC = DIAMETER * math.pi
WIDTH = 397

def forward(distance, speed, p0, p1):
    # Checks if robot has moved a specific distance
    if p1 * CIRC <= distance:
        print(p1 * CIRC)
        my_motor_board.motors[0].power = speed
        #robot.sleep(0.001)
        my_motor_board.motors[1].power = speed
    else:
        stop()
        return True

def rotate(angle, speed, p0, p1):
    # Checks if robot has turned a specific angle
    if (2 * p1 * CIRC) / WIDTH <= angle:
        my_motor_board.motors[0].power = speed
        #robot.sleep(0.001)
        my_motor_board.motors[1].power = -speed
    else:
        stop()
        return True

def stop():
    my_motor_board.motors[0].power = 0
    my_motor_board.motors[1].power = 0

step = 0
# Each step of making the triangle
no_triangle = 0
# Number of triangles formed

previous_position0 = 0
previous_position1 = 0

ended = False
while no_triangle < 3:
    speed0 = robot.arduino.command("m")
    position0 = robot.arduino.command("n")
    # Speed and position of motor 0
    speed1 = robot.arduino.command("x")
    position1 = robot.arduino.command("y")
    # Speed and position of motor 1
    position0 = float(position0)
    position1 = float(position1)

    # Calculate relative positions
    relative_position0 = position0 - previous_position0
    relative_position1 = position1 - previous_position1
    print("Position 0:", relative_position0, "Speed0:", speed0, "Position1:", relative_position1, "Speed1:", speed1)

    if step == 0:
        ended = forward(1500, 0.5, relative_position0, relative_position1)
        if ended:
            step += 1
            # Reset encoder reference points
            previous_position0 = position0
            previous_position1 = position1
            robot.sleep(1)
    elif step == 1:
        ended = rotate(1.13, 0.5, relative_position0, -relative_position1)
        if ended:
            step += 1
            previous_position0 = position0
            previous_position1 = position1
            robot.sleep(1)
    elif step == 2:
        ended = forward(2121, 0.5, relative_position0, relative_position1)
        if ended:
            step += 1
            previous_position0 = position0
            previous_position1 = position1
            robot.sleep(1)
    elif step == 3:
        ended = rotate(1.13, 0.5, relative_position0, -relative_position1)
        if ended:
            step += 1
            previous_position0 = position0
            previous_position1 = position1
            robot.sleep(1)
    elif step == 4:
        ended = forward(1500, 0.5, relative_position0, relative_position1)
        if ended:
            step += 1
            previous_position0 = position0
            previous_position1 = position1
            robot.sleep(1)
    elif step == 5:
        ended = rotate(0.09, 0.5, relative_position0, -relative_position1)
        if ended:
            step = 0
            no_triangle += 1
            previous_position0 = position0
            previous_position1 = position1
            robot.sleep(1)





