import json

from models.camera import Camera, json_parse_camera
from models.point import Point, json_parse_point
from models.shot import Shot, json_parse_shot, ShotOrthoBoundaries
from scipy import stats


class Reconstruction:
    cameras: dict[str, Camera] = {}
    _shots: list[Shot] = []
    points: list[Point] = []
    shot_boundaries: dict[str, ShotOrthoBoundaries] = {}
    shot_points: dict[str, set[int]] = {}

    @property
    def shots(self) -> list[Shot]:
        self._shots.sort(key=lambda s: s.image_name)
        return self._shots

    def add_camera(self, name: str, camera: Camera):
        self.cameras[name] = camera

    def add_shot(self, shot: Shot):
        self._shots.append(shot)

    def add_point(self, point: Point):
        self.points.append(point)

    def to_json(self) -> dict:
        return {
            'cameras': json.dumps(self.cameras, default=vars),
            'shots': [s.to_json() for s in self.shots],
            'points': {p.id: json.dumps(p, default=vars) for p in self.points},
            'shotBoundaries': {i: json.dumps(b, default=vars) for i, b in self.shot_boundaries.items()},
            'shotPoints': self.shot_points
        }

    def compute_shot_point_coverage(self):
        """
        From shots and points, fill the shot_boundaries and the shot_contains_points maps
        :rtype: None
        """
        ret = {}
        for shot in self.shots:
            pix_coords = []
            for point in self.points:
                pixel = shot.camera_pixel(point.coordinates)
                if shot.camera.in_frame(pixel):
                    pix_coords.append((pixel, point.coordinates))
                    if shot.image_name not in self.shot_points:
                        self.shot_points[shot.image_name] = set()
                    self.shot_points[shot.image_name].add(point.id)
        if len(pix_coords) >= 2:
            ret[shot.image_name] = ShotOrthoBoundaries(
                x_min=min([(pc[1][0]) for pc in pix_coords]),
                x_max=max([(pc[1][0]) for pc in pix_coords]),
                y_min=min([(pc[1][1]) for pc in pix_coords]),
                y_max=max([(pc[1][1]) for pc in pix_coords]),
            )


class ReconstructionCollection:
    reconstructions: list[Reconstruction] = []

    def append(self, reconstruction: Reconstruction):
        self.reconstructions.append(reconstruction)

    def __getitem__(self, i: int):
        return self.reconstructions[i]

    def __len__(self):
        return len(self.reconstructions)


def lin_reg(pairs: list[(float, float)]) -> (float, float, float, float):
    x = [p[0] for p in pairs]
    y = [p[1] for p in pairs]
    return stats.linregress(x, y)


def json_parse_reconstruction(el: dict) -> Reconstruction:
    reconstruction = Reconstruction()
    for name, ela in el['cameras'].items():
        reconstruction.add_camera(name, json_parse_camera(name, ela))

    for image_name, ela in el['shots'].items():
        reconstruction.add_shot(json_parse_shot(image_name, ela, reconstruction.cameras))

    for name, ela in el['points'].items():
        reconstruction.add_point(json_parse_point(name, ela))

    return reconstruction


def json_parse_reconstruction_collection(el: dict) -> ReconstructionCollection:
    rc = ReconstructionCollection()
    for elr in el:
        rc.append(json_parse_reconstruction(elr))
    return rc
