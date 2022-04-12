from unittest import TestCase

from odm_report_shot_coverage.models.reconstruction import parse_reconstruction


class Test(TestCase):

    def test_json_parse_reconstruction(self):
        got = parse_reconstruction('example/project')

        self.assertEqual(60, len(got.shots), 'shots')
        self.assertEqual(48509, len(got.mesh.points), 'points')
