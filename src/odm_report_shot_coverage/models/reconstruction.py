import geojson
from scipy import stats

from odm_report_shot_coverage.models.camera import Camera, json_parse_camera
from odm_report_shot_coverage.models.shot import Shot, shot_boundaries_from_points
from odm_report_shot_coverage.models.wavefront_25d import Wavefront25D, parse_wavefront_25d_obj


class Reconstruction:
    cameras: 'dict[str, Camera]' = {}
    _shots: 'list[Shot]' = []
    mesh = Wavefront25D

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
        }

    def compute_shot_boundaries(self):
        """
        From shots and points, fill the shot_boundaries
        :rtype: None
        """

        for shot in self.shots:
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


def parse_reconstruction(path: str) -> Reconstruction:
    reconstruction = Reconstruction()
    with open('%s/cameras.json' % path, 'r') as fd:
        cameras_json = geojson.load(fd)
        for n, j in cameras_json.items():
            camera = json_parse_camera(n, j)
            reconstruction.add_camera(n, camera)

    with open('%s/odm_report/shots.geojson' % path, 'r') as fd:
        shots_geojson = geojson.load(fd)
        for feat in shots_geojson['features']:
            shot = Shot()
            props = feat['properties']
            shot.camera = reconstruction.find_camera_by_width_height(props['width'], props['height'])
            shot.image_name = props['filename']
            shot.translation = props['translation']
            shot.rotation = props['rotation']
            reconstruction.add_shot(shot)

    wf = parse_wavefront_25d_obj('%s/odm_texturing_25d/odm_textured_model_geo.obj' % path)
    reconstruction.mesh = wf

    return reconstruction
