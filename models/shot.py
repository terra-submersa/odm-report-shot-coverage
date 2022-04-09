import numpy as np
from scipy.spatial.transform import Rotation as R, Rotation

from models.camera import Camera


class ShotBoundaries:
    path: [(float, float)]

    __max_val = 10000000

    def __init__(
            self,
            path: [(float, float)],
    ):
        self.path = path

    def to_json(self) -> dict:
        return {
            'path': self.path
        }

    def __repr__(self):
        return '[%f, %f] x [%f, %f]' % (self.x_min, self.x_max, self.y_min, self.y_max)


def shot_boundaries_from_points(points: list[(float, float)]) -> ShotBoundaries:
    midpoint = (sum([p[0] for p in points])/len(points),sum([p[0] for p in points])/len(points))

    leftmost = max(points, key=lambda p: (p[0]-midpoint[0])*(p[0]-midpoint[0]) + (p[1]-midpoint[1])*(p[1]-midpoint[1]))
    rightmost = max(points, key=lambda p: (p[0]-leftmost[0])*(p[0]-leftmost[0]) + (p[1]-leftmost[1])*(p[1]-leftmost[1]))
    ft = leftmost
    d_ft = 0
    fl = leftmost
    d_fl = 0
    am = rightmost[0] - leftmost[0]
    bm = rightmost[1] - leftmost[1]
    for p in points:
        a1 = p[0] - leftmost[0]
        b1 = p[1] - leftmost[1]
        a2 = p[0] - rightmost[0]
        b2 = p[1] - rightmost[1]

        d = np.sqrt(a1 * a1 + b1 * b1) + np.sqrt(a2 * a2 + b2 * b2)
        if a1 * bm - b1 * am >= 0:
            if d > d_ft:
                ft = p
                d_ft = d
        else:
            if d > d_fl:
                fl = p
                d_fl = d
    return ShotBoundaries([leftmost, ft, rightmost, fl])


class Shot:
    image_name: str
    _rotation: (float, float, float)
    translation: (float, float, float)
    camera: Camera
    _transfo_rotation: Rotation
    boundaries: ShotBoundaries

    @property
    def rotation(self) -> (float, float, float):
        return self._rotation

    @rotation.setter
    def rotation(self, new_rotation: (float, float, float)):
        self._rotation = new_rotation
        (r_x, r_y, r_z) = new_rotation
        self._transfo_rotation = R.from_rotvec([r_x, r_y, r_z])

    def boundaries_from_points(self, points: list[(float, float)]):
        self.boundaries = shot_boundaries_from_points(points)

    def __repr__(self):
        return '%s translation=(%.2f, %.2f, %.2f) rotation=(%.2f, %.2f, %.2f)' % (
            self.image_name,
            self.translation[0], self.translation[1], self.translation[2],
            self.rotation[0], self.rotation[1], self.rotation[2],
        )

    def to_json(self):
        return {
            'imageName': self.image_name,
            'camera': self.camera.to_json(),
            'rotation': self._rotation,
            'translation': self.translation,
            'camera': self.camera.name,
            'boundaries': self.boundaries.to_json()
        }

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


class Boundaries:
    x_min: float
    x_max: float
    y_min: float
    y_max: float

    def __init__(self, x_min: float, x_max: float, y_min: float, y_max: float):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def to_json(self) -> dict:
        return {
            'xMin': self.x_min,
            'xMax': self.x_max,
            'yMin': self.y_min,
            'yMax': self.y_max,
        }

    def __repr__(self):
        return '[%f, %f] x [%f, %f]' % (self.x_min, self.x_max, self.y_min, self.y_max)


def json_parse_shot(image_name: str, el: dict, cameras: dict[str, Camera]) -> Shot:
    shot = Shot()
    shot.image_name = image_name
    shot.rotation = el['rotation']
    shot.translation = el['translation']
    shot.camera = cameras[el['camera']]
    return shot
