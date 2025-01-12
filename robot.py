import math

from sr.robot3 import *
from enum import Enum

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
    return round(round(math.degrees(n)/10)/1/9) * 90

class State(Enum):
    INITIAL = "initial"
    SEARCH_1 = "search_1"

class MarkerProperty(Enum):
    ID = "marker.id"
    ROLL = "marker.orientation.roll"
    DISTANCE = "marker.position.distance"

class MyRobot(Robot):
    def __init__(self) -> None:
        """Initialises the robot."""
        Robot.__init__(self)
        self.vacuum = self.power_board.outputs[OUT_H0]
        self.vacuum.is_enabled = False
        self.markers = []
        self.filtered_markers = []
        self.filter_properties = []
        self.last_refresh = 0
        self.refresh_interval = 0.05
        self.left_motor = self.motor_board.motors[0]
        self.right_motor = self.motor_board.motors[1]

        self.target_id = None
        self.target_roll = None

        self.own_pallets = f"pallets_{self.zone}"
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

    def turn(self, speed: float = 0.1) -> None:
        """
        Turns the robot clockwise on-the-spot at the given speed. Input a negative speed to turn the robot anti-clockwise.

        :param float speed: The speed, from -1 to 1.
        """
        self.left_motor.power = speed
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
        :param int target_roll: [optional] The roll of the target marker; this differentiates between the faces of the marker. This value should be pre-normalised using round_10().

        :return: The path between the robot and the target marker.
        """
        pass

    def target_visible(self, target: str | int) -> bool:
        """
        Checks if the target zone or id is visible. If the target is a zone, the target id is set to that of the first visible marker.

        :param str|int target: The target zone or id.

        :return: True if the target zone or id is visible, False otherwise.
        """
        if type(target) is str:
            for marker in self.markers:
                if marker.id in arena.map[target]:
                    self.target_id = marker.id
                    return True
            return False
        else:
            for marker in self.markers:
                if marker.id == target:
                    return True
            return False

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
        self.target_roll = round_10([marker for marker in sorted(self.markers, key = lambda marker: abs(marker.orientation.yaw) if abs(round_10(marker.orientation.roll)) != 90 else abs(marker.orientation.pitch)) if marker.id == self.target_id][0].orientation.roll) # Stable sort. lambda marker: (marker.position.distance, abs(marker.orientation.yaw)
        print([(marker.id, round_10(marker.orientation.roll), math.degrees(marker.orientation.yaw), math.degrees(marker.orientation.pitch)) for marker in sorted(self.markers, key = lambda marker: abs(marker.orientation.yaw) if abs(round_10(marker.orientation.roll)) != 90 else abs(marker.orientation.pitch)) if marker.id == self.target_id])


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
            "highrise_0": [195]
        }
        self.highriseInfo = {}      # Stores information about the pallets in each highrise, i.e. team, id, etc.
        for highrise in self.map["highrise"]:
            self.highriseInfo[highrise] = []

    def get_highrise_height(self, highrise_id: int) -> int:
        """
        Returns the height of a highrise.

        :param int highrise_id: The id of the highrise.

        :return: The height of the highrise.
        """
        return len(self.highriseInfo[highrise_id])

robot = MyRobot()
arena = Arena()

robot.see()         # Initialises the camera. There is a noticeable delay when capturing the first frame, so the camera needs to be initialised outside the main loop.
robot.sleep(0.5)

while True:
    refreshed_camera = robot.see()
    match robot.status:
        case State.INITIAL:
            robot.turn()
            robot.activity_start_time = robot.time()
            robot.activity_stop_time = robot.activity_start_time + 11    # Activity time-out occurs after 11 seconds (when the robot has turned 360 degrees).
            robot.status = State.SEARCH_1
        case State.SEARCH_1 if refreshed_camera:    # Performance improvement; prevents code from running if camera hasn't updated. Remove 'if refreshed_camera' if self.refresh_interval is particularly high as the robot may take longer than expected to sop if no target id is found.
            is_target_found = robot.select_target_id()
            match is_target_found:
                case True:
                    # The robot found a target id within 11 seconds of the activity starting.
                    # robot.sleep(0.5)    # Wait for the robot to come to a complete stop.
                    robot.select_target_roll()
                    print(robot.target_roll)
                case False if robot.time() > robot.activity_stop_time:
                    # The robot turned on the spot for 11 seconds without finding a target id. Initiate backup search algorithm / change robot position.
                    pass

# add error-detection when found id goes out-of-view
# round to nearest 45/90 degrees rather than 10 as roll property can sometimes be unreliable
# https://ftc-docs.firstinspires.org/en/latest/apriltag/understanding_apriltag_detection_values/understanding-apriltag-detection-values.html