from models.camera import Camera
from scipy.spatial.transform import Rotation as R, Rotation
import numpy as np


class Shot:
    image_name: str
    _rotation: (float, float, float)
    translation: (float, float, float)
    camera: Camera
    _transfo_inv_rotation: Rotation

    @property
    def rotation(self) -> (float, float, float):
        return self._rotation

    @rotation.setter
    def rotation(self, new_rotation: (float, float, float)):
        self._rotation = new_rotation
        (r_x, r_y, r_z) = new_rotation
        self._transfo_inv_rotation = R.from_rotvec(np.pi / 2 * np.array([-r_x, -r_y, -r_z]))

    def camera_relative_coordinates(self, abs_coords: (float, float, float)) -> (float, float, float):
        """
        from an absolute coordinates, return a coordinates relative to the camera, applying the rotation + translation backwards
        :param abs_coords: the absolute coordinates
        :type abs_coords: (float, float, float)
        :return: (x,y,z), in camera pixel
        :rtype:(float, float, float)
        """
        rc = self._transfo_inv_rotation.apply(abs_coords)
        return rc[0] - self.translation[0], rc[1] - self.translation[1], rc[2] - self.translation[2]

    def camera_pixel(self, abs_coords: (float, float, float)) -> (float, float):
        """
        from an absolute coordinates, returns the camera pixels
        :param abs_coords: the absolute coordinates
        :type abs_coords:(float, float, float)
        :return: camera pixel (in [0,1] range)
        :rtype: (float, float)
        """
        rel_coords = self.camera_relative_coordinates(abs_coords)
        return self.camera.perspective_pixel(rel_coords)


def json_parse_shot(image_name: str, el: dict, cameras: dict[str, Camera]) -> Shot:
    shot = Shot()
    shot.image_name = image_name
    shot.rotation = el['rotation']
    shot.translation = el['translation']
    shot.camera = cameras[el['camera']]
    return shot
