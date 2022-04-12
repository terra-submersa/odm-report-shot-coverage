import numpy as np
from scipy.spatial.transform import Rotation as R, Rotation

from odm_report_shot_coverage.models.camera import Camera


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


def shot_boundaries_from_points(points: 'list[(float, float)]', nb_path_points: int = 36) -> ShotBoundaries:
    midpoint = (sum([p[0] for p in points]) / len(points), sum([p[1] for p in points]) / len(points))
    dist_slices = [0 for i in range(nb_path_points)]
    furthest_slices = [midpoint for i in range(nb_path_points)]

    def slice_index_dist(p: (float, float)):
        alpha = None
        vx = p[0] - midpoint[0]
        vy = p[1] - midpoint[1]
        if vx == 0:
            alpha = np.pi / 2 if vy >= 0 else - np.pi / 2
        else:
            alpha = np.arctan(vy / vx)
        i_slice = int(nb_path_points / 2 * (alpha / np.pi + 0.5))
        if vx < 0:
            i_slice += int(nb_path_points / 2)
        return i_slice, vx * vx + vy * vy

    for p in points:
        (i, d) = slice_index_dist(p)
        if d > dist_slices[i]:
            furthest_slices[i] = p
            dist_slices[i] = d

    return ShotBoundaries([(p[0], p[1]) for p in furthest_slices])


class Shot:
    image_name: str
    _rotation: (float, float, float)
    rotation_euler_xyz = (float, float, float)
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
        euler = self._transfo_rotation.as_euler('xyz')
        self.rotation_euler_xyz = (euler[0], euler[1], euler[2])

    def boundaries_from_points(self, points: 'list[(float, float)]'):
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
            'originalDimensions': {
                'width': self.camera.width,
                'height': self.camera.height,
            },
            'rotation': self._rotation,
            'rotationEulerXYZ': self.rotation_euler_xyz,
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
        rc = self._transfo_rotation.apply(tc, inverse=False)
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


def json_parse_shot(image_name: str, el: dict, cameras: 'dict[str, Camera]') -> Shot:
    shot = Shot()
    shot.image_name = image_name
    shot.rotation = el['rotation']
    shot.translation = el['translation']
    shot.camera = cameras[el['camera']]
    return shot
