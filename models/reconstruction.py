from models.camera import Camera, json_parse_camera
from models.point import Point, json_parse_point
from models.shot import Shot, json_parse_shot
from scipy import stats


class Reconstruction:
    cameras: dict[str, Camera] = {}
    _shots: list[Shot] = []
    points: list[Point] = []

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

    def shot_xy_boundaries(self) -> dict[str, ((float, float), (float, float))]:
        ret = {}
        for shot in [s for s in self.shots if s.image_name in {'GOPR3101.jpeg', 'GOPR3102.jpeg', 'GOPR3103.jpeg', 'GOPR3104.jpeg', 'GOPR3105.jpeg', 'GOPR3106.jpeg' , 'GOPR3107.jpeg' }]:
            print('------------------- %s' % shot)
            pix_coords = []
            for point in self.points:
                pixel = shot.camera_pixel(point.coordinates)
                if shot.camera.in_frame(pixel):
                    pix_coords.append((pixel, point.coordinates))
            if len(pix_coords) >= 2:
                lin_reg_x = lin_reg([(pc[0][0], pc[1][0]) for pc in pix_coords])
                lin_reg_y = lin_reg([(pc[0][1], pc[1][1]) for pc in pix_coords])
                print('%s\t%d\n\t%s\n\t%s' % (shot.image_name, len(pix_coords), lin_reg_x, lin_reg_y))
                print('(%f, %f) - (%f, %f) / %f x %f' % (
                    lin_reg_x.intercept - lin_reg_x.slope / 2,
                    lin_reg_x.intercept + lin_reg_x.slope / 2,
                    lin_reg_y.intercept - lin_reg_y.slope / 2,
                    lin_reg_y.intercept + lin_reg_y.slope / 2,
                    lin_reg_x.slope,
                    lin_reg_y.slope
                ))


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
        reconstruction.add_camera(name, json_parse_camera(ela))

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
