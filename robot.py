import math

from sr.robot3 import *
from math import degrees, radians


def round_10(n) -> int:
    """
    Rounds a number to the nearest tenth.

    :param float n: The number to be rounded.

    :return: The rounded number.
    """
    return round(math.degrees(n) / 10) * 10


class MyRobot(Robot):
    def __init__(self) -> None:
        """Initialises the robot."""
        Robot.__init__(self)
        self.vacuum = self.power_board.outputs[OUT_H0]
        self.markers = []
        self.last_refresh = 0
        self.refresh_interval = 0.05

    def see(self, force_update = False) -> None:
        """
        Fetches and saves marker ids currently in view, if more than self.refresh_interval seconds have passed since the last update.

        :param bool force_update: [optional] Force updates the marker ids if True. Defaults to False.
        """
        if force_update or (self.time() - self.last_refresh) > self.refresh_interval:
            self.markers = self.camera.see()

    def calculate_path(self, target_id, target_roll = None):
        """
        Calculates the path between the robot and the target marker.

        :param int target_id: The id of the target marker.
        :param int target_roll: [optional] The roll of the target marker; this differentiates between the faces of the marker. This value should be pre-normalised using round_10().

        :return: The path between the robot and the target marker.
        """

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
        self.highriseInfo = {}
        for highrise in self.map["highrise"]:
            self.highriseInfo[highrise] = []
        print(self.highriseInfo)

    def get_highrise_height(self, highrise_id) -> int:
        """
        Returns the height of a highrise.

        :param int highrise_id: The id of the highrise.

        :return: The height of the highrise.
        """
        return len(self.highriseInfo[highrise_id])

robot = MyRobot()
arena = Arena()
