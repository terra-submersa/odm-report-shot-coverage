from unittest import TestCase

import numpy as np

from models.point import Point
from models.shot import Shot


class TestShot(TestCase):

    def test_camera_relative_coordinates_straight_forward(self):
        shot = Shot()
        shot.translation = (10, 20, 30)
        shot.rotation = (0, 0, 0)

        point = Point()
        point.coordinates = (15, 20, 30)

        got = shot.camera_relative_coordinates(point.coordinates)
        self.assertEqual((5, 0, 0), got)

    def test_camera_relative_coordinates_straight_forward_middle(self):
        shot = Shot()
        shot.translation = (10, 20, 30)
        shot.rotation = (0, 0, 0)

        point = Point()
        point.coordinates = (10, 20, 25)

        got = shot.camera_relative_coordinates(point.coordinates)
        self.assertEqual((0, 0, -5), got)

    def test_camera_relative_coordinates_straight_forward_shifted(self):
        shot = Shot()
        shot.translation = (10, 20, 30)
        shot.rotation = (0, 0, 0)

        point = Point()
        point.coordinates = (8, 23, 27)

        got = shot.camera_relative_coordinates(point.coordinates)

        self.assertAlmostEqual(-2, got[0])
        self.assertAlmostEqual(3, got[1])
        self.assertAlmostEqual(-3, got[2])

    def test_camera_relative_coordinates_x_180_z_90_middle(self):
        shot = Shot()
        shot.translation = (10, 20, 30)
        shot.rotation = (np.pi / np.sqrt(2), np.pi / np.sqrt(2), 0)
        point = Point()
        point.coordinates = (10, 20, 25)

        got = shot.camera_relative_coordinates(point.coordinates)

        self.assertAlmostEqual(0, got[0])
        self.assertAlmostEqual(0, got[1])
        self.assertAlmostEqual(5, got[2])

    def test_camera_relative_coordinates_x_180_z_90_shifted(self):
        shot = Shot()
        shot.translation = (10, 20, 30)
        shot.rotation = (np.pi / np.sqrt(2), np.pi / np.sqrt(2), 0)
        point = Point()
        point.coordinates = (8, 23, 27)

        got = shot.camera_relative_coordinates(point.coordinates)

        self.assertAlmostEqual(3, got[0])
        self.assertAlmostEqual(-2, got[1])
        self.assertAlmostEqual(3, got[2])
