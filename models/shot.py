import numpy as np
from scipy.spatial.transform import Rotation as R, Rotation

from models.camera import Camera


class Shot:
    image_name: str
    _rotation: (float, float, float)
    translation: (float, float, float)
    camera: Camera
    _transfo_rotation: Rotation

    @property
    def rotation(self) -> (float, float, float):
        return self._rotation

    @rotation.setter
    def rotation(self, new_rotation: (float, float, float)):
        self._rotation = new_rotation
        (r_x, r_y, r_z) = new_rotation
        # print(np.sqrt(r_x*r_x+r_y*r_y+r_z*r_z))

        self._transfo_rotation = R.from_rotvec([r_x, r_y, r_z])

        # (r_x, r_y, r_z) = (0, 0, np.pi)

        # self._transfo_rotation = R.from_euler('xyz', [0, 0, 0 ], degrees=True)
        # self._transfo_rotation = R.from_rotvec([np.pi/np.sqrt(2), np.pi/np.sqrt(2), 0])

        # print(self._transfo_rotation.as_euler('xyz'))
        # print(self._transfo_rotation.as_rotvec())

    def __repr__(self):
        return '%s translation=(%.2f, %.2f, %.2f) rotation=(%.2f, %.2f, %.2f)' % (
            self.image_name,
            self.translation[0], self.translation[1], self.translation[2],
            self.rotation[0], self.rotation[1], self.rotation[2],
        )

    def camera_relative_coordinates(self, abs_coords: (float, float, float)) -> (float, float, float):
        """
        from an absolute coordinates, return a coordinates relative to the camera, applying the rotation + translation backwards
        :param abs_coords: the absolute coordinates
        :type abs_coords: (float, float, float)
        :return: (x,y,z), in camera pixel
        :rtype:(float, float, float)
        """
        tc = abs_coords[0] - self.translation[0], abs_coords[1] - self.translation[1], abs_coords[2] - self.translation[
            2]
        rc = self._transfo_rotation.apply(tc, inverse=True)
        return rc[0], rc[1], rc[2]
        # rc = self._transfo_rotation.apply(abs_coords, inverse=True)
        # tc = rc[0] - self.translation[0], rc[1] - self.translation[1], rc[2] - self.translation[2]
        # return tc

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
