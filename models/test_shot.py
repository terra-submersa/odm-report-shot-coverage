from unittest import TestCase

import numpy as np

from models.point import Point
from models.shot import Shot, shot_boundaries_from_points


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


class TestShotBoundaries(TestCase):
    def test_extend_one(self):
        points = [(5, 7)]

        sb = shot_boundaries_from_points(points, 4)

        self.assertEqual([(5, 7), (5, 7), (5, 7), (5, 7)], sb.path)

    def test_shot_boundaries_from_points_a(self):
        # 9 ...xX....
        # 8 ..xxx....
        # 7 .XxxxX...
        # 6 ..xxx..
        # 5 ..Xx...
        #   4567890

        points = [
            (6, 5),
            (7, 5),
            (6, 6),
            (7, 6),
            (8, 6),
            (5, 7),
            (6, 7),
            (7, 7),
            (8, 7),
            (9, 7),
            (6, 8),
            (7, 8),
            (8, 8),
            (7, 9),
            (8, 9),
        ]

        sb = shot_boundaries_from_points(points, 4)

        self.assertEqual([(7, 5), (8, 9), (7, 9), (6, 5)], sb.path)

    def test_shot_boundaries_from_points_b(self):
        # 9 .........
        # 8 .........
        # 7 ....XxX..
        # 6 ...xxx...
        # 5 ..XxX....
        #   456789012

        points = [
            (6, 5),
            (7, 5),
            (8, 5),
            (7, 6),
            (8, 6),
            (9, 6),
            (8, 7),
            (9, 7),
            (10, 7),
        ]
        sb = shot_boundaries_from_points(points, 4)

        self.assertEqual([(8, 5), (10, 7), (8, 7), (6, 5)], sb.path)

    def test_shot_boundaries_from_points_3087(self):

        points = [(0, -9, -10), (0, -6, -10), (0, -3, -10), (0, 0, -10), (3, -12, -10), (3, -9, -10), (3, -6, -10),
                  (3, -3, -10), (3, 0, -10), (3, 3, -10), (6, -12, -10), (6, -9, -10), (6, -6, -10), (6, -3, -10),
                  (6, 0, -10), (6, 3, -10), (6, 6, -10), (9, -12, -10), (9, -9, -10), (9, -6, -10), (9, -3, -10),
                  (9, 0, -10), (9, 3, -10), (9, 6, -10), (12, -12, -10), (12, -9, -10), (12, -6, -10), (12, -3, -10),
                  (12, 0, -10), (12, 3, -10), (12, 6, -10), (12, 9, -10), (15, 6, -10), (15, 9, -10), (15, 12, -10)]
        sb = shot_boundaries_from_points(points, 8)

        self.assertEqual([(12, -12), (12, -6), (12, 0), (15, 12), (6, 6), (0, 0), (0, -9), (3, -12)], sb.path)
