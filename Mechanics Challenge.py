from sr.robot3 import *

robot = Robot()

def scissorLift(height, lift_speed_down, lift_speed_up):
    target_height = float(height)
    current_height = 0.00
    print("Not in loop")
    print(current_height != target_height)
    print(current_height)
    print(target_height)
    tolerance = 0.01
    multiplier = 2140 #to be confirmed
    while current_height != target_height:
        print("in loop")
        motor2position = robot.arduino.command("b")
        motor3position = robot.arduino.command("c")
        print(motor2position, motor3position)
        average_position = (float(abs(motor2position)) + float(abs(motor3position))) / 2
        current_height = abs(float(motor2position))
        print("Current height is: ", current_height)
        if current_height > target_height:
            robot.motor_boards["SR0TDC"].motors[0].power = lift_speed_down
            robot.motor_boards["SR0TDC"].motors[1].power = lift_speed_down
        else:
            robot.motor_boards["SR0TDC"].motors[0].power = lift_speed_up
            robot.motor_boards["SR0TDC"].motors[1].power = lift_speed_up
    robot.motor_boards["SR0TDC"].motors[0].power = 0
    robot.motor_boards["SR0TDC"].motors[1].power = 0

while True:
    scissorLift(0.1, 0.3, -0.85)
