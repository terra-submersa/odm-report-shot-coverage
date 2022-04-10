import geojson
from scipy import stats

from models.camera import Camera
from models.shot import Shot, shot_boundaries_from_points
from models.wavefront_25d import Wavefront25D, parse_wavefront_25d_obj


class Reconstruction:
    cameras: dict[str, Camera] = {}
    _shots: list[Shot] = []
    mesh = Wavefront25D

    @property
    def shots(self) -> list[Shot]:
        self._shots.sort(key=lambda s: s.image_name)
        return self._shots

    def add_camera(self, name: str, camera: Camera):
        self.cameras[name] = camera

    def add_shot(self, shot: Shot):
        self._shots.append(shot)

    def to_json(self) -> dict:
        return {
            'cameras': {n: c.to_json() for n, c in self.cameras},
            'shots': [s.to_json() for s in self.shots],
            # 'mesh': self.mesh.to_json(),
            'boundaries': self.mesh.boundaries.to_json(),
        }

    def compute_shot_boundaries(self):
        """
        From shots and points, fill the shot_boundaries
        :rtype: None
        """
        # self.mesh.points=[]
        # for i in range(-15, 20, 1):
        #     for j in range(-15, 20, 1):
        #         self.mesh.points.append((i, j, -10))

        for shot in self.shots:

            points = []
            for i, point in enumerate(self.mesh.points):
                pixel = shot.camera_pixel(point)
                if shot.camera.in_frame(pixel):
                    points.append(point)

            shot.boundaries = shot_boundaries_from_points(points)


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


def parse_reconstruction(path: str) -> Reconstruction:
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

    wf = parse_wavefront_25d_obj('%s/odm_texturing_25d/odm_textured_model_geo.obj' % path)
    reconstruction.mesh = wf

    return reconstruction
