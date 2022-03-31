from models.camera import Camera
from models.point import Point
from models.shot import Shot


class TestFixtures:
    @staticmethod
    def a_camera_gopro8_linear() -> Camera:
        camera = Camera()
        camera.width = 3000
        camera.height = 4000
        camera.focal = 0.5207834102328533
        camera.k1 = -0.10638507280457302
        camera.k2 = 0.06769290794144624
        return camera

    @staticmethod
    def a_point() -> Point:
        point = Point()
        point.id = 'A'
        point.coordinates = (0.43375263823147325, 2.4853185781312033, -3.0598703709130475)
        return point

    @staticmethod
    def a_shot() -> Shot:
        shot = Shot()
        shot.image_name = 'a.jpeg'
        shot.camera = TestFixtures.a_camera_gopro8_linear()
        shot.rotation = (2.0577299307555323, -2.20218132761156, -0.04484071736689525)
        shot.translation = (0.033173629227221335, 0.5114751173118289, -0.07091459305900544)
        return shot
