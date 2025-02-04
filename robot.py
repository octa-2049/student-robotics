import math
from unittest import case

from sr.robot3 import *
from enum import Enum

DEFAULT_SPEED = 0.5
DEFAULT_ROTATION = 0.1

def round_10(n: float) -> int:
    """
    Converts an angle in radians to degrees and rounds it to the nearest tenth.

    :param float n: The number to be rounded.

    :return: The rounded number.
    """
    return round(math.degrees(n) / 10) * 10

def round_90(n: float) -> int:
    """
    Converts an angle in radians to degrees and rounds it to the nearest 90 degrees.

    :param float n: The number to be rounded.

    :return: The rounded number.
    """
    return round(math.degrees(n)/10/1/9) * 90

class State(Enum):
    INITIAL = "initial"
    SEARCH_1 = "search_1"
    TRAVEL_1 = "travel_1"
    TRAVEL_2 = "travel_2"
    TRAVEL_2A = "travel_2a"
    TRAVEL_3 = "travel_3"
    TRAVEL_4 = "travel_4"
    PICKUP_1 = "pickup_1"
    DROP_1 = "drop_1"

class MarkerProperty(Enum):
    ID = "marker.id"
    ROLL = "marker.orientation.roll"
    DISTANCE = "marker.position.distance"

class MyRobot(Robot):
    def __init__(self) -> None:
        """Initialises the robot."""
        Robot.__init__(self)
        self.vacuum_enabled = self.power_board.outputs[OUT_H0]
        self.vacuum_enabled.is_enabled = False
        self.vacuum_position = self.servo_board.servos[0]
        self.markers = []
        self.filtered_markers = []
        self.filter_properties = []
        self.last_refresh = 0
        self.refresh_interval = 0.05
        self.left_motor = self.motor_board.motors[0]
        self.right_motor = self.motor_board.motors[1]

        self.default_speed = DEFAULT_SPEED
        self.wheel_radius = 0.05 # in meters

        self.front_ultrasound = 0
        self.front_left_microswitch = False
        self.front_right_microswitch = False

        self.arduino.pins[10].mode = OUTPUT
        self.arduino.pins[11].mode = OUTPUT

        self.pallet_in_possession = None

        self.target_id = None
        self.target_roll = None
        self.target_object = None

        self.perpendicular_distance = 0
        self.travel_distance = 0
        self.real_yaw = 0
        self.reverse = False

        self.own_pallets = f"pallets_{self.zone}"
        self.own_highrise = f"highrise_{self.zone}"
        self.target_zone = self.own_pallets

        self.status = State.INITIAL
        self.activity_start_time = 0

    def see(self, force_update: bool = False) -> bool:
        """
        Fetches and saves the marker ids currently in view, if more than self.refresh_interval seconds have passed since the last update.

        :param bool force_update: [optional] Force updates the marker ids if True. Defaults to False.
        """
        if force_update or (self.time() - self.last_refresh) > self.refresh_interval:
            self.markers = self.camera.see()
            self.last_refresh = self.time()
            return True
        return False

    def turn(self, speed: float = DEFAULT_ROTATION, reverse = False) -> None:
        """
        Turns the robot clockwise on-the-spot at the given speed. Input a negative speed to turn the robot anti-clockwise.

        :param float speed: [optional] The speed, from -1 to 1.
        :param bool reverse: [optional] Reverse the turn direction. Defaults to False.
        """
        if not reverse:
            self.left_motor.power = speed
            self.right_motor.power = -speed
        else:
            self.left_motor.power = -speed
            self.right_motor.power = speed

    def move(self, speed: float = DEFAULT_SPEED, reverse = False) -> None:
        if not reverse:
            self.left_motor.power = speed
            self.right_motor.power = speed
        else:
            self.left_motor.power = -speed
            self.right_motor.power = -speed

    def brake(self) -> None:
        """Brakes all motors."""
        self.left_motor.power = BRAKE
        self.right_motor.power = BRAKE

    def coast(self) -> None:
        """Coasts all motors."""
        self.left_motor.power = COAST
        self.right_motor.power = COAST

    def calculate_path(self, target_id: int, target_roll: int = None):
        """
        Calculates the path between the robot and the target marker.

        :param int target_id: The id of the target marker.
        :param int target_roll: [optional] The roll of the target marker; this differentiates between the faces of the marker. This value should be pre-normalised using round_90().

        :return: The path between the robot and the target marker.
        """
        pass

    def target_visible(self, target: str | int) -> bool:
        """
        Checks if the target zone or id is visible. If the target is a zone, the target id is set to that of the first visible marker.

        :param str|int target: The target zone or id.

        :return: True if the target zone or id is visible, False otherwise.
        """
        cache_markers = []
        if type(target) is str:
            for marker in self.markers:
                if marker.id in arena.map[target] and marker.id not in arena.excluded_pallets:
                    cache_markers.append(marker)
        else:
            for marker in self.markers:
                if marker.id == target:
                    return True
            return False

        if len(cache_markers) == 0:
            return False
        else:
            self.target_id = sorted(cache_markers, key = lambda marker: marker.position.distance)[0].id
            return True

    def select_target_id(self) -> bool:
        """
        Stops the robot if a target id within self.target_zone is visible. The target_visible function called also sets the target id.

        :return: Whether the robot has stopped.
        """
        if self.target_visible(self.target_zone):
            self.coast()
            return True
        return False

    def select_target_roll(self):
        """Selects the target roll (lowest absolute value of yaw relative to the camera) and sets it to self.target_roll."""
        self.target_roll = [round_90([marker for marker in sorted(self.markers, key = lambda marker: abs(marker.orientation.yaw) if abs(round_90(marker.orientation.roll)) != 90 else abs(marker.orientation.pitch)) if marker.id == self.target_id][0].orientation.roll)] # Stable sort. lambda marker: (marker.position.distance, abs(marker.orientation.yaw)
        if abs(self.target_roll[0]) == 180:
            self.target_roll = [-180, 180]
        print([(marker.id, marker.size, round_90(marker.orientation.roll), math.degrees(marker.orientation.roll), math.degrees(marker.orientation.yaw), math.degrees(marker.orientation.pitch)) for marker in sorted(self.markers, key = lambda marker: abs(marker.orientation.yaw) if abs(round_90(marker.orientation.roll)) != 90 else abs(marker.orientation.pitch)) if marker.id == self.target_id])

    def select_target_object(self) -> bool:
        """
        Saves the appropriate marker object with matching id and roll to self.target_object. Returns False if not visible.

        :return: Whether the selected marker face is visible."""
        try:
            self.target_object = [marker for marker in self.markers if marker.id == self.target_id and round_90(marker.orientation.roll) in self.target_roll][0]
            return True
        except:
            # self.target_object = None
            return False

    def calculate_real_yaw(self):
        """Calculates the marker's yaw from the perspective of the camera."""
        roll_cache = round_90(self.target_object.orientation.roll)
        is_roll_negative = -1 if roll_cache < 0 or roll_cache == 180 else 1
        if roll_cache == 0 or roll_cache == 180 or roll_cache == -180:
            self.real_yaw = is_roll_negative * self.target_object.orientation.yaw
        else:
            self.real_yaw = is_roll_negative * self.target_object.orientation.pitch
        # self.real_yaw = self.target_object.orientation.yaw if abs(round_90(self.target_object.orientation.roll)) != 90 else self.target_object.orientation.pitch if round_90(self.target_object.orientation.roll) == 90 else -self.target_object.orientation.pitch

    def calculate_perpendicular_distance(self):
        self.perpendicular_distance = (self.target_object.position.distance * math.sin(self.target_object.position.horizontal_angle)) / math.sin(math.pi - abs(self.real_yaw) - abs(self.target_object.position.horizontal_angle))

    def calculate_travel_distance(self):
        self.travel_distance = (self.target_object.position.distance * math.sin(self.real_yaw)) / math.sin(math.pi - abs(self.real_yaw) - abs(self.target_object.position.horizontal_angle))

    def update_ultrasound(self):
        self.front_ultrasound = self.arduino.ultrasound_measure(2, 3)
        self.front_left_microswitch = self.arduino.pins[10].digital_read()
        self.front_right_microswitch = self.arduino.pins[11].digital_read()

    def vacuum_control(self):
        self.vacuum_enabled.is_enabled = not self.vacuum_enabled.is_enabled
        if self.vacuum_enabled.is_enabled:
            self.vacuum_position.position = -1
            robot.sleep(0.5)
            self.vacuum_position.position = 1

    def fetch_next_state(self):
        match self.status:
            case State.SEARCH_1:
                if self.target_id in arena.map["highrise"]:
                    return State.TRAVEL_1 # State.TRAVEL_2A
                else:
                    return State.TRAVEL_1
            case State.TRAVEL_4:
                if self.target_id in arena.map["highrise"]:
                    return State.DROP_1
                else:
                    return State.PICKUP_1


    # def calculate_turn_direction(self):
    #     modifier = (self.perpendicular_distance < 0 and self.travel_distance < 0) or (self.perpendicular_distance > 0 and self.travel_distance > 0)
    #     has_negative_travel_distance = self.travel_distance < 0
    #     distance_satisfied = abs(self.perpendicular_distance) > 300
    #     if distance_satisfied:


class Arena:
    def __init__(self) -> None:
        self.map = {
            "boundary_0": [i for i in range(0, 7)],
            "boundary_90": [i for i in range(7, 14)],
            "boundary_180": [i for i in range(14, 21)],
            "boundary_270": [i for i in range(21, 28)],
            "boundary": [i for i in range(0, 28)],
            "pallets_0": [i for i in range(100, 120)],
            "pallets_1": [i for i in range(120, 140)],
            "pallets_2": [i for i in range(140, 160)],
            "pallets_3": [i for i in range(160, 180)],
            "highrise_center": [199],
            "highrise": [i for i in range(195, 200)],
            "highrise_0": [195],
            "highrise_1": [196],
            "highrise_2": [197],
            "highrise_3": [198],
            "highrise_targets": [199] # broken
        }

        self.map["highrise_targets"].extend(self.map[robot.own_highrise]) # NOT APPEND - append gives [199, [195]] which won't work # TODO retest

        self.highrise_capacity = {
            195: 2,
            196: 2,
            197: 2,
            198: 2,
            199: 1
        }
        self.highrise_info = {}      # Stores information about the pallets in each highrise, i.e. team, id, etc.
        for highrise in self.map["highrise"]:
            self.highrise_info[highrise] = []
        self.excluded_pallets = []

    def get_highrise_height(self, highrise_id: int) -> int:
        """
        Returns the height of a highrise.

        :param int highrise_id: The id of the highrise.

        :return: The height of the highrise.
        """
        return len(self.highrise_info[highrise_id])

    def drop_distance(self, highrise_id: int) -> int:
        if highrise_id not in self.highrise_capacity:
            return 30
        elif len(self.highrise_info[highrise_id]) < self.highrise_capacity[highrise_id]:
            print(self.highrise_info[highrise_id], 30)
            return 30
        else:
            print(self.highrise_info[highrise_id], 190)
            return 205


robot = MyRobot()
arena = Arena()

robot.see()         # Initialises the camera. There is a noticeable delay when capturing the first frame, so the camera needs to be initialised outside the main loop.
robot.sleep(0.5)

while True:
    refreshed_camera = robot.see()
    # if refreshed_camera and robot.target_id is not None and robot.target_roll is not None:
    #     robot.select_target_object()
    match robot.status:
        case State.INITIAL:
            robot.refresh_interval = 0.05
            robot.turn(reverse = False if len(arena.excluded_pallets) < 3 else True)
            robot.activity_start_time = robot.time()
            robot.activity_stop_time = robot.activity_start_time + 11    # Activity time-out occurs after 11 seconds (when the robot has turned 360 degrees).
            robot.status = State.SEARCH_1
        case State.SEARCH_1 if refreshed_camera:    # Performance improvement; prevents code from running if camera hasn't updated. Remove 'if refreshed_camera' if self.refresh_interval is particularly high as the robot may take longer than expected to sop if no target id is found.
            is_target_found = robot.select_target_id()
            print("SEARCH_1 is_target_found", is_target_found)
            match is_target_found:
                case True:
                    # The robot found a target id within 11 seconds of the activity starting.
                    # robot.sleep(0.5)    # Wait for the robot to come to a complete stop.
                    robot.select_target_roll()
                    robot.status = robot.fetch_next_state()
                    robot.activity_start_time = robot.time()
                    robot.activity_stop_time = robot.activity_start_time + 11
                    robot.refresh_interval = 0.001
                case False if robot.time() > robot.activity_stop_time:
                    # The robot turned on the spot for 11 seconds without finding a target id. Initiate backup search algorithm / change robot position.
                    pass
        case State.TRAVEL_1 if refreshed_camera:
            is_target_in_view = robot.select_target_object() # fix marker goes out of view + negative values + marker to the right, replace distance with horizontal distance (accounting for vertical angle etc.)
            print("TRAVEL_1 is_target_in_view", is_target_in_view)
            # print([(marker.id, marker.size, round_90(marker.orientation.roll), math.degrees(marker.orientation.roll), math.degrees(marker.orientation.yaw), math.degrees(marker.orientation.pitch)) for marker in sorted(robot.markers, key=lambda marker: abs(marker.orientation.yaw) if abs(round_90(marker.orientation.roll)) != 90 else abs(marker.orientation.pitch)) if marker.id == robot.target_id])
            # print("REAL YAW", robot.real_yaw, "ROLL", round_90(robot.target_object.orientation.roll), "RAW ROLL", math.degrees(robot.target_object.orientation.roll), "YAW", math.degrees(robot.target_object.orientation.yaw), "PITCH", math.degrees(robot.target_object.orientation.pitch))
            match is_target_in_view:
                case True:
                    robot.calculate_real_yaw()
                    print("REAL YAW", math.degrees(robot.real_yaw), "RAW_ROLL", math.degrees(robot.target_object.orientation.roll), "ROLL", round_90(robot.target_object.orientation.roll), "YAW", math.degrees(robot.target_object.orientation.yaw), "PITCH", math.degrees(robot.target_object.orientation.pitch), "HORIZONTAL ANGLE", math.degrees(robot.target_object.position.horizontal_angle))
                    robot.calculate_travel_distance()
                    robot.calculate_perpendicular_distance()
                    print(robot.perpendicular_distance, robot.target_object.position.horizontal_angle)
                    robot.reverse = robot.real_yaw < 0
                    # TODO update boolean logic as may not work in some scenarios + infinite loop if marker starts too close
                    # if abs(robot.perpendicular_distance) > 400 and not ((robot.perpendicular_distance < 0 and robot.travel_distance < 0) or (robot.perpendicular_distance > 0 and robot.travel_distance > 0)):
                    #     robot.reverse = robot.travel_distance < 0
                    #     robot.turn(reverse = robot.reverse)
                    # elif 400 < abs(robot.perpendicular_distance):
                    #     robot.brake()
                    #     robot.status = State.TRAVEL_2
                    #     robot.activity_start_time = robot.time()
                    #     robot.move()
                    #     robot.activity_stop_time = robot.activity_start_time + abs((robot.travel_distance * 0.001) / (robot.default_speed * 25 * 1.015 * robot.wheel_radius))
                    #     print("PERPENDICULAR DISTANCE", robot.perpendicular_distance, "TRAVEL DISTANCE", robot.travel_distance)
                    #     print("travel time:", (robot.travel_distance * 0.001) / (robot.default_speed * 25 * 1.015 * robot.wheel_radius))
                    # else:
                    #     robot.reverse = robot.travel_distance > 0
                    #     robot.turn(reverse = robot.reverse)
                    #     # robot.reverse = robot.travel_distance < 0
                    #     # robot.turn(reverse = robot.reverse)
                    #     print("BACKUP TRAVEL_1")
                    #     robot.sleep(1)
                    #     robot.brake()
                    #     robot.status = State.TRAVEL_2
                    #     robot.activity_start_time = robot.time()
                    #     robot.move()
                    #     robot.activity_stop_time = robot.activity_start_time + abs((robot.travel_distance * 0.001) / (robot.default_speed * 25 * 1.015 * robot.wheel_radius))
                    #     print("PERPENDICULAR DISTANCE", robot.perpendicular_distance, "TRAVEL DISTANCE", robot.travel_distance)
                    #     print("travel time:", (robot.travel_distance * 0.001) / (robot.default_speed * 25 * 1.015 * robot.wheel_radius))

                    # if (robot.real_yaw < 0 and robot.perpendicular_distance < -400) or (robot.real_yaw > 0 and robot.perpendicular_distance < 400):
                    #     robot.turn(reverse = True)
                    # elif (robot.real_yaw > 0 and robot.perpendicular_distance > 400) or (robot.real_yaw < 0 and robot.perpendicular_distance > -400):
                    #     robot.turn()
                    # else:
                    #     robot.brake()

                    if robot.real_yaw > 0 and robot.perpendicular_distance < 280:
                        robot.turn(reverse = True)
                    elif robot.real_yaw < 0 and robot.perpendicular_distance > -280:
                        robot.turn()
                    else:
                        robot.brake()
                        robot.status = State.TRAVEL_2
                        robot.move()
                        robot.activity_start_time = robot.time()
                        robot.activity_stop_time = robot.activity_start_time + abs((robot.travel_distance * 0.001) / (robot.default_speed * 25 * 1.1 * robot.wheel_radius)) # TODO bug if changed to 1.1/1.2
                        print("PERPENDICULAR DISTANCE", robot.perpendicular_distance, "TRAVEL DISTANCE", robot.travel_distance)
                        print("travel time:", abs((robot.travel_distance * 0.001) / (robot.default_speed * 25 * 1.1 * robot.wheel_radius)))


                case False if robot.time() > robot.activity_stop_time:
                    pass
                case False:
                    robot.turn(0.5 * DEFAULT_ROTATION)
        case State.TRAVEL_2:
            if robot.time() > robot.activity_stop_time:
                robot.brake()
                robot.status = State.TRAVEL_3
                robot.refresh_interval = 0.001
                robot.activity_start_time = robot.time()
                robot.turn(speed = 0.5 * DEFAULT_ROTATION, reverse = robot.reverse)
                robot.activity_stop_time = robot.activity_start_time + 13
        case State.TRAVEL_2A:
            robot.status = State.TRAVEL_3
            robot.refresh_interval = 0.001
            robot.activity_start_time = robot.time()
            robot.turn(speed= 0.5 * DEFAULT_ROTATION)
            robot.activity_stop_time = robot.activity_start_time + 13
        case State.TRAVEL_3:
            is_target_in_view = robot.select_target_object()
            match is_target_in_view:
                case True:
                    if math.degrees(abs(robot.target_object.position.horizontal_angle)) < 1:
                        robot.move(0.1)
                        robot.status = State.TRAVEL_4
                case False if robot.time() > robot.activity_stop_time:
                    pass
        case State.TRAVEL_4:
            robot.update_ultrasound()
            is_target_in_view = robot.select_target_object()
            match is_target_in_view:
                case True if math.degrees(abs(robot.target_object.position.horizontal_angle)) > 1.5 and robot.target_object.position.distance > 350:
                    robot.turn(speed= 0.5 * DEFAULT_ROTATION, reverse=robot.target_object.position.horizontal_angle < 0)
                    robot.status = State.TRAVEL_3
                case False if ((robot.front_ultrasound != 0) and (robot.front_ultrasound < arena.drop_distance(robot.target_id))) or (robot.front_ultrasound == 0 and arena.drop_distance(robot.target_id) == 205) or ((robot.front_ultrasound == 0 or robot.target_id in arena.highrise_capacity) and (robot.front_left_microswitch or robot.front_right_microswitch)):
                    robot.brake()
                    robot.status = robot.fetch_next_state()
                    robot.sleep(0.5)
                    robot.vacuum_control()
                    if robot.status == State.PICKUP_1: # allows for box to be fully picked up before ultrasound reading taken
                        robot.sleep(1.5)

            print(robot.travel_distance, robot.perpendicular_distance, robot.target_object.position.distance, math.degrees(robot.real_yaw), robot.front_ultrasound)
        case State.PICKUP_1:
            print("PICKUP_1", "FRONT ULTRASOUND", robot.front_ultrasound, "LEFT MICROSWITCH", robot.front_left_microswitch, "RIGHT MICROSWITCH", robot.front_right_microswitch)
            robot.update_ultrasound()
            if (robot.front_ultrasound != 0 and robot.front_ultrasound < 50) or robot.front_left_microswitch or robot.front_right_microswitch:
                # broken? intended to detect if the pallet was actually successfully picked up
                # robot.move(reverse = True)
                robot.vacuum_control()
                robot.sleep(1.5)
                # robot.status = State.TRAVEL_4 # causes infinite loop
            else:
                robot.target_zone = robot.own_highrise # TODO if len(arena.excluded_pallets) < 4 else "highrise_center" # slightly dodgy - for this to work get the nearest pallet to the center; also calculate how much time is left - go to own highrise if not enough time
                robot.pallet_in_possession = robot.target_id
                robot.status = State.INITIAL
                robot.reverse = not robot.reverse

        case State.DROP_1:
            robot.target_zone = robot.own_pallets
            arena.highrise_info[robot.target_id].append(robot.pallet_in_possession)
            arena.excluded_pallets.append(robot.pallet_in_possession)

            robot.move(reverse=True)
            if len(arena.excluded_pallets) != 3:
                robot.sleep(0.2)
            else:
                robot.sleep(1.5)
                # DEFAULT_ROTATION = -0.1
                robot.turn(-0.1)
                robot.sleep(0.5)

            robot.status = State.INITIAL
            robot.reverse = False


# fix boolean logic - does not work properly when dragged in front of camera etc. - perhaps hardcode turn directions (i.e. first 3 boxes: turn right then turn left) etc.
# add error-detection when found id goes out-of-view
# https://ftc-docs.firstinspires.org/en/latest/apriltag/understanding_apriltag_detection_values/understanding-apriltag-detection-values.html

# calculate travel time with acceleration in mind?
# add condition so that robot picks up pallet if pallet touches sensors; ultrasound doesn't always work

# TODO fix camera refresh interval after 4th pallet