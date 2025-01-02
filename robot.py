from sr.robot3 import *

robot = Robot()

zone = robot.zone

motor_board = robot.motor_board
servo_board = robot.servo_board
vacuum = robot.power_board.outputs[OUT_H0]

map = {
    "boundary_0": [i for i in range(0,7)],
    "boundary_90": [i for i in range(7, 14)],
    "boundary_180": [i for i in range(14, 21)],
    "boundary_270": [i for i in range(21, 28)],
    "boundary": [i for i in range(0, 28)],
    "zone_0": [i for i in range(100, 120)],
    "zone_1": [i for i in range(120, 140)],
    "zone_2": [i for i in range(140, 160)],
    "zone_3": [i for i in range(160,180)],
    "highrise_center": [199],
    "highrise": [i for i in range(195, 200)],
    "highrise_0": [195]
       }

current_target_outer = f"highrise_{zone}"
current_target = f"highrise_{zone}"
current_target_roll = None
current_state = ["searching"]

def sort_distance(e):
    return e["distance"]

def line_up(mode):
    if mode == "normal":
        pass
    elif mode == "fine":
        pass

while True:
    target_marker_info = []
    all_markers = robot.camera.see()
    for m in all_markers:
        if type(current_target) == int:
            if m.id == current_target:
                target_marker_info = m
        else:
            if m.id in map[current_target]:
                target_marker_info.append({"id": m.id, "distance": m.position.distance, "roll": m.orientation.roll})
                print(m, target_marker_info)

    if target_marker_info == [] and current_state[-1] != "lifting":
        current_state.append("searching")
        current_target = current_target_outer

    if current_state[-1] == "searching":
        robot.motor_board.motors[0].power = -0.05
        robot.motor_board.motors[1].power = 0.05

        if target_marker_info != []:
            if type(current_target) == int:
                pass
            else:
                robot.sleep(0.1)
                robot.motor_board.motors[0].power = BRAKE
                robot.motor_board.motors[1].power = BRAKE
                target_marker_info.sort(key=sort_distance)
                current_target = target_marker_info[0]["id"]
                current_target_roll = target_marker_info[0]["roll"]
                current_state.append("lining_up")
    elif current_state[-1] == "lining_up":
        if target_marker_info.position.horizontal_angle < -0.05:
            # move left
            robot.motor_board.motors[0].power = -0.1
            robot.motor_board.motors[1].power = 0.1
        elif target_marker_info.position.horizontal_angle > 0.05:
            # move right
            robot.motor_board.motors[0].power = 0.1
            robot.motor_board.motors[1].power = -0.1
        else:
            robot.motor_board.motors[0].power = BRAKE
            robot.motor_board.motors[1].power = BRAKE
            current_state.append("driving")
        print("lining up", m, m.orientation)
    elif current_state[-1] == "driving":
        if target_marker_info.position.distance < 500:
            robot.motor_board.motors[0].power = 0.05
            robot.motor_board.motors[1].power = 0.05
            current_state.append("lifting")
            # fine-lining first?
        else:
            if target_marker_info.position.horizontal_angle < -0.1:
                # move left
                robot.motor_board.motors[0].power = -0.1
                robot.motor_board.motors[1].power = 0.1
            elif target_marker_info.position.horizontal_angle > 0.1:
                # move right
                robot.motor_board.motors[0].power = 0.1
                robot.motor_board.motors[1].power = -0.1
            else:
                robot.motor_board.motors[0].power = 0.1
                robot.motor_board.motors[1].power = 0.1
    elif current_state[-1] == "lifting":
        print("lifting", m, m.orientation)
        distance_mm = robot.arduino.ultrasound_measure(2, 3)
        if distance_mm < 80:
            robot.motor_board.motors[0].power = BRAKE
            robot.motor_board.motors[1].power = BRAKE
            if "zone" in current_target_outer:
                vacuum.is_enabled = True
                servo_board.servos[0].position = -1
                robot.sleep(3)
                servo_board.servos[0].position = 1
                current_state.append("searching")
                current_target_outer = "highrise_center"
                current_target = "highrise_center"
            elif "highrise" in current_target_outer:
                servo_board.servos[0].position = 0.7
                vacuum.is_enabled = False
                robot.sleep(1)
                servo_board.servos[0].position = 1
                current_state.append("searching")
                current_target_outer = "zone_0"
                current_target = "zone_0"

# notes: slow down after depositing two boxes as cannot see
# implement counter to avoid restacking same boxes + height detection?
# count how many have been stacked on each high rise
# add stacked boxes to a list so they aren't stacked again

# NOTE: robot differentiates ids by YAW
# test with outer highrise