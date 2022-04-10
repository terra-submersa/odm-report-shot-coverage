import json
from unittest import TestCase

import numpy as np

from models.camera import json_parse_camera
from models.test_fixtures import TestFixtures as Fixtures


class Test(TestCase):
    def test_json_load_camera(self):
        json_str = """
        {
                "projection_type": "brown",
                "width": 3000,
                "height": 4000,
                "focal_x": 0.5207834102328533,
                "focal_y": 0.5207834102328533,
                "c_x": -0.010331518981731644,
                "c_y": -0.0036169971231284,
                "k1": -0.10638507280457302,
                "k2": 0.06769290794144624,
                "p1": -0.0009394968204580917,
                "p2": -0.0007005575451251272,
                "k3": -0.005369531191619131
            }
            """
        given = json.loads(json_str)

        got = json_parse_camera('gopro8', given)
        self.assertEqual('gopro8', got.name, 'name')
        self.assertEqual('brown', got.projection_type, 'project_type')
        self.assertEqual(3000, got.width, 'width')
        self.assertEqual(4000, got.height, 'height')
        self.assertEqual(0.5207834102328533, got.focal, 'focal')
        self.assertEqual(-0.10638507280457302, got.k1, 'k1')
        self.assertEqual(0.06769290794144624, got.k2, 'k2')
        self.assertEqual(-0.005369531191619131, got.k3, 'k3')
        self.assertEqual(-0.0009394968204580917, got.p1, 'p1')
        self.assertEqual(-0.0007005575451251272, got.p2, 'p2')

    # GoPro in linear mode has a horizontal FOV of 86.7º
    # I've adapted it to 89.9 (water diffraction ??), based on trial an error to fit the camera.json specs
    horiz_fov = 89.9 / 2 / 180 * np.pi
    tan_camera = np.tan(horiz_fov)
    given_z = 10

    def test_perspective_center(self):
        got = Fixtures.a_camera_gopro8_linear().perspective_pixel((0, 0, self.given_z))
        self.assertEqual(0, got[0])
        self.assertEqual(0, got[1])

    def test_perspective_max_right(self):
        given_x = self.given_z * self.tan_camera
        got = Fixtures.a_camera_gopro8_linear().perspective_pixel((given_x, 0, self.given_z))
        self.assertAlmostEqual(0.5, got[0], 3)
        self.assertAlmostEqual(0, got[1], 3)

    def test_perspective_max_right_factor_2(self):
        given_x = self.given_z * self.tan_camera
        got = Fixtures.a_camera_gopro8_linear().perspective_pixel((given_x * 2, 0, self.given_z * 2))
        self.assertAlmostEqual(0.5, got[0], 3)
        self.assertAlmostEqual(0, got[1], 3)

    def test_perspective_max_top(self):
        given_x = self.given_z * self.tan_camera
        got = Fixtures.a_camera_gopro8_linear().perspective_pixel((0, given_x, self.given_z))
        self.assertAlmostEqual(0, got[0], 3)
        self.assertAlmostEqual(0.5, got[1], 3)
