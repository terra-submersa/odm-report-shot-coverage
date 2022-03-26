import json
from unittest import TestCase

from models.camera import json_parse_camera


class Test(TestCase):
    def test_json_load_camera(self):
        json_str="""
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

        got = json_parse_camera(given)
        self.assertEqual(3000, got.width)
        self.assertEqual(4000, got.height)
        self.assertEqual(0.5207834102328533, got.focal)
        self.assertEqual(-0.10638507280457302, got.k1)
        self.assertEqual(0.06769290794144624, got.k2)
