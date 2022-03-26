from unittest import TestCase

from models.test_fixtures import TestFixtures


class TestShot(TestCase):
    def test_camera_relative_coordinates(self):
        shot = TestFixtures.a_shot()
        point = TestFixtures.a_point()

        got = shot.camera_relative_coordinates(point.coordinates)
        self.assertEqual((1.2646942673746822, 2.678944091796595, 2.036753006024462), got)
