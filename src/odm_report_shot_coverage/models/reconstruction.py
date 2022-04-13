import json
import logging

import geojson
import numpy as np
from tqdm import tqdm
from scipy import stats

from odm_report_shot_coverage.models.camera import Camera, json_parse_camera
from odm_report_shot_coverage.models.shot import Shot, shot_boundaries_from_points, Boundaries
from odm_report_shot_coverage.models.wavefront_25d import Wavefront25D, parse_wavefront_25d_obj


class Reconstruction:
    cameras: 'dict[str, Camera]' = {}
    _shots: 'list[Shot]' = []
    mesh = Wavefront25D
    orthophoto_boundaries: Boundaries

    @property
    def shots(self) -> 'list[Shot]':
        self._shots.sort(key=lambda s: s.image_name)
        return self._shots

    def add_camera(self, name: str, camera: Camera):
        self.cameras[name] = camera

    def add_shot(self, shot: Shot):
        self._shots.append(shot)

    def to_json(self) -> dict:
        return {
            'cameras': {n: c.to_json() for n, c in self.cameras.items()},
            'shots': [s.to_json() for s in self.shots],
            # 'mesh': self.mesh.to_json(),
            'boundaries': self.mesh.boundaries.to_json(),
            'orthophotoBoundaries': self.orthophoto_boundaries.to_json(),
        }

    def compute_shot_boundaries(self):
        """
        From shots and points, fill the shot_boundaries
        :rtype: None
        """

        for shot in tqdm(self.shots, desc='Computing shot boundaries'):
            points = []
            for i, point in enumerate(self.mesh.points):
                pixel = shot.camera_pixel(point)
                if shot.camera.in_frame(pixel):
                    points.append(point)
            shot.boundaries = shot_boundaries_from_points(points)

    def find_camera_by_width_height(self, width: int, height: int) -> Camera:
        cs = [c for c in self.cameras.values() if c.width == width and c.height == height]
        if len(cs) != 1:
            raise Exception('Not exactly one camera found with size %s x %s' % (width, height))
        return cs[0]


class ReconstructionCollection:
    reconstructions: 'list[Reconstruction]' = []

    def append(self, reconstruction: Reconstruction):
        self.reconstructions.append(reconstruction)

    def __getitem__(self, i: int):
        return self.reconstructions[i]

    def __len__(self):
        return len(self.reconstructions)


def lin_reg(pairs: 'list[(float, float)]') -> (float, float, float, float):
    x = [p[0] for p in pairs]
    y = [p[1] for p in pairs]
    return stats.linregress(x, y)


def _parse_point_cloud_boundaries(path: str) -> Boundaries:
    with open('%s/odm_report/stats.json' % path, 'r') as fd:
        stats_json = json.load(fd)
        bbox = stats_json['point_cloud_statistics']['stats']['bbox']['native']['bbox']
        return Boundaries(
            x_min=bbox['minx'],
            x_max=bbox['maxx'],
            y_min=bbox['miny'],
            y_max=bbox['maxy'],
            z_min=bbox['minz'],
            z_max=bbox['maxz'],
        )


def _parse_camera_shotgeojson(path: str, reconstruction: Reconstruction, native_to_25d_coordinates):
    with open('%s/cameras.json' % path, 'r') as fd:
        cameras_json = json.load(fd)
        for n, j in cameras_json.items():
            camera = json_parse_camera(n, j)
            reconstruction.add_camera(n, camera)

    (tr_x, tr_y, tr_z) = native_to_25d_coordinates
    with open('%s/odm_report/shots.geojson' % path, 'r') as fd:
        shots_geojson = geojson.load(fd)
        for feat in shots_geojson['features']:
            shot = Shot()
            props = feat['properties']
            shot.camera = reconstruction.find_camera_by_width_height(props['width'], props['height'])
            shot.image_name = props['filename']
            translation = props['translation']
            shot.translation = (tr_x(translation[0]), tr_y(translation[1]), tr_z(translation[2]))
            shot.rotation = props['rotation']
            reconstruction.add_shot(shot)


def _native_to_model_25d_coordinates(native_boundaries: Boundaries, model_25d_boundaries: Boundaries):
    width_25d = model_25d_boundaries.x_max - model_25d_boundaries.x_min
    height_25d = model_25d_boundaries.y_max - model_25d_boundaries.y_min
    elevation_25d = model_25d_boundaries.y_max - model_25d_boundaries.y_min
    width_native = native_boundaries.x_max - native_boundaries.x_min
    height_native = native_boundaries.y_max - native_boundaries.y_min
    elevation_native = native_boundaries.y_max - native_boundaries.y_min
    width_ratio = np.abs(1 - width_native / width_25d)
    height_ratio = np.abs(1 - height_native / height_25d)
    elevation_ratio = np.abs(1 - elevation_native / elevation_25d)
    logging.info(
        'native/25d model boundaries discrepancies width=%.2f%% height=%.2f%% elevation=%.2f%%' % (
            width_ratio * 100, height_ratio * 100, elevation_ratio * 100))

    return (
        lambda x: (x - (native_boundaries.x_max + native_boundaries.x_min) / 2) + (
                model_25d_boundaries.x_max + model_25d_boundaries.x_min) / 2,
        lambda y: (y - (native_boundaries.y_max + native_boundaries.y_min) / 2) + (
                model_25d_boundaries.y_max + model_25d_boundaries.y_min) / 2,
        lambda z: (z - (native_boundaries.z_max + native_boundaries.z_min) / 2) + (
                model_25d_boundaries.z_max + model_25d_boundaries.z_min) / 2
    )


def parse_reconstruction(path: str) -> Reconstruction:
    reconstruction = Reconstruction()

    wf = parse_wavefront_25d_obj('%s/odm_texturing_25d/odm_textured_model_geo.obj' % path)
    reconstruction.mesh = wf
    reconstruction.orthophoto_boundaries = wf.boundaries

    native_boundaries = _parse_point_cloud_boundaries(path)
    _parse_camera_shotgeojson(path, reconstruction,
                              _native_to_model_25d_coordinates(native_boundaries, wf.boundaries))

    return reconstruction
