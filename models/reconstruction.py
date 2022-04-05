import json

import geojson

from models.camera import Camera, json_parse_camera
from models.point import Point, json_parse_point
from models.shot import Shot, json_parse_shot, ShotOrthoBoundaries
from scipy import stats


class Reconstruction:
    cameras: dict[str, Camera] = {}
    _shots: list[Shot] = []
    points: list[(float, float, float)] = []
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

    def add_point(self, coordinates: (float, float, float)):
        self.points.append(coordinates)

    def to_json(self) -> dict:
        return {
            'cameras': {name: camera.to_json() for name, camera in self.cameras.items()},
            'shots': [s.to_json() for s in self.shots],
            'points': self.points,
            'shotBoundaries': {i: b.to_json() for i, b in self.shot_boundaries.items()},
            'shotPoints': {img: list(points) for img, points in self.shot_points.items()}
        }

    def compute_shot_point_coverage(self):
        """
        From shots and points, fill the shot_boundaries and the shot_contains_points maps
        :rtype: None
        """
        for shot in self.shots:
            pix_coords = []
            for i, point in enumerate(self.points):
                pixel = shot.camera_pixel(point)
                if shot.camera.in_frame(pixel):
                    pix_coords.append((pixel, point))
                    if shot.image_name not in self.shot_points:
                        self.shot_points[shot.image_name] = set()
                    self.shot_points[shot.image_name].add(i)
            self.shot_boundaries[shot.image_name] = ShotOrthoBoundaries(
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


def json_parse_reconstruction(path: str) -> Reconstruction:
    reconstruction = Reconstruction()
    with open('%s/odm_report/shots.geojson' % path) as fd:
        shots_geojson = geojson.load(fd)
        for feat in shots_geojson['features']:
            props = feat['properties']
            camera = Camera()
            camera.name = '-'
            camera.focal = props['focal']
            camera.width = props['width']
            camera.height = props['height']
            shot = Shot()
            shot.camera = camera
            shot.image_name = props['filename']
            shot.translation = props['translation']
            shot.rotation = props['rotation']
            reconstruction.add_shot(shot)

    with open('%s/odm_texturing_25d/odm_textured_model_geo.obj' % path) as fd:
        for l in [l for l in fd.readlines() if l.startswith('v ')]:
            v = l.replace('v ', '').split(' ')
            reconstruction.add_point([float(v[0]), float(v[1]), float(v[2])])

    #
    # for name, ela in el['points'].items():
    #     reconstruction.add_point(json_parse_point(name, ela))

    return reconstruction


def json_parse_reconstruction_collection(el: dict) -> ReconstructionCollection:
    rc = ReconstructionCollection()
    for elr in el:
        rc.append(json_parse_reconstruction(elr))
    return rc
